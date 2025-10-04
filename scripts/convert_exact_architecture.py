"""
DIANA - Conversion Architecture Exacte
Reconstruit l'architecture exacte basée sur la structure du state_dict
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class SEBlock(nn.Module):
    """Squeeze-and-Excitation Block"""
    
    def __init__(self, channels, reduction=16):
        super(SEBlock, self).__init__()
        self.avg_pool = nn.AdaptiveAvgPool2d(1)
        self.fc = nn.Sequential(
            nn.Linear(channels, channels // reduction, bias=False),
            nn.ReLU(inplace=True),
            nn.Linear(channels // reduction, channels, bias=False),
            nn.Sigmoid()
        )
    
    def forward(self, x):
        b, c, _, _ = x.size()
        y = self.avg_pool(x).view(b, c)
        y = self.fc(y).view(b, c, 1, 1)
        return x * y


class BasicBlock(nn.Module):
    """Basic ResNet Block avec SE"""
    
    def __init__(self, in_channels, out_channels, stride=1, se_ratio=16):
        super(BasicBlock, self).__init__()
        
        self.conv1 = nn.Conv2d(in_channels, out_channels, 3, stride, 1, bias=False)
        self.bn1 = nn.BatchNorm2d(out_channels)
        self.conv2 = nn.Conv2d(out_channels, out_channels, 3, 1, 1, bias=False)
        self.bn2 = nn.BatchNorm2d(out_channels)
        
        # SE Block
        self.se = SEBlock(out_channels, se_ratio)
        
        # Shortcut
        self.shortcut = nn.Sequential()
        if stride != 1 or in_channels != out_channels:
            self.shortcut = nn.Sequential(
                nn.Conv2d(in_channels, out_channels, 1, stride, bias=False),
                nn.BatchNorm2d(out_channels)
            )
    
    def forward(self, x):
        residual = x
        
        out = F.relu(self.bn1(self.conv1(x)))
        out = self.bn2(self.conv2(out))
        out = self.se(out)
        
        out += self.shortcut(residual)
        out = F.relu(out)
        
        return out


class BreastCancerFilterExact(nn.Module):
    """Architecture exacte basée sur la structure du state_dict"""
    
    def __init__(self, num_classes=3):
        super(BreastCancerFilterExact, self).__init__()
        
        # Couche initiale (features.0)
        self.features = nn.Sequential(
            # features.0.0 - Conv2d
            nn.Conv2d(3, 64, 7, 2, 3, bias=False),
            # features.0.1 - BatchNorm2d
            nn.BatchNorm2d(64),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(3, 2, 1)
        )
        
        # Couches ResNet avec blocs imbriqués
        # features.1 - Layer 1
        self.features_1 = self._make_layer(64, 64, 2, stride=1)
        # features.2 - Layer 2  
        self.features_2 = self._make_layer(64, 128, 2, stride=2)
        # features.3 - Layer 3
        self.features_3 = self._make_layer(128, 256, 2, stride=2)
        # features.4 - Layer 4
        self.features_4 = self._make_layer(256, 512, 2, stride=2)
        # features.5 - Layer 5
        self.features_5 = self._make_layer(512, 1024, 2, stride=2)
        # features.6 - Layer 6
        self.features_6 = self._make_layer(1024, 2048, 2, stride=2)
        # features.7 - Layer 7
        self.features_7 = self._make_layer(2048, 2048, 2, stride=2)
        
        # Global Average Pooling
        self.avgpool = nn.AdaptiveAvgPool2d((1, 1))
        
        # Classificateur
        self.classifier = nn.Sequential(
            nn.Dropout(0.5),
            nn.Linear(2048, 1280),
            nn.ReLU(inplace=True),
            nn.Dropout(0.5),
            nn.Linear(1280, num_classes)
        )
    
    def _make_layer(self, in_channels, out_channels, blocks, stride):
        layers = []
        layers.append(BasicBlock(in_channels, out_channels, stride))
        for _ in range(1, blocks):
            layers.append(BasicBlock(out_channels, out_channels))
        return nn.Sequential(*layers)
    
    def forward(self, x):
        x = self.features(x)
        x = self.features_1(x)
        x = self.features_2(x)
        x = self.features_3(x)
        x = self.features_4(x)
        x = self.features_5(x)
        x = self.features_6(x)
        x = self.features_7(x)
        
        x = self.avgpool(x)
        x = x.view(x.size(0), -1)
        x = self.classifier(x)
        
        return x


def convert_exact_architecture():
    """Convertit le modèle avec l'architecture exacte"""
    
    # Chemins
    pytorch_path = Path("models/filter/best_model.pth")
    onnx_path = Path("models/filter/breast_cancer_filter.onnx")
    
    print("=" * 60)
    print("DIANA - Conversion Architecture Exacte")
    print("=" * 60)
    
    # Vérifier que le fichier PyTorch existe
    if not pytorch_path.exists():
        print(f"ERREUR: Fichier PyTorch introuvable: {pytorch_path}")
        return False
    
    try:
        # Charger le state_dict
        print("Chargement du state_dict...")
        checkpoint = torch.load(pytorch_path, map_location='cpu')
        
        print("Clés disponibles:", list(checkpoint.keys()))
        
        # Extraire le state_dict
        if 'model_state_dict' in checkpoint:
            state_dict = checkpoint['model_state_dict']
        elif 'state_dict' in checkpoint:
            state_dict = checkpoint['state_dict']
        else:
            print("ERREUR: Aucun state_dict trouvé")
            return False
        
        print(f"State_dict chargé: {len(state_dict)} paramètres")
        
        # Créer l'architecture exacte
        print("Création de l'architecture exacte...")
        model = BreastCancerFilterExact(num_classes=3)
        
        # Charger les poids
        print("Chargement des poids...")
        model.load_state_dict(state_dict)
        model.eval()
        
        # Créer un exemple d'entrée
        dummy_input = torch.randn(1, 3, 224, 224)
        
        print("Conversion vers ONNX...")
        print(f"Entrée: {dummy_input.shape}")
        
        # Exporter vers ONNX
        torch.onnx.export(
            model,
            dummy_input,
            str(onnx_path),
            export_params=True,
            opset_version=11,
            do_constant_folding=True,
            input_names=['input'],
            output_names=['output'],
            dynamic_axes={
                'input': {0: 'batch_size'},
                'output': {0: 'batch_size'}
            }
        )
        
        print(f"Conversion réussie: {onnx_path}")
        print(f"Taille ONNX: {onnx_path.stat().st_size / (1024*1024):.1f} MB")
        
        return True
        
    except Exception as e:
        print(f"ERREUR lors de la conversion: {e}")
        print("\nSolutions possibles:")
        print("1. Vérifiez que l'architecture correspond à votre modèle")
        print("2. Modifiez la classe selon votre architecture exacte")
        print("3. Vérifiez que le nombre de classes est correct (3)")
        return False


def test_onnx_model():
    """Teste le modèle ONNX converti"""
    try:
        import onnxruntime as ort
        
        onnx_path = Path("models/filter/breast_cancer_filter.onnx")
        if not onnx_path.exists():
            print("Modèle ONNX non trouvé")
            return False
        
        print("\nTest du modèle ONNX...")
        
        # Charger le modèle ONNX
        session = ort.InferenceSession(str(onnx_path))
        
        # Tester avec une entrée factice
        import numpy as np
        dummy_input = np.random.randn(1, 3, 224, 224).astype(np.float32)
        
        # Exécuter l'inférence
        outputs = session.run(None, {'input': dummy_input})
        
        print(f"Modele ONNX fonctionne")
        print(f"Sortie: {outputs[0].shape}")
        print(f"Classes: {outputs[0][0]}")
        
        return True
        
    except Exception as e:
        print(f"ERREUR lors du test ONNX: {e}")
        return False


if __name__ == "__main__":
    # Configuration du logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Conversion
    success = convert_exact_architecture()
    
    if success:
        # Test du modèle converti
        test_onnx_model()
        
        print("\n" + "=" * 60)
        print("CONVERSION TERMINEE")
        print("=" * 60)
        print("Votre modèle ONNX est prêt dans: models/filter/breast_cancer_filter.onnx")
        print("Le système de filtrage sera automatiquement activé au prochain démarrage")
    else:
        print("\n" + "=" * 60)
        print("CONVERSION ECHOUEE")
        print("=" * 60)
        print("Vous devez adapter l'architecture dans le script")
