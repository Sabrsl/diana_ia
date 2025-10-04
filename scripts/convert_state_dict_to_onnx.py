"""
DIANA - Conversion State Dict vers ONNX
Reconstruit l'architecture du modèle à partir du state_dict
"""

import torch
import torch.nn as nn
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class BreastCancerFilter(nn.Module):
    """Architecture du modèle de filtrage - À ADAPTER selon votre modèle"""
    
    def __init__(self, num_classes=3):
        super(BreastCancerFilter, self).__init__()
        
        # Architecture de base - À MODIFIER selon votre modèle
        self.features = nn.Sequential(
            # Couche 1
            nn.Conv2d(3, 64, kernel_size=3, padding=1),
            nn.BatchNorm2d(64),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(2, 2),
            
            # Couche 2
            nn.Conv2d(64, 128, kernel_size=3, padding=1),
            nn.BatchNorm2d(128),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(2, 2),
            
            # Couche 3
            nn.Conv2d(128, 256, kernel_size=3, padding=1),
            nn.BatchNorm2d(256),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(2, 2),
            
            # Couche 4
            nn.Conv2d(256, 512, kernel_size=3, padding=1),
            nn.BatchNorm2d(512),
            nn.ReLU(inplace=True),
            nn.AdaptiveAvgPool2d((1, 1))
        )
        
        # Classificateur
        self.classifier = nn.Sequential(
            nn.Dropout(0.5),
            nn.Linear(512, 256),
            nn.ReLU(inplace=True),
            nn.Dropout(0.5),
            nn.Linear(256, num_classes)
        )
    
    def forward(self, x):
        x = self.features(x)
        x = x.view(x.size(0), -1)
        x = self.classifier(x)
        return x


def convert_state_dict_to_onnx():
    """Convertit un state_dict en modèle ONNX"""
    
    # Chemins
    pytorch_path = Path("models/filter/best_model.pth")
    onnx_path = Path("models/filter/breast_cancer_filter.onnx")
    
    print("=" * 60)
    print("DIANA - Conversion State Dict vers ONNX")
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
        
        # Créer l'architecture du modèle
        print("Création de l'architecture...")
        model = BreastCancerFilter(num_classes=3)
        
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
        print("2. Modifiez la classe BreastCancerFilter selon votre architecture")
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
    success = convert_state_dict_to_onnx()
    
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
