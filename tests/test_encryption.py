"""
Tests pour le gestionnaire de chiffrement
"""

import pytest
import tempfile
from pathlib import Path
import sys

# Ajouter le répertoire parent au path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.encryption_manager import EncryptionManager


class TestEncryptionManager:
    """Tests pour EncryptionManager"""
    
    @pytest.fixture
    def temp_files(self):
        """Crée des fichiers temporaires pour les tests"""
        # Fichier source
        source_file = tempfile.NamedTemporaryFile(mode='wb', delete=False)
        source_file.write(b"Contenu de test pour DIANA")
        source_file.close()
        
        # Fichier chiffré
        encrypted_file = tempfile.NamedTemporaryFile(delete=False, suffix='.enc')
        encrypted_file.close()
        
        # Fichier déchiffré
        decrypted_file = tempfile.NamedTemporaryFile(delete=False)
        decrypted_file.close()
        
        files = {
            'source': Path(source_file.name),
            'encrypted': Path(encrypted_file.name),
            'decrypted': Path(decrypted_file.name)
        }
        
        yield files
        
        # Nettoyage
        for file_path in files.values():
            file_path.unlink(missing_ok=True)
    
    def test_encryption(self, temp_files):
        """Test du chiffrement"""
        manager = EncryptionManager()
        
        success = manager.encrypt_file(
            temp_files['source'],
            temp_files['encrypted']
        )
        
        assert success is True
        assert temp_files['encrypted'].exists()
        
        # Vérifier que le contenu est différent
        with open(temp_files['source'], 'rb') as f:
            original = f.read()
        
        with open(temp_files['encrypted'], 'rb') as f:
            encrypted = f.read()
        
        assert original != encrypted
    
    def test_decryption(self, temp_files):
        """Test du déchiffrement"""
        manager = EncryptionManager()
        
        # Chiffrer
        manager.encrypt_file(
            temp_files['source'],
            temp_files['encrypted']
        )
        
        # Déchiffrer
        success = manager.decrypt_file(
            temp_files['encrypted'],
            temp_files['decrypted']
        )
        
        assert success is True
        assert temp_files['decrypted'].exists()
        
        # Vérifier que le contenu est identique à l'original
        with open(temp_files['source'], 'rb') as f:
            original = f.read()
        
        with open(temp_files['decrypted'], 'rb') as f:
            decrypted = f.read()
        
        assert original == decrypted
    
    def test_decrypt_to_memory(self, temp_files):
        """Test du déchiffrement en mémoire"""
        manager = EncryptionManager()
        
        # Chiffrer
        manager.encrypt_file(
            temp_files['source'],
            temp_files['encrypted']
        )
        
        # Déchiffrer en mémoire
        decrypted_data = manager.decrypt_to_memory(temp_files['encrypted'])
        
        assert decrypted_data is not None
        
        # Vérifier le contenu
        with open(temp_files['source'], 'rb') as f:
            original = f.read()
        
        assert decrypted_data == original
    
    def test_verify_encrypted_file(self, temp_files):
        """Test de la vérification d'un fichier chiffré"""
        manager = EncryptionManager()
        
        # Chiffrer
        manager.encrypt_file(
            temp_files['source'],
            temp_files['encrypted']
        )
        
        # Vérifier
        is_valid = manager.verify_encrypted_file(temp_files['encrypted'])
        
        assert is_valid is True
    
    def test_wrong_key(self, temp_files):
        """Test avec une mauvaise clé"""
        manager1 = EncryptionManager()
        
        # Chiffrer avec une clé
        manager1.encrypt_file(
            temp_files['source'],
            temp_files['encrypted']
        )
        
        # Essayer de déchiffrer avec une autre clé
        manager2 = EncryptionManager(key=b"wrong_key_12345678901234567890")
        
        success = manager2.decrypt_file(
            temp_files['encrypted'],
            temp_files['decrypted']
        )
        
        # Le déchiffrement devrait échouer
        assert success is False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

