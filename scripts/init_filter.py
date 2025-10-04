"""
DIANA - Initialisation du filtre d'images
Charge le modèle de filtrage au démarrage de l'application
"""

import logging
from pathlib import Path
import sys

# Ajouter le répertoire parent au path pour les imports
sys.path.append(str(Path(__file__).parent.parent))

from src.image_filter import get_image_filter

logger = logging.getLogger(__name__)


def init_image_filter():
    """Initialise le filtre d'images au démarrage"""
    try:
        logger.info("Initialisation du filtre d'images...")
        
        filter_engine = get_image_filter()
        success = filter_engine.load_model()
        
        if success:
            logger.info("✅ Filtre d'images initialisé avec succès")
            filter_info = filter_engine.get_model_info()
            logger.info(f"Modèle: {filter_info['input_name']}, Shape: {filter_info['input_shape']}")
        else:
            logger.warning("⚠️ Filtre d'images non disponible - toutes les images seront acceptées")
            logger.warning(f"Placez votre modèle dans: {filter_engine.model_path}")
        
        return success
        
    except Exception as e:
        logger.error(f"Erreur lors de l'initialisation du filtre: {e}")
        return False


if __name__ == "__main__":
    # Configuration du logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    print("=" * 60)
    print("🔍 DIANA - Initialisation du Filtre d'Images")
    print("=" * 60)
    
    success = init_image_filter()
    
    if success:
        print("✅ Filtre initialisé avec succès")
    else:
        print("⚠️ Filtre non disponible")
    
    print("=" * 60)
