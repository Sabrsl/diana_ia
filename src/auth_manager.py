"""
DIANA - Gestionnaire d'authentification Supabase
Gestion de l'authentification premium et du contrôle des appareils
"""

import logging
import uuid
import json
from pathlib import Path
from typing import Optional, Dict, Tuple
from datetime import datetime

from supabase import create_client, Client
import config

logger = logging.getLogger(__name__)


class AuthManager:
    """Gestion de l'authentification et des comptes premium via Supabase"""
    
    def __init__(self):
        self.supabase: Client = create_client(
            config.SUPABASE_URL,
            config.SUPABASE_ANON_KEY
        )
        self.current_user = None
        self.device_id = self._get_or_create_device_id()
        self.session_file = config.SESSION_FILE
        self._load_session()
    
    def _get_or_create_device_id(self) -> str:
        """Obtient ou crée un identifiant unique pour cet appareil"""
        device_file = config.DEVICE_ID_FILE
        
        if device_file.exists():
            try:
                with open(device_file, 'r') as f:
                    device_id = f.read().strip()
                    if device_id:
                        return device_id
            except Exception as e:
                logger.error(f"Erreur lecture device_id: {e}")
        
        # Créer un nouvel ID
        device_id = str(uuid.uuid4())
        try:
            with open(device_file, 'w') as f:
                f.write(device_id)
        except Exception as e:
            logger.error(f"Erreur sauvegarde device_id: {e}")
        
        return device_id
    
    def _save_session(self, user_data: Dict):
        """Sauvegarde la session utilisateur localement"""
        try:
            session_data = {
                "user_id": user_data.get("id"),
                "email": user_data.get("email"),
                "is_premium": user_data.get("is_premium", False),
                "device_id": self.device_id,
                "timestamp": datetime.now().isoformat()
            }
            with open(self.session_file, 'w', encoding='utf-8') as f:
                json.dump(session_data, f, indent=2)
            logger.info("Session sauvegardée")
        except Exception as e:
            logger.error(f"Erreur sauvegarde session: {e}")
    
    def _load_session(self) -> bool:
        """Charge la session utilisateur depuis le fichier local"""
        if not self.session_file.exists():
            return False
        
        try:
            with open(self.session_file, 'r', encoding='utf-8') as f:
                session_data = json.load(f)
                self.current_user = session_data
                logger.info(f"Session chargée pour {session_data.get('email')}")
                return True
        except Exception as e:
            logger.error(f"Erreur chargement session: {e}")
            return False
    
    def _clear_session(self):
        """Efface la session locale"""
        try:
            if self.session_file.exists():
                self.session_file.unlink()
            self.current_user = None
            logger.info("Session effacée")
        except Exception as e:
            logger.error(f"Erreur effacement session: {e}")
    
    async def sign_up(self, email: str, password: str) -> Tuple[bool, str]:
        """
        Inscription d'un nouvel utilisateur
        Returns: (success, message)
        """
        try:
            response = self.supabase.auth.sign_up({
                "email": email,
                "password": password
            })
            
            if response.user:
                # Créer l'entrée utilisateur dans la table users
                user_data = {
                    "id": response.user.id,
                    "email": email,
                    "is_premium": False,
                    "active_devices": [],
                    "max_devices": config.MAX_DEVICES_PER_USER,
                    "created_at": datetime.now().isoformat()
                }
                
                self.supabase.table(config.SUPABASE_USERS_TABLE).insert(user_data).execute()
                
                logger.info(f"Utilisateur créé: {email}")
                return True, "Inscription réussie ! Vérifiez votre email pour confirmer."
            
            return False, "Erreur lors de l'inscription"
            
        except Exception as e:
            logger.error(f"Erreur inscription: {e}")
            return False, f"Erreur: {str(e)}"
    
    async def sign_in(self, email: str, password: str) -> Tuple[bool, str]:
        """
        Connexion d'un utilisateur existant
        Returns: (success, message)
        """
        try:
            response = self.supabase.auth.sign_in_with_password({
                "email": email,
                "password": password
            })
            
            if response.user:
                # Récupérer les infos utilisateur depuis la table
                user_response = self.supabase.table(config.SUPABASE_USERS_TABLE)\
                    .select("*")\
                    .eq("id", response.user.id)\
                    .execute()
                
                if user_response.data and len(user_response.data) > 0:
                    user_data = user_response.data[0]
                    
                    # Vérifier le nombre d'appareils actifs
                    if not self._can_add_device(user_data):
                        return False, f"Limite d'appareils atteinte ({config.MAX_DEVICES_PER_USER} max)"
                    
                    # Enregistrer cet appareil
                    self._register_device(response.user.id, user_data)
                    
                    # Sauvegarder la session
                    self.current_user = {
                        "id": response.user.id,
                        "email": email,
                        "is_premium": user_data.get("is_premium", False)
                    }
                    self._save_session(self.current_user)
                    
                    logger.info(f"Connexion réussie: {email}")
                    return True, "Connexion réussie !"
                
                return False, "Utilisateur non trouvé dans la base"
            
            return False, "Email ou mot de passe incorrect"
            
        except Exception as e:
            logger.error(f"Erreur connexion: {e}")
            return False, f"Erreur: {str(e)}"
    
    def _can_add_device(self, user_data: Dict) -> bool:
        """Vérifie si l'utilisateur peut ajouter un nouvel appareil"""
        active_devices = user_data.get("active_devices", [])
        max_devices = user_data.get("max_devices", config.MAX_DEVICES_PER_USER)
        
        # Si cet appareil est déjà enregistré, OK
        if self.device_id in active_devices:
            return True
        
        # Sinon, vérifier le quota
        return len(active_devices) < max_devices
    
    def _register_device(self, user_id: str, user_data: Dict):
        """Enregistre l'appareil actuel pour l'utilisateur"""
        try:
            active_devices = user_data.get("active_devices", [])
            
            if self.device_id not in active_devices:
                active_devices.append(self.device_id)
                
                # Mettre à jour la table users
                self.supabase.table(config.SUPABASE_USERS_TABLE)\
                    .update({"active_devices": active_devices})\
                    .eq("id", user_id)\
                    .execute()
                
                logger.info(f"Appareil enregistré: {self.device_id}")
            
            # Enregistrer dans la table des devices
            device_data = {
                "user_id": user_id,
                "device_id": self.device_id,
                "last_login": datetime.now().isoformat()
            }
            
            # Upsert (insert or update)
            self.supabase.table(config.SUPABASE_DEVICES_TABLE)\
                .upsert(device_data, on_conflict="device_id")\
                .execute()
                
        except Exception as e:
            logger.error(f"Erreur enregistrement appareil: {e}")
    
    def sign_out(self):
        """Déconnexion de l'utilisateur"""
        try:
            if self.current_user:
                # Optionnel : retirer l'appareil de la liste
                # (pour permettre la connexion ailleurs)
                pass
            
            self.supabase.auth.sign_out()
            self._clear_session()
            logger.info("Déconnexion réussie")
            
        except Exception as e:
            logger.error(f"Erreur déconnexion: {e}")
    
    def is_logged_in(self) -> bool:
        """Vérifie si un utilisateur est connecté"""
        return self.current_user is not None
    
    def is_premium(self) -> bool:
        """Vérifie si l'utilisateur actuel est premium"""
        if not self.current_user:
            return False
        return self.current_user.get("is_premium", False)
    
    def get_current_user(self) -> Optional[Dict]:
        """Retourne les informations de l'utilisateur actuel"""
        return self.current_user
    
    async def refresh_user_status(self) -> bool:
        """Rafraîchit le statut premium de l'utilisateur depuis Supabase"""
        if not self.current_user:
            return False
        
        try:
            user_response = self.supabase.table(config.SUPABASE_USERS_TABLE)\
                .select("is_premium")\
                .eq("id", self.current_user["id"])\
                .execute()
            
            if user_response.data and len(user_response.data) > 0:
                is_premium = user_response.data[0].get("is_premium", False)
                self.current_user["is_premium"] = is_premium
                self._save_session(self.current_user)
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Erreur rafraîchissement statut: {e}")
            return False


# Singleton global
_auth_manager_instance: Optional[AuthManager] = None


def get_auth_manager() -> AuthManager:
    """Retourne l'instance singleton du gestionnaire d'authentification"""
    global _auth_manager_instance
    if _auth_manager_instance is None:
        _auth_manager_instance = AuthManager()
    return _auth_manager_instance

