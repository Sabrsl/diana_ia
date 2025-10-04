"""
DIANA - Configuration centralisée
Gestion des paramètres de l'application
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

# Déterminer le répertoire de base (gère PyInstaller)
def get_base_dir():
    """Retourne le répertoire de base, compatible avec PyInstaller"""
    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        # Application packagée avec PyInstaller
        return Path(sys._MEIPASS)
    else:
        # Mode développement
        return Path(__file__).parent

# Chemins de base
BASE_DIR = get_base_dir()
DATA_DIR = Path.home() / "AppData" / "Local" / "DIANA" / "data"  # Données utilisateur
MODELS_DIR = BASE_DIR / "models"  # Modèle dans l'exécutable
LOGS_DIR = Path.home() / "AppData" / "Local" / "DIANA" / "logs"  # Logs utilisateur

# Créer les dossiers nécessaires
DATA_DIR.mkdir(parents=True, exist_ok=True)
LOGS_DIR.mkdir(parents=True, exist_ok=True)
# MODELS_DIR n'est pas créé car il est dans l'exécutable (PyInstaller) ou existe déjà (dev)

# Configuration Supabase
SUPABASE_URL = os.getenv("SUPABASE_URL", "https://ozphkjphnlxznshyyift.supabase.co")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im96cGhranBobmx4em5zaHl5aWZ0Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTkzNTg0ODUsImV4cCI6MjA3NDkzNDQ4NX0.nWRcmmRDf_Qdj_wngB53R7XocDb46wiP6JTETYfS5hs")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im96cGhranBobmx4em5zaHl5aWZ0Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1OTM1ODQ4NSwiZXhwIjoyMDc0OTM0NDg1fQ.HaOP5n0QErjcxTSuEn8us7lgcILag0brBdtA01Fx_zc")

# Configuration de l'application
APP_NAME = "DIANA"
APP_FULL_NAME = "Diagnostic Intelligent Automatisé pour les Nouvelles Analyses"
APP_VERSION = os.getenv("APP_VERSION", "1.0.0")
APP_DESCRIPTION = "Détection intelligente du cancer du sein par IA"

# Configuration des mises à jour
UPDATE_CHECK_URL = os.getenv("UPDATE_CHECK_URL", "https://diana-updates.example.com/latest.json")
UPDATE_CHECK_INTERVAL = 3600  # Vérifier toutes les heures

# Configuration du modèle
MODEL_ENCRYPTED_PATH = MODELS_DIR / "breast_cancer_model.onnx.enc"
MODEL_DECRYPTED_PATH = MODELS_DIR / "breast_cancer_model.onnx"
FILTER_MODEL_PATH = Path("models/filter/breast_cancer_filter.onnx")
ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY", "").encode()

# Configuration des quotas
FREE_TIER_LIMIT = int(os.getenv("FREE_TIER_LIMIT", "5000"))
MAX_DEVICES_PER_USER = int(os.getenv("MAX_DEVICES_PER_USER", "2"))
QUOTA_FILE = DATA_DIR / "user_quota.json"
SESSION_FILE = DATA_DIR / "session.dat"

# Configuration de l'interface
WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 800
THEME_DARK = True

# Configuration des logs
LOG_FILE = LOGS_DIR / "diana.log"
LOG_LEVEL = "INFO"

# Formats d'images supportés
SUPPORTED_IMAGE_FORMATS = [".jpg", ".jpeg", ".png", ".dcm", ".tiff", ".bmp"]

# Configuration du device tracking
DEVICE_ID_FILE = DATA_DIR / "device_id.txt"

# Tables Supabase
SUPABASE_USERS_TABLE = "users"
SUPABASE_DEVICES_TABLE = "user_devices"
SUPABASE_USAGE_TABLE = "usage_logs"

