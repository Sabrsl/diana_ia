"""
DIANA - Gestionnaire de quota local
Gestion du système freemium avec quota de 5000 analyses gratuites
"""

import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict
import config

logger = logging.getLogger(__name__)


class QuotaManager:
    """Gestion du quota d'analyses pour la version gratuite"""
    
    def __init__(self, quota_file: Path = config.QUOTA_FILE):
        self.quota_file = quota_file
        self.free_limit = config.FREE_TIER_LIMIT
        self._ensure_quota_file()
    
    def _ensure_quota_file(self):
        """Crée le fichier de quota s'il n'existe pas"""
        if not self.quota_file.exists():
            initial_data = {
                "analyses_count": 0,
                "first_use_date": datetime.now().isoformat(),
                "last_analysis_date": None,
                "is_premium": False
            }
            self._save_quota(initial_data)
            logger.info("Fichier de quota initialisé")
    
    def _load_quota(self) -> Dict:
        """Charge les données de quota depuis le fichier"""
        try:
            with open(self.quota_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Erreur lors du chargement du quota: {e}")
            return {
                "analyses_count": 0,
                "first_use_date": datetime.now().isoformat(),
                "last_analysis_date": None,
                "is_premium": False
            }
    
    def _save_quota(self, data: Dict):
        """Sauvegarde les données de quota"""
        try:
            with open(self.quota_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Erreur lors de la sauvegarde du quota: {e}")
    
    def get_remaining_analyses(self) -> int:
        """Retourne le nombre d'analyses restantes"""
        data = self._load_quota()
        if data.get("is_premium", False):
            return -1  # Illimité
        
        used = data.get("analyses_count", 0)
        remaining = max(0, self.free_limit - used)
        return remaining
    
    def get_used_analyses(self) -> int:
        """Retourne le nombre d'analyses utilisées"""
        data = self._load_quota()
        return data.get("analyses_count", 0)
    
    def can_analyze(self) -> bool:
        """Vérifie si l'utilisateur peut effectuer une analyse"""
        data = self._load_quota()
        
        # Si premium, toujours autorisé
        if data.get("is_premium", False):
            return True
        
        # Sinon, vérifier le quota
        used = data.get("analyses_count", 0)
        return used < self.free_limit
    
    def increment_usage(self) -> bool:
        """Incrémente le compteur d'utilisation"""
        data = self._load_quota()
        
        # Si premium, incrémenter sans limite
        if data.get("is_premium", False):
            data["analyses_count"] = data.get("analyses_count", 0) + 1
            data["last_analysis_date"] = datetime.now().isoformat()
            self._save_quota(data)
            logger.info(f"Analyse effectuée (Premium). Total: {data['analyses_count']}")
            return True
        
        # Vérifier si le quota n'est pas dépassé
        if not self.can_analyze():
            logger.warning("Quota gratuit épuisé")
            return False
        
        # Incrémenter
        data["analyses_count"] = data.get("analyses_count", 0) + 1
        data["last_analysis_date"] = datetime.now().isoformat()
        self._save_quota(data)
        
        remaining = self.get_remaining_analyses()
        logger.info(f"Analyse effectuée. Restantes: {remaining}/{self.free_limit}")
        
        return True
    
    def set_premium(self, is_premium: bool):
        """Active ou désactive le mode premium"""
        data = self._load_quota()
        data["is_premium"] = is_premium
        self._save_quota(data)
        logger.info(f"Mode premium {'activé' if is_premium else 'désactivé'}")
    
    def is_premium(self) -> bool:
        """Vérifie si l'utilisateur est premium"""
        data = self._load_quota()
        return data.get("is_premium", False)
    
    def reset_quota(self):
        """Réinitialise le quota (admin uniquement)"""
        initial_data = {
            "analyses_count": 0,
            "first_use_date": datetime.now().isoformat(),
            "last_analysis_date": None,
            "is_premium": False
        }
        self._save_quota(initial_data)
        logger.info("Quota réinitialisé")
    
    def get_stats(self) -> Dict:
        """Retourne les statistiques d'utilisation"""
        data = self._load_quota()
        remaining = self.get_remaining_analyses()
        
        return {
            "used": data.get("analyses_count", 0),
            "remaining": remaining if remaining >= 0 else "Illimité",
            "limit": self.free_limit if not data.get("is_premium") else "Illimité",
            "is_premium": data.get("is_premium", False),
            "first_use": data.get("first_use_date"),
            "last_analysis": data.get("last_analysis_date")
        }


# Singleton global
_quota_manager_instance: Optional[QuotaManager] = None


def get_quota_manager() -> QuotaManager:
    """Retourne l'instance singleton du gestionnaire de quota"""
    global _quota_manager_instance
    if _quota_manager_instance is None:
        _quota_manager_instance = QuotaManager()
    return _quota_manager_instance

