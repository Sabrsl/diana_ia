"""
DIANA - Moteur d'inférence
Exécution des prédictions avec le modèle ONNX
"""

import logging
import io
from pathlib import Path
from typing import Optional, Dict, Tuple, List
import numpy as np
from PIL import Image
import cv2
import onnxruntime as ort

import config
from src.encryption_manager import get_model_decryptor
from src.quota_manager import get_quota_manager
from src.auth_manager import get_auth_manager
from src.image_filter import get_image_filter

logger = logging.getLogger(__name__)


class InferenceEngine:
    """Moteur d'inférence pour la détection du cancer du sein"""
    
    def __init__(self):
        self.session: Optional[ort.InferenceSession] = None
        self.input_name: Optional[str] = None
        self.output_names: Optional[List[str]] = None
        self.input_shape: Optional[Tuple] = None
        self.is_loaded = False
    
    def load_model(self, force_reload: bool = False) -> bool:
        """
        Charge le modèle ONNX en mémoire
        
        Args:
            force_reload: Force le rechargement même si déjà chargé
            
        Returns:
            True si chargement réussi
        """
        if self.is_loaded and not force_reload:
            logger.info("Modèle déjà chargé")
            return True
        
        try:
            # Vérifier que le modèle chiffré existe
            model_decryptor = get_model_decryptor()
            if not model_decryptor.encrypted_model_path.exists():
                logger.error(f"Modèle chiffré introuvable: {model_decryptor.encrypted_model_path}")
                return False
            
            # Vérifier les autorisations
            quota_manager = get_quota_manager()
            auth_manager = get_auth_manager()
            
            is_premium = auth_manager.is_premium()
            has_quota = quota_manager.can_analyze()
            
            if not (is_premium or has_quota):
                logger.error("Chargement du modèle refusé: quota épuisé et pas premium")
                return False
            
            # Déchiffrer le modèle
            model_data = model_decryptor.get_model_in_memory(is_premium, has_quota)
            
            if model_data is None:
                logger.error("Échec du déchiffrement du modèle")
                return False
            
            # Charger le modèle en mémoire
            logger.info("Chargement du modèle ONNX...")
            
            # Configurer les providers (GPU si disponible, sinon CPU)
            providers = ['CPUExecutionProvider']
            if 'CUDAExecutionProvider' in ort.get_available_providers():
                providers.insert(0, 'CUDAExecutionProvider')
                logger.info("GPU CUDA détecté, utilisation du GPU")
            
            self.session = ort.InferenceSession(
                model_data,
                providers=providers
            )
            
            # Récupérer les métadonnées du modèle
            self.input_name = self.session.get_inputs()[0].name
            self.output_names = [output.name for output in self.session.get_outputs()]
            self.input_shape = self.session.get_inputs()[0].shape
            
            self.is_loaded = True
            logger.info(f"Modèle chargé avec succès. Input: {self.input_name}, Shape: {self.input_shape}")
            
            return True
            
        except Exception as e:
            logger.error(f"Erreur lors du chargement du modèle: {e}")
            self.is_loaded = False
            return False
    
    def preprocess_image(self, image_path: Path) -> Optional[np.ndarray]:
        """
        Prétraite une image pour l'inférence
        
        Args:
            image_path: Chemin de l'image
            
        Returns:
            Tensor numpy prétraité ou None si erreur
        """
        try:
            # Charger l'image
            image = Image.open(image_path)
            
            # Convertir en RGB si nécessaire
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Redimensionner selon la forme d'entrée du modèle
            # Par défaut: 224x224 pour la plupart des modèles de vision
            target_size = (224, 224)
            if self.input_shape and len(self.input_shape) >= 3:
                # Format typique: [batch, channels, height, width] ou [batch, height, width, channels]
                if self.input_shape[1] in [1, 3]:  # Channels first
                    target_size = (self.input_shape[2], self.input_shape[3])
                else:  # Channels last
                    target_size = (self.input_shape[1], self.input_shape[2])
            
            image = image.resize(target_size, Image.Resampling.LANCZOS)
            
            # Convertir en array numpy
            img_array = np.array(image, dtype=np.float32)
            
            # Normaliser (0-255 -> 0-1)
            img_array = img_array / 255.0
            
            # Ajouter la dimension batch et réorganiser (HWC -> CHW)
            if len(img_array.shape) == 3:
                img_array = np.transpose(img_array, (2, 0, 1))  # HWC -> CHW
            
            img_array = np.expand_dims(img_array, axis=0)  # Ajouter batch dimension
            
            logger.info(f"Image prétraitée: {img_array.shape}")
            return img_array
            
        except Exception as e:
            logger.error(f"Erreur lors du prétraitement: {e}")
            return None
    
    def predict(self, image_path: Path) -> Optional[Dict]:
        """
        Effectue une prédiction sur une image
        
        Args:
            image_path: Chemin de l'image à analyser
            
        Returns:
            Dictionnaire avec les résultats ou None si erreur
        """
        import time
        start_time = time.time()
        
        try:
            # FILTRAGE D'IMAGE - Vérifier si l'image est relative au cancer du sein
            image_filter = get_image_filter()
            filter_result = image_filter.filter_image(image_path)
            
            if not filter_result["accepted"]:
                logger.warning(f"Image rejetée par le filtre: {filter_result['reason']}")
                return {
                    "error": True,
                    "message": f"Image rejetée: {filter_result['reason']}",
                    "filter_result": filter_result,
                    "prediction": None
                }
            
            logger.info(f"Image acceptée par le filtre: {filter_result.get('category_name', 'Filtrage désactivé')} ({filter_result['confidence']:.2f}%)")
            # Vérifier que le modèle chiffré existe
            model_decryptor = get_model_decryptor()
            if not model_decryptor.encrypted_model_path.exists():
                logger.error(f"❌ Modèle ONNX introuvable: {model_decryptor.encrypted_model_path}")
                raise FileNotFoundError(
                    f"Modèle ONNX chiffré introuvable.\n\n"
                    f"Veuillez placer votre modèle dans:\n"
                    f"{model_decryptor.encrypted_model_path}\n\n"
                    f"Ou chiffrez votre modèle avec:\n"
                    f"python scripts/encrypt_model.py"
                )
            
            # Charger le modèle si nécessaire
            if not self.is_loaded:
                if not self.load_model():
                    return None
            
            # Prétraiter l'image
            input_tensor = self.preprocess_image(image_path)
            if input_tensor is None:
                return None
            
            # Effectuer l'inférence
            inference_start = time.time()
            logger.info("Exécution de l'inférence...")
            outputs = self.session.run(
                self.output_names,
                {self.input_name: input_tensor}
            )
            inference_time = (time.time() - inference_start) * 1000  # En millisecondes
            logger.info(f"Temps d'inférence: {inference_time:.2f} ms")
            
            # Traiter les résultats
            # Format typique: [batch, num_classes]
            logits = outputs[0][0]  # Première sortie, premier batch
            
            # Log des valeurs brutes du modèle (preuve qu'il est utilisé)
            logger.info(f"Logits bruts du modèle: {logits}")
            
            # Appliquer softmax pour obtenir des probabilités
            exp_logits = np.exp(logits - np.max(logits))  # Stabilité numérique
            probabilities = exp_logits / np.sum(exp_logits)
            
            logger.info(f"Probabilités après softmax: {probabilities}")
            
            # Noms des classes
            if len(probabilities) == 2:
                class_names = ["Bénin", "Malin"]
            elif len(probabilities) == 3:
                class_names = ["Bénin", "Malin", "Normal"]
            else:
                class_names = [f"Classe {i}" for i in range(len(probabilities))]
            
            # Trouver la classe prédite
            class_id = int(np.argmax(probabilities))
            prediction_name = class_names[class_id]
            confidence = float(probabilities[class_id])
            
            # Créer le résultat
            result = {
                "prediction": prediction_name,
                "confidence": confidence * 100,
                "class_id": class_id,
                "probabilities": {
                    name: float(prob) * 100 
                    for name, prob in zip(class_names, probabilities)
                }
            }
            
            # Calculer le risque si on a bénin/malin
            if len(probabilities) >= 2:
                malignant_prob = float(probabilities[1])  # Index 1 = Malin
                result["risk_level"] = self._calculate_risk_level(malignant_prob)
            
            total_time = (time.time() - start_time) * 1000  # En millisecondes
            
            logger.info(f"Prédiction: {result['prediction']} ({result['confidence']:.2f}%)")
            logger.info(f"Temps total: {total_time:.2f} ms (inférence: {inference_time:.2f} ms)")
            
            # Incrémenter le compteur d'utilisation
            quota_manager = get_quota_manager()
            quota_manager.increment_usage()
            
            return result
            
        except Exception as e:
            logger.error(f"Erreur lors de la prédiction: {e}")
            return None
    
    def _calculate_risk_level(self, malignant_probability: float) -> str:
        """
        Calcule le niveau de risque basé sur la probabilité
        
        Args:
            malignant_probability: Probabilité de malignité (0-1)
            
        Returns:
            Niveau de risque: "Faible", "Modéré", "Élevé"
        """
        if malignant_probability < 0.3:
            return "Faible"
        elif malignant_probability < 0.7:
            return "Modéré"
        else:
            return "Élevé"
    
    def unload_model(self):
        """Décharge le modèle de la mémoire"""
        self.session = None
        self.is_loaded = False
        logger.info("Modèle déchargé de la mémoire")
    
    def get_model_info(self) -> Dict:
        """
        Retourne les informations sur le modèle
        
        Returns:
            Dictionnaire avec les métadonnées du modèle
        """
        if not self.is_loaded:
            return {"loaded": False}
        
        return {
            "loaded": True,
            "input_name": self.input_name,
            "input_shape": self.input_shape,
            "output_names": self.output_names,
            "providers": self.session.get_providers() if self.session else []
        }


# Singleton global
_inference_engine_instance: Optional[InferenceEngine] = None


def get_inference_engine() -> InferenceEngine:
    """Retourne l'instance singleton du moteur d'inférence"""
    global _inference_engine_instance
    if _inference_engine_instance is None:
        _inference_engine_instance = InferenceEngine()
    return _inference_engine_instance

