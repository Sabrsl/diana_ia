"""
DIANA - Conversion PyTorch vers ONNX
Convertit un modèle PyTorch (.pth) en format ONNX pour le filtrage
"""

import torch
import torch.onnx
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


def convert_pytorch_to_onnx():
    """Convertit le modèle PyTorch en ONNX"""
    
    # Chemins
    pytorch_path = Path("models/filter/best_model.pth")
    onnx_path = Path("models/filter/breast_cancer_filter.onnx")
    
    print("=" * 60)
    print("DIANA - Conversion PyTorch vers ONNX")
    print("=" * 60)
    
    # Vérifier que le fichier PyTorch existe
    if not pytorch_path.exists():
        print(f"ERREUR: Fichier PyTorch introuvable: {pytorch_path}")
        return False
    
    print(f"Fichier PyTorch trouvé: {pytorch_path}")
    print(f"Taille: {pytorch_path.stat().st_size / (1024*1024):.1f} MB")
    
    try:
        # Charger le modèle PyTorch
        print("Chargement du modèle PyTorch...")
        model = torch.load(pytorch_path, map_location='cpu')
        
        # Vérifier le type de modèle
        if isinstance(model, dict):
            print("Fichier contient un dictionnaire")
            print("Clés disponibles:", list(model.keys()))
            
            if 'model' in model:
                model = model['model']
                print("Modèle extrait de la clé 'model'")
            elif 'state_dict' in model:
                print("ATTENTION: Fichier contient un state_dict")
                print("Vous devez fournir l'architecture du modèle")
                print("Ou sauvegarder le modèle complet avec torch.save(model, 'fichier.pth')")
                return False
            else:
                print("Structure inconnue du fichier PyTorch")
                print("Essayons de traiter comme un modèle complet...")
                # Essayer de trouver le modèle dans les valeurs
                for key, value in model.items():
                    if hasattr(value, 'eval'):
                        model = value
                        print(f"Modèle trouvé dans la clé '{key}'")
                        break
                else:
                    print("Aucun modèle trouvé dans le dictionnaire")
                    return False
        
        # Mettre le modèle en mode évaluation
        model.eval()
        
        # Créer un exemple d'entrée (224x224 RGB)
        dummy_input = torch.randn(1, 3, 224, 224)
        
        print("Conversion vers ONNX...")
        print(f"Entrée: {dummy_input.shape}")
        
        # Exporter vers ONNX
        torch.onnx.export(
            model,                          # Modèle
            dummy_input,                    # Exemple d'entrée
            str(onnx_path),                 # Chemin de sortie
            export_params=True,            # Sauvegarder les paramètres
            opset_version=11,               # Version ONNX
            do_constant_folding=True,      # Optimisation
            input_names=['input'],          # Nom de l'entrée
            output_names=['output'],       # Nom de la sortie
            dynamic_axes={                 # Axes dynamiques
                'input': {0: 'batch_size'},
                'output': {0: 'batch_size'}
            }
        )
        
        print(f"✅ Conversion réussie: {onnx_path}")
        print(f"Taille ONNX: {onnx_path.stat().st_size / (1024*1024):.1f} MB")
        
        return True
        
    except Exception as e:
        print(f"ERREUR lors de la conversion: {e}")
        print("\nSolutions possibles:")
        print("1. Vérifiez que le fichier .pth contient un modèle complet")
        print("2. Si c'est un state_dict, vous devez reconstruire l'architecture")
        print("3. Assurez-vous que le modèle accepte des entrées [1, 3, 224, 224]")
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
    success = convert_pytorch_to_onnx()
    
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
        print("Vérifiez votre fichier PyTorch et réessayez")
