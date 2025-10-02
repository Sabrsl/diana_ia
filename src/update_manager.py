"""
DIANA - Gestionnaire de mises à jour automatiques
Système d'auto-update professionnel avec vérification d'intégrité
"""

import logging
import json
import hashlib
import tempfile
import subprocess
import sys
from pathlib import Path
from typing import Optional, Dict, Tuple
from packaging import version
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

import config

logger = logging.getLogger(__name__)


class UpdateManager:
    """Gestion des mises à jour automatiques de l'application"""
    
    def __init__(self):
        self.current_version = version.parse(config.APP_VERSION)
        self.update_url = config.UPDATE_CHECK_URL
        self.session = self._create_session()
        self.update_available = False
        self.latest_info: Optional[Dict] = None
    
    def _create_session(self) -> requests.Session:
        """Crée une session HTTP avec retry automatique"""
        session = requests.Session()
        retry = Retry(
            total=3,
            backoff_factor=0.3,
            status_forcelist=[500, 502, 503, 504]
        )
        adapter = HTTPAdapter(max_retries=retry)
        session.mount('http://', adapter)
        session.mount('https://', adapter)
        return session
    
    def check_for_updates(self, timeout: int = 10) -> Tuple[bool, Optional[Dict]]:
        """
        Vérifie si une mise à jour est disponible
        
        Args:
            timeout: Timeout en secondes pour la requête
            
        Returns:
            (update_available, update_info)
        """
        try:
            logger.info(f"Vérification des mises à jour depuis {self.update_url}")
            
            response = self.session.get(self.update_url, timeout=timeout)
            response.raise_for_status()
            
            update_info = response.json()
            
            # Vérifier la structure des données
            required_fields = ['version', 'download_url', 'checksum', 'release_notes']
            if not all(field in update_info for field in required_fields):
                logger.error("Format de mise à jour invalide")
                return False, None
            
            # Comparer les versions
            latest_version = version.parse(update_info['version'])
            
            if latest_version > self.current_version:
                self.update_available = True
                self.latest_info = update_info
                logger.info(f"Mise à jour disponible: {latest_version} > {self.current_version}")
                return True, update_info
            
            logger.info("Application à jour")
            return False, None
            
        except requests.exceptions.RequestException as e:
            logger.warning(f"Impossible de vérifier les mises à jour: {e}")
            return False, None
        except Exception as e:
            logger.error(f"Erreur lors de la vérification: {e}")
            return False, None
    
    def download_update(self, download_url: str, progress_callback=None) -> Optional[Path]:
        """
        Télécharge la mise à jour
        
        Args:
            download_url: URL du fichier à télécharger
            progress_callback: Fonction appelée avec (bytes_downloaded, total_bytes)
            
        Returns:
            Chemin du fichier téléchargé ou None si erreur
        """
        try:
            logger.info(f"Téléchargement depuis {download_url}")
            
            response = self.session.get(download_url, stream=True, timeout=30)
            response.raise_for_status()
            
            total_size = int(response.headers.get('content-length', 0))
            
            # Créer un fichier temporaire
            temp_file = tempfile.NamedTemporaryFile(
                delete=False,
                suffix='.exe' if sys.platform == 'win32' else ''
            )
            temp_path = Path(temp_file.name)
            
            downloaded = 0
            chunk_size = 8192
            
            with open(temp_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=chunk_size):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        
                        if progress_callback and total_size > 0:
                            progress_callback(downloaded, total_size)
            
            logger.info(f"Téléchargement terminé: {temp_path}")
            return temp_path
            
        except Exception as e:
            logger.error(f"Erreur lors du téléchargement: {e}")
            return None
    
    def verify_checksum(self, file_path: Path, expected_checksum: str, algorithm: str = 'sha256') -> bool:
        """
        Vérifie l'intégrité du fichier téléchargé
        
        Args:
            file_path: Chemin du fichier à vérifier
            expected_checksum: Checksum attendu
            algorithm: Algorithme de hash ('sha256', 'md5', etc.)
            
        Returns:
            True si le checksum correspond
        """
        try:
            logger.info(f"Vérification du checksum ({algorithm})...")
            
            hash_func = hashlib.new(algorithm)
            
            with open(file_path, 'rb') as f:
                while chunk := f.read(8192):
                    hash_func.update(chunk)
            
            calculated_checksum = hash_func.hexdigest()
            
            if calculated_checksum.lower() == expected_checksum.lower():
                logger.info("Checksum valide")
                return True
            
            logger.error(f"Checksum invalide: {calculated_checksum} != {expected_checksum}")
            return False
            
        except Exception as e:
            logger.error(f"Erreur lors de la vérification: {e}")
            return False
    
    def install_update(self, update_file: Path) -> bool:
        """
        Installe la mise à jour
        
        Args:
            update_file: Chemin de l'installateur téléchargé
            
        Returns:
            True si l'installation a démarré avec succès
        """
        try:
            logger.info(f"Installation de la mise à jour: {update_file}")
            
            if sys.platform == 'win32':
                # Windows: lancer l'installateur en mode silencieux
                subprocess.Popen(
                    [str(update_file), '/SILENT', '/CLOSEAPPLICATIONS'],
                    creationflags=subprocess.DETACHED_PROCESS
                )
            elif sys.platform == 'darwin':
                # macOS: ouvrir le DMG ou lancer l'installateur
                subprocess.Popen(['open', str(update_file)])
            else:
                # Linux: lancer le script d'installation
                subprocess.Popen([str(update_file)])
            
            logger.info("Installation démarrée")
            return True
            
        except Exception as e:
            logger.error(f"Erreur lors de l'installation: {e}")
            return False
    
    def perform_update(self, progress_callback=None) -> Tuple[bool, str]:
        """
        Effectue la mise à jour complète (téléchargement + vérification + installation)
        
        Args:
            progress_callback: Fonction de callback pour la progression
            
        Returns:
            (success, message)
        """
        if not self.update_available or not self.latest_info:
            return False, "Aucune mise à jour disponible"
        
        try:
            # 1. Télécharger
            download_url = self.latest_info['download_url']
            update_file = self.download_update(download_url, progress_callback)
            
            if not update_file:
                return False, "Échec du téléchargement"
            
            # 2. Vérifier le checksum
            checksum = self.latest_info['checksum']
            algorithm = self.latest_info.get('checksum_algorithm', 'sha256')
            
            if not self.verify_checksum(update_file, checksum, algorithm):
                update_file.unlink()  # Supprimer le fichier corrompu
                return False, "Fichier corrompu (checksum invalide)"
            
            # 3. Installer
            if not self.install_update(update_file):
                return False, "Échec de l'installation"
            
            return True, "Mise à jour installée avec succès"
            
        except Exception as e:
            logger.error(f"Erreur lors de la mise à jour: {e}")
            return False, f"Erreur: {str(e)}"
    
    def get_release_notes(self) -> Optional[str]:
        """
        Retourne les notes de version de la dernière mise à jour
        
        Returns:
            Notes de version ou None
        """
        if self.latest_info:
            return self.latest_info.get('release_notes')
        return None
    
    def get_update_info(self) -> Optional[Dict]:
        """
        Retourne les informations complètes sur la mise à jour disponible
        
        Returns:
            Dictionnaire avec les informations ou None
        """
        return self.latest_info


class UpdateScheduler:
    """Planificateur pour les vérifications automatiques de mises à jour"""
    
    def __init__(self, check_interval: int = config.UPDATE_CHECK_INTERVAL):
        self.check_interval = check_interval
        self.update_manager = UpdateManager()
        self.last_check_file = config.DATA_DIR / "last_update_check.json"
    
    def should_check_now(self) -> bool:
        """Vérifie s'il est temps de vérifier les mises à jour"""
        if not self.last_check_file.exists():
            return True
        
        try:
            with open(self.last_check_file, 'r') as f:
                data = json.load(f)
                last_check = data.get('timestamp', 0)
                
            import time
            current_time = time.time()
            
            return (current_time - last_check) > self.check_interval
            
        except Exception:
            return True
    
    def update_last_check(self):
        """Met à jour la date de dernière vérification"""
        try:
            import time
            data = {'timestamp': time.time()}
            
            with open(self.last_check_file, 'w') as f:
                json.dump(data, f)
                
        except Exception as e:
            logger.error(f"Erreur mise à jour last_check: {e}")
    
    def check_and_notify(self) -> Tuple[bool, Optional[Dict]]:
        """
        Vérifie les mises à jour si nécessaire
        
        Returns:
            (update_available, update_info)
        """
        if not self.should_check_now():
            return False, None
        
        update_available, update_info = self.update_manager.check_for_updates()
        self.update_last_check()
        
        return update_available, update_info


# Singleton global
_update_manager_instance: Optional[UpdateManager] = None


def get_update_manager() -> UpdateManager:
    """Retourne l'instance singleton du gestionnaire de mises à jour"""
    global _update_manager_instance
    if _update_manager_instance is None:
        _update_manager_instance = UpdateManager()
    return _update_manager_instance

