"""
DIANA - Création d'un modèle de filtrage factice
Crée un modèle ONNX simple pour tester le système de filtrage
"""

import numpy as np
import onnx
from onnx import helper, TensorProto
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


def create_dummy_filter_model():
    """Crée un modèle ONNX factice pour le filtrage d'images"""
    
    # Définir les dimensions
    batch_size = 1
    channels = 3
    height = 224
    width = 224
    num_classes = 3
    
    # Créer un modèle ultra-simple avec juste un reshape et une couche dense
    graph = helper.make_graph(
        nodes=[
            # Reshape pour aplatir
            helper.make_node(
                'Reshape',
                inputs=['input', 'shape'],
                outputs=['flatten'],
                name='reshape'
            ),
            # Couche dense finale
            helper.make_node(
                'Gemm',
                inputs=['flatten', 'weight', 'bias'],
                outputs=['output'],
                name='dense',
                alpha=1.0,
                beta=1.0,
                transA=0,
                transB=1
            )
        ],
        name='breast_cancer_filter',
        inputs=[
            helper.make_tensor_value_info(
                'input',
                TensorProto.FLOAT,
                [batch_size, channels, height, width]
            )
        ],
        outputs=[
            helper.make_tensor_value_info(
                'output',
                TensorProto.FLOAT,
                [batch_size, num_classes]
            )
        ],
        initializer=[
            # Shape pour reshape
            helper.make_tensor(
                'shape',
                TensorProto.INT64,
                [2],
                np.array([batch_size, channels * height * width], dtype=np.int64)
            ),
            # Poids de la couche dense (simulation)
            helper.make_tensor(
                'weight',
                TensorProto.FLOAT,
                [channels * height * width, num_classes],
                np.random.randn(channels * height * width, num_classes).astype(np.float32).flatten()
            ),
            # Biais de la couche dense
            helper.make_tensor(
                'bias',
                TensorProto.FLOAT,
                [num_classes],
                np.array([0.1, 0.2, 0.7], dtype=np.float32)  # Biais vers "breast_cancer"
            )
        ]
    )
    
    # Créer le modèle
    model = helper.make_model(graph)
    model.opset_import[0].version = 9  # Version compatible
    model.ir_version = 6  # Version IR compatible
    
    return model


def main():
    """Fonction principale"""
    print("=" * 60)
    print("DIANA - Creation d'un Modele de Filtrage Factice")
    print("=" * 60)
    
    try:
        # Créer le modèle
        print("Creation du modele ONNX...")
        model = create_dummy_filter_model()
        
        # Créer le dossier de destination
        output_dir = Path("models/filter")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Sauvegarder le modèle
        output_path = output_dir / "breast_cancer_filter.onnx"
        onnx.save(model, str(output_path))
        
        print(f"Modele cree: {output_path}")
        print()
        print("Informations du modele:")
        print(f"   - Entree: [1, 3, 224, 224] (batch, channels, height, width)")
        print(f"   - Sortie: [1, 3] (batch, classes)")
        print(f"   - Classes: [non_medical, medical_other, breast_cancer]")
        print()
        print("ATTENTION: Ce modele est factice et ne fait pas de vraie classification!")
        print("   Remplacez-le par votre vrai modele entraine.")
        print()
        print("Pour tester le systeme:")
        print("   python scripts/test_filter.py")
        
    except Exception as e:
        logger.error(f"Erreur lors de la creation du modele: {e}")
        print(f"ERREUR: {e}")


if __name__ == "__main__":
    # Configuration du logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    main()
