"""
Tests pour le gestionnaire de quota
"""

import pytest
import tempfile
from pathlib import Path
import sys

# Ajouter le répertoire parent au path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.quota_manager import QuotaManager


class TestQuotaManager:
    """Tests pour QuotaManager"""
    
    @pytest.fixture
    def temp_quota_file(self):
        """Crée un fichier de quota temporaire"""
        temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json')
        temp_file.close()
        yield Path(temp_file.name)
        # Nettoyage
        Path(temp_file.name).unlink(missing_ok=True)
    
    def test_initialization(self, temp_quota_file):
        """Test de l'initialisation"""
        manager = QuotaManager(temp_quota_file)
        assert temp_quota_file.exists()
        assert manager.get_used_analyses() == 0
        assert manager.get_remaining_analyses() == 5000
    
    def test_can_analyze_free_tier(self, temp_quota_file):
        """Test de la vérification du quota gratuit"""
        manager = QuotaManager(temp_quota_file)
        assert manager.can_analyze() is True
    
    def test_increment_usage(self, temp_quota_file):
        """Test de l'incrémentation du compteur"""
        manager = QuotaManager(temp_quota_file)
        
        initial_count = manager.get_used_analyses()
        manager.increment_usage()
        new_count = manager.get_used_analyses()
        
        assert new_count == initial_count + 1
        assert manager.get_remaining_analyses() == 4999
    
    def test_quota_exhaustion(self, temp_quota_file):
        """Test de l'épuisement du quota"""
        manager = QuotaManager(temp_quota_file)
        manager.free_limit = 10  # Limite basse pour test
        
        # Utiliser tout le quota
        for _ in range(10):
            assert manager.can_analyze() is True
            manager.increment_usage()
        
        # Vérifier que le quota est épuisé
        assert manager.can_analyze() is False
        assert manager.get_remaining_analyses() == 0
    
    def test_premium_unlimited(self, temp_quota_file):
        """Test du mode premium illimité"""
        manager = QuotaManager(temp_quota_file)
        manager.set_premium(True)
        
        assert manager.is_premium() is True
        assert manager.can_analyze() is True
        assert manager.get_remaining_analyses() == -1  # Illimité
        
        # Même après de nombreuses utilisations
        for _ in range(1000):
            manager.increment_usage()
        
        assert manager.can_analyze() is True
    
    def test_stats(self, temp_quota_file):
        """Test des statistiques"""
        manager = QuotaManager(temp_quota_file)
        
        # Effectuer quelques analyses
        for _ in range(5):
            manager.increment_usage()
        
        stats = manager.get_stats()
        
        assert stats['used'] == 5
        assert stats['remaining'] == 4995
        assert stats['is_premium'] is False
        assert stats['limit'] == 5000


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

