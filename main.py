"""
DIANA - Diagnostic Intelligent Automatisé pour les Nouvelles Analyses
Point d'entrée principal de l'application
"""

import sys
import logging
from pathlib import Path

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt

import config
from src.ui.modern_main_window import ModernMainWindow


def setup_logging():
    """Configure le système de logging"""
    # Créer le format de log
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    date_format = '%Y-%m-%d %H:%M:%S'
    
    # Configuration du logger
    logging.basicConfig(
        level=getattr(logging, config.LOG_LEVEL),
        format=log_format,
        datefmt=date_format,
        handlers=[
            logging.FileHandler(config.LOG_FILE, encoding='utf-8'),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    logger = logging.getLogger(__name__)
    logger.info(f"=== Démarrage de {config.APP_NAME} v{config.APP_VERSION} ===")
    
    return logger


def check_prerequisites():
    """Vérifie que tous les prérequis sont présents"""
    logger = logging.getLogger(__name__)
    
    # Vérifier que les dossiers nécessaires existent
    required_dirs = [config.DATA_DIR, config.LOGS_DIR]
    for directory in required_dirs:
        if not directory.exists():
            directory.mkdir(parents=True, exist_ok=True)
            logger.info(f"Dossier créé: {directory}")
    
    # Vérifier que le modèle chiffré existe
    if not config.MODEL_ENCRYPTED_PATH.exists():
        logger.warning("=" * 60)
        logger.warning("ATTENTION : Modele ONNX introuvable")
        logger.warning("=" * 60)
        logger.warning(f"Emplacement attendu : {config.MODEL_ENCRYPTED_PATH}")
        logger.warning("")
        logger.warning("Pour utiliser l'application :")
        logger.warning("1. Placez votre modèle ONNX dans : models/breast_cancer_model.onnx")
        logger.warning("2. Chiffrez-le avec : python scripts/encrypt_model.py")
        logger.warning("")
        logger.warning("L'application va démarrer, mais vous devrez ajouter le modèle pour analyser des images.")
        logger.warning("=" * 60)
    else:
        logger.info(f"Modele chiffre detecte: {config.MODEL_ENCRYPTED_PATH}")
    
    return True


def main():
    """Fonction principale"""
    # Configuration du logging
    logger = setup_logging()
    
    try:
        # Vérifier les prérequis
        if not check_prerequisites():
            logger.error("Prérequis non satisfaits")
            sys.exit(1)
        
        # Créer l'application Qt
        app = QApplication(sys.argv)
        
        # Configuration de l'application
        app.setApplicationName(config.APP_NAME)
        app.setApplicationVersion(config.APP_VERSION)
        app.setOrganizationName("DIANA Team")
        
        # Activer le support des DPI élevés
        if hasattr(Qt, 'AA_EnableHighDpiScaling'):
            QApplication.setAttribute(Qt.ApplicationAttribute.AA_EnableHighDpiScaling, True)
        if hasattr(Qt, 'AA_UseHighDpiPixmaps'):
            QApplication.setAttribute(Qt.ApplicationAttribute.AA_UseHighDpiPixmaps, True)
        
        # Créer et afficher la fenêtre principale
        window = ModernMainWindow()
        window.show()
        
        logger.info("Application démarrée avec succès")
        
        # Lancer la boucle d'événements
        exit_code = app.exec()
        
        logger.info(f"Application terminée avec le code {exit_code}")
        sys.exit(exit_code)
        
    except Exception as e:
        logger.critical(f"Erreur fatale: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()

