"""
DIANA - Gestionnaire de chiffrement
Chiffrement/déchiffrement sécurisé du modèle ONNX
"""

import logging
from pathlib import Path
from typing import Optional
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend
import base64
import os

import config

logger = logging.getLogger(__name__)


class EncryptionManager:
    """Gestion du chiffrement et déchiffrement du modèle ONNX"""
    
    def __init__(self, key: Optional[bytes] = None):
        """
        Initialise le gestionnaire de chiffrement
        
        Args:
            key: Clé de chiffrement (utilise config.ENCRYPTION_KEY par défaut)
        """
        if key is None:
            key = config.ENCRYPTION_KEY
        
        self.encryption_key = self._derive_key(key)
        self.fernet = Fernet(self.encryption_key)
    
    def _derive_key(self, password: bytes) -> bytes:
        """
        Dérive une clé Fernet à partir d'un mot de passe
        
        Args:
            password: Mot de passe source
            
        Returns:
            Clé Fernet valide (32 bytes encodés en base64)
        """
        # Si déjà une clé Fernet valide, la retourner
        try:
            Fernet(password)
            return password
        except:
            pass
        
        # Sinon, dériver une clé à partir du mot de passe
        salt = b'diana_breast_cancer_detection_2025'  # Salt fixe pour reproductibilité
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
            backend=default_backend()
        )
        key = base64.urlsafe_b64encode(kdf.derive(password))
        return key
    
    def encrypt_file(self, input_path: Path, output_path: Optional[Path] = None) -> bool:
        """
        Chiffre un fichier (ex: modèle ONNX)
        
        Args:
            input_path: Chemin du fichier à chiffrer
            output_path: Chemin du fichier chiffré (par défaut: input_path + '.enc')
            
        Returns:
            True si succès, False sinon
        """
        if output_path is None:
            output_path = Path(str(input_path) + '.enc')
        
        try:
            logger.info(f"Chiffrement de {input_path}...")
            
            # Lire le fichier source
            with open(input_path, 'rb') as f:
                data = f.read()
            
            # Chiffrer
            encrypted_data = self.fernet.encrypt(data)
            
            # Écrire le fichier chiffré
            with open(output_path, 'wb') as f:
                f.write(encrypted_data)
            
            logger.info(f"Fichier chiffré: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Erreur lors du chiffrement: {e}")
            return False
    
    def decrypt_file(self, input_path: Path, output_path: Optional[Path] = None) -> bool:
        """
        Déchiffre un fichier
        
        Args:
            input_path: Chemin du fichier chiffré
            output_path: Chemin du fichier déchiffré
            
        Returns:
            True si succès, False sinon
        """
        if output_path is None:
            output_path = Path(str(input_path).replace('.enc', ''))
        
        try:
            logger.info(f"Déchiffrement de {input_path}...")
            
            # Lire le fichier chiffré
            with open(input_path, 'rb') as f:
                encrypted_data = f.read()
            
            # Déchiffrer
            decrypted_data = self.fernet.decrypt(encrypted_data)
            
            # Écrire le fichier déchiffré
            with open(output_path, 'wb') as f:
                f.write(decrypted_data)
            
            logger.info(f"Fichier déchiffré: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Erreur lors du déchiffrement: {e}")
            return False
    
    def decrypt_to_memory(self, input_path: Path) -> Optional[bytes]:
        """
        Déchiffre un fichier directement en mémoire sans l'écrire sur disque
        
        Args:
            input_path: Chemin du fichier chiffré
            
        Returns:
            Données déchiffrées ou None si erreur
        """
        try:
            logger.info(f"Déchiffrement en mémoire: {input_path}")
            
            # Lire le fichier chiffré
            with open(input_path, 'rb') as f:
                encrypted_data = f.read()
            
            # Déchiffrer
            decrypted_data = self.fernet.decrypt(encrypted_data)
            
            logger.info("Déchiffrement en mémoire réussi")
            return decrypted_data
            
        except Exception as e:
            logger.error(f"Erreur déchiffrement en mémoire: {e}")
            return None
    
    def verify_encrypted_file(self, file_path: Path) -> bool:
        """
        Vérifie qu'un fichier est bien chiffré et déchiffrable
        
        Args:
            file_path: Chemin du fichier chiffré
            
        Returns:
            True si le fichier est valide
        """
        try:
            with open(file_path, 'rb') as f:
                encrypted_data = f.read()
            
            # Essayer de déchiffrer (sans sauvegarder)
            self.fernet.decrypt(encrypted_data)
            
            return True
            
        except Exception as e:
            logger.error(f"Fichier chiffré invalide: {e}")
            return False
    
    @staticmethod
    def generate_key() -> bytes:
        """
        Génère une nouvelle clé de chiffrement Fernet
        
        Returns:
            Clé de chiffrement encodée en base64
        """
        return Fernet.generate_key()
    
    def cleanup_decrypted_file(self, file_path: Path):
        """
        Supprime un fichier déchiffré de manière sécurisée
        
        Args:
            file_path: Chemin du fichier à supprimer
        """
        try:
            if file_path.exists():
                # Écraser le fichier avec des données aléatoires avant suppression
                file_size = file_path.stat().st_size
                with open(file_path, 'wb') as f:
                    f.write(os.urandom(file_size))
                
                # Supprimer le fichier
                file_path.unlink()
                logger.info(f"Fichier déchiffré supprimé: {file_path}")
                
        except Exception as e:
            logger.error(f"Erreur suppression fichier: {e}")


class ModelDecryptor:
    """Gestionnaire spécialisé pour le déchiffrement du modèle ONNX"""
    
    def __init__(self):
        self.encryption_manager = EncryptionManager()
        self.encrypted_model_path = config.MODEL_ENCRYPTED_PATH
        self.decrypted_model_path = config.MODEL_DECRYPTED_PATH
    
    def can_decrypt(self, is_premium: bool, has_quota: bool) -> bool:
        """
        Vérifie si le déchiffrement est autorisé
        
        Args:
            is_premium: L'utilisateur est premium
            has_quota: L'utilisateur a du quota gratuit restant
            
        Returns:
            True si autorisé
        """
        return is_premium or has_quota
    
    def decrypt_model(self, is_premium: bool, has_quota: bool) -> Optional[Path]:
        """
        Déchiffre le modèle ONNX si autorisé
        
        Args:
            is_premium: L'utilisateur est premium
            has_quota: L'utilisateur a du quota gratuit restant
            
        Returns:
            Chemin du modèle déchiffré ou None si non autorisé
        """
        if not self.can_decrypt(is_premium, has_quota):
            logger.warning("Déchiffrement non autorisé (pas de quota/premium)")
            return None
        
        if not self.encrypted_model_path.exists():
            logger.error(f"Modèle chiffré introuvable: {self.encrypted_model_path}")
            return None
        
        # Déchiffrer le modèle
        success = self.encryption_manager.decrypt_file(
            self.encrypted_model_path,
            self.decrypted_model_path
        )
        
        if success and self.decrypted_model_path.exists():
            return self.decrypted_model_path
        
        return None
    
    def get_model_in_memory(self, is_premium: bool, has_quota: bool) -> Optional[bytes]:
        """
        Déchiffre le modèle directement en mémoire (plus sécurisé)
        
        Args:
            is_premium: L'utilisateur est premium
            has_quota: L'utilisateur a du quota gratuit restant
            
        Returns:
            Données du modèle déchiffré ou None
        """
        if not self.can_decrypt(is_premium, has_quota):
            logger.warning("Déchiffrement non autorisé")
            return None
        
        if not self.encrypted_model_path.exists():
            logger.error(f"Modèle chiffré introuvable: {self.encrypted_model_path}")
            return None
        
        return self.encryption_manager.decrypt_to_memory(self.encrypted_model_path)
    
    def cleanup(self):
        """Supprime le modèle déchiffré du disque"""
        if self.decrypted_model_path.exists():
            self.encryption_manager.cleanup_decrypted_file(self.decrypted_model_path)


# Singleton global
_model_decryptor_instance: Optional[ModelDecryptor] = None


def get_model_decryptor() -> ModelDecryptor:
    """Retourne l'instance singleton du déchiffreur de modèle"""
    global _model_decryptor_instance
    if _model_decryptor_instance is None:
        _model_decryptor_instance = ModelDecryptor()
    return _model_decryptor_instance

