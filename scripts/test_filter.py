"""
DIANA - Test du système de filtrage
Script de test pour vérifier le fonctionnement du filtre d'images
"""

import logging
import sys
from pathlib import Path
import tempfile
from PIL import Image, ImageDraw

# Ajouter le répertoire parent au path pour les imports
sys.path.append(str(Path(__file__).parent.parent))

from src.image_filter import get_image_filter

logger = logging.getLogger(__name__)


def create_test_images():
    """Crée des images de test pour différents scénarios"""
    test_images = {}
    
    # Image non-médicale (photo normale)
    img_normal = Image.new('RGB', (224, 224), color='lightblue')
    draw = ImageDraw.Draw(img_normal)
    draw.rectangle([50, 50, 150, 150], fill='red', outline='black')
    draw.text((80, 100), "TEST", fill='white')
    test_images['non_medical'] = img_normal
    
    # Image médicale simulée (rayons X génériques)
    img_medical = Image.new('RGB', (224, 224), color='black')
    draw = ImageDraw.Draw(img_medical)
    # Simuler une structure osseuse
    for i in range(0, 224, 20):
        draw.line([(i, 0), (i, 224)], fill='white', width=2)
    draw.text((100, 100), "X-RAY", fill='white')
    test_images['medical_other'] = img_medical
    
    # Image de mammographie simulée
    img_mammo = Image.new('RGB', (224, 224), color='darkgray')
    draw = ImageDraw.Draw(img_mammo)
    # Simuler une structure de tissu mammaire
    for i in range(0, 224, 10):
        for j in range(0, 224, 10):
            if (i + j) % 20 == 0:
                draw.ellipse([i, j, i+8, j+8], fill='white')
    draw.text((80, 100), "MAMMO", fill='white')
    test_images['breast_cancer'] = img_mammo
    
    return test_images


def test_filter():
    """Test complet du système de filtrage"""
    print("=" * 60)
    print("DIANA - Test du Systeme de Filtrage")
    print("=" * 60)
    
    # Initialiser le filtre
    filter_engine = get_image_filter()
    filter_engine.load_model()  # Forcer le chargement
    filter_info = filter_engine.get_model_info()
    
    print(f"Modele: {filter_info['model_path']}")
    print(f"Existe: {filter_info['model_exists']}")
    print(f"Charge: {filter_info['loaded']}")
    print()
    
    if not filter_info['loaded']:
        print("ATTENTION: Modele de filtrage non disponible")
        print("   Placez votre modele dans: models/filter/breast_cancer_filter.onnx")
        print("   Le systeme acceptera toutes les images par defaut")
        return
    
    # Créer les images de test
    print("Creation des images de test...")
    test_images = create_test_images()
    
    # Tester chaque type d'image
    results = {}
    
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        for category, image in test_images.items():
            # Sauvegarder l'image temporaire
            image_path = temp_path / f"test_{category}.png"
            image.save(image_path)
            
            print(f"\nTest: {category}")
            print(f"   Image: {image_path}")
            
            # Filtrer l'image
            result = filter_engine.filter_image(image_path)
            
            print(f"   Resultat: {'ACCEPTE' if result['accepted'] else 'REJETE'}")
            print(f"   Categorie: {result['category_name']}")
            print(f"   Confiance: {result['confidence']:.2f}%")
            print(f"   Raison: {result['reason']}")
            
            results[category] = result
    
    # Résumé des tests
    print("\n" + "=" * 60)
    print("RESUME DES TESTS")
    print("=" * 60)
    
    for category, result in results.items():
        status = "PASS" if result['accepted'] == (category == 'breast_cancer') else "FAIL"
        print(f"{status} {category}: {result['category_name']} ({result['confidence']:.1f}%)")
    
    print("\nResultats attendus:")
    print("   - non_medical: REJETE")
    print("   - medical_other: REJETE") 
    print("   - breast_cancer: ACCEPTE")


if __name__ == "__main__":
    # Configuration du logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    test_filter()
