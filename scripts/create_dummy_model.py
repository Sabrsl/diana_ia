"""
DIANA - Création d'un modèle ONNX dummy pour tests
Ce script crée un modèle simple pour tester l'application sans modèle réel
"""

import sys
from pathlib import Path

try:
    import torch
    import torch.nn as nn
except ImportError:
    print("❌ PyTorch n'est pas installé")
    print("💡 Installez-le avec: pip install torch")
    sys.exit(1)


class DummyBreastCancerModel(nn.Module):
    """
    Modèle dummy pour tests
    Ne doit PAS être utilisé en production !
    """
    
    def __init__(self):
        super().__init__()
        
        # Feature extractor simple
        self.features = nn.Sequential(
            nn.Conv2d(3, 64, kernel_size=7, stride=2, padding=3),
            nn.BatchNorm2d(64),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(kernel_size=3, stride=2, padding=1),
            
            nn.Conv2d(64, 128, kernel_size=3, padding=1),
            nn.BatchNorm2d(128),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(kernel_size=2, stride=2),
            
            nn.Conv2d(128, 256, kernel_size=3, padding=1),
            nn.BatchNorm2d(256),
            nn.ReLU(inplace=True),
            nn.AdaptiveAvgPool2d((1, 1))
        )
        
        # Classifier
        self.classifier = nn.Sequential(
            nn.Flatten(),
            nn.Dropout(0.5),
            nn.Linear(256, 128),
            nn.ReLU(inplace=True),
            nn.Dropout(0.3),
            nn.Linear(128, 2)  # 2 classes : bénin, malin
        )
        
        # Initialiser les poids de manière réaliste
        self._initialize_weights()
    
    def _initialize_weights(self):
        """Initialise les poids du modèle"""
        for m in self.modules():
            if isinstance(m, nn.Conv2d):
                nn.init.kaiming_normal_(m.weight, mode='fan_out', nonlinearity='relu')
                if m.bias is not None:
                    nn.init.constant_(m.bias, 0)
            elif isinstance(m, nn.BatchNorm2d):
                nn.init.constant_(m.weight, 1)
                nn.init.constant_(m.bias, 0)
            elif isinstance(m, nn.Linear):
                nn.init.normal_(m.weight, 0, 0.01)
                nn.init.constant_(m.bias, 0)
    
    def forward(self, x):
        """Forward pass"""
        x = self.features(x)
        x = self.classifier(x)
        return x


def create_dummy_model(output_path: str = "models/breast_cancer_model.onnx"):
    """
    Crée et exporte un modèle ONNX dummy
    
    Args:
        output_path: Chemin de sortie du modèle ONNX
    """
    print("=" * 60)
    print("DIANA - Création d'un modèle dummy pour tests")
    print("=" * 60)
    print("\n⚠️  ATTENTION: Ce modèle est UNIQUEMENT pour les tests !")
    print("Ne l'utilisez PAS en production médicale !\n")
    
    # Créer le modèle
    print("📦 Création du modèle...")
    model = DummyBreastCancerModel()
    model.eval()
    
    # Créer un input dummy
    dummy_input = torch.randn(1, 3, 224, 224)
    
    # Tester le modèle
    print("🧪 Test du modèle...")
    with torch.no_grad():
        output = model(dummy_input)
        print(f"   Input shape: {dummy_input.shape}")
        print(f"   Output shape: {output.shape}")
        
        # Appliquer softmax pour avoir des probabilités
        probs = torch.softmax(output, dim=1)
        print(f"   Probabilities: {probs[0].tolist()}")
    
    # S'assurer que le dossier existe
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Exporter en ONNX
    print(f"\n💾 Export ONNX vers {output_path}...")
    
    torch.onnx.export(
        model,
        dummy_input,
        output_path,
        export_params=True,
        opset_version=14,
        do_constant_folding=True,
        input_names=['input'],
        output_names=['output'],
        dynamic_axes={
            'input': {0: 'batch_size'},
            'output': {0: 'batch_size'}
        }
    )
    
    # Vérifier le fichier
    if output_path.exists():
        size_mb = output_path.stat().st_size / (1024 * 1024)
        print(f"✅ Modèle créé avec succès !")
        print(f"📊 Taille: {size_mb:.2f} MB")
        print(f"📁 Emplacement: {output_path}")
        
        # Tester avec ONNX Runtime
        try:
            import onnxruntime as ort
            import numpy as np
            
            print("\n🔍 Vérification avec ONNX Runtime...")
            session = ort.InferenceSession(str(output_path))
            
            # Test
            input_data = np.random.randn(1, 3, 224, 224).astype(np.float32)
            outputs = session.run(None, {'input': input_data})
            
            # Appliquer softmax
            logits = outputs[0]
            exp_logits = np.exp(logits - np.max(logits, axis=1, keepdims=True))
            probs = exp_logits / np.sum(exp_logits, axis=1, keepdims=True)
            
            print(f"   Input shape: {input_data.shape}")
            print(f"   Output shape: {outputs[0].shape}")
            print(f"   Probabilities: {probs[0]}")
            print("✅ Modèle ONNX valide !")
            
        except ImportError:
            print("⚠️  ONNX Runtime non installé, vérification ignorée")
        except Exception as e:
            print(f"⚠️  Erreur lors de la vérification: {e}")
        
        # Prochaines étapes
        print("\n" + "=" * 60)
        print("📋 Prochaines étapes:")
        print("=" * 60)
        print("1. Chiffrez le modèle:")
        print("   python scripts/encrypt_model.py")
        print("\n2. Lancez l'application:")
        print("   python main.py")
        print("\n3. Pour utiliser un vrai modèle:")
        print("   - Remplacez ce fichier par votre modèle entraîné")
        print("   - Re-chiffrez avec encrypt_model.py")
        print("=" * 60)
        
        return True
    else:
        print("❌ Erreur: Le fichier n'a pas été créé")
        return False


def main():
    """Fonction principale"""
    
    # Chemin de sortie
    output_path = input("\nChemin de sortie (défaut: models/breast_cancer_model.onnx): ").strip()
    if not output_path:
        output_path = "models/breast_cancer_model.onnx"
    
    # Vérifier si le fichier existe déjà
    if Path(output_path).exists():
        confirm = input(f"\n⚠️  {output_path} existe déjà. Écraser ? (o/n): ").strip().lower()
        if confirm != 'o':
            print("❌ Opération annulée")
            return
    
    # Créer le modèle
    success = create_dummy_model(output_path)
    
    if not success:
        sys.exit(1)


if __name__ == "__main__":
    main()

