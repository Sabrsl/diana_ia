"""
DIANA - Filtre d'images médicales
Vérifie si les images sont relatives au cancer du sein avant analyse
"""

import logging
import io
from pathlib import Path
from typing import Optional, Dict, Tuple
import numpy as np
from PIL import Image
import onnxruntime as ort

import config

logger = logging.getLogger(__name__)


class ImageFilter:
    """Filtre d'images pour vérifier la pertinence médicale"""
    
    def __init__(self):
        self.session: Optional[ort.InferenceSession] = None
        self.input_name: Optional[str] = None
        self.output_names: Optional[list] = None
        self.input_shape: Optional[Tuple] = None
        self.is_loaded = False
        self.model_path = config.FILTER_MODEL_PATH
    
    def load_model(self, force_reload: bool = False) -> bool:
        """
        Charge le modèle de filtrage ONNX
        
        Args:
            force_reload: Force le rechargement même si déjà chargé
            
        Returns:
            True si chargement réussi
        """
        if self.is_loaded and not force_reload:
            logger.info("Modèle de filtrage déjà chargé")
            return True
        
        try:
            # Vérifier que le modèle existe
            if not self.model_path.exists():
                logger.warning(f"Modèle de filtrage introuvable: {self.model_path}")
                logger.warning("Le filtrage sera désactivé - toutes les images seront acceptées")
                return False
            
            # Charger le modèle ONNX
            logger.info("Chargement du modèle de filtrage ONNX...")
            
            # Configurer les providers (GPU si disponible, sinon CPU)
            providers = ['CPUExecutionProvider']
            if 'CUDAExecutionProvider' in ort.get_available_providers():
                providers.insert(0, 'CUDAExecutionProvider')
                logger.info("GPU CUDA détecté pour le filtrage")
            
            self.session = ort.InferenceSession(
                str(self.model_path),
                providers=providers
            )
            
            # Récupérer les métadonnées du modèle
            self.input_name = self.session.get_inputs()[0].name
            self.output_names = [output.name for output in self.session.get_outputs()]
            self.input_shape = self.session.get_inputs()[0].shape
            
            self.is_loaded = True
            logger.info(f"Modèle de filtrage chargé: {self.input_name}, Shape: {self.input_shape}")
            
            return True
            
        except Exception as e:
            logger.error(f"Erreur lors du chargement du modèle de filtrage: {e}")
            self.is_loaded = False
            return False
    
    def preprocess_image(self, image_path: Path) -> Optional[np.ndarray]:
        """
        Prétraite une image pour le filtrage
        
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
            
            # Redimensionner à 224x224 (standard pour les modèles de vision)
            target_size = (224, 224)
            if self.input_shape and len(self.input_shape) >= 3:
                # Adapter selon la forme d'entrée du modèle
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
            
            logger.debug(f"Image prétraitée pour filtrage: {img_array.shape}")
            return img_array
            
        except Exception as e:
            logger.error(f"Erreur lors du prétraitement pour filtrage: {e}")
            return None
    
    def filter_image(self, image_path: Path) -> Dict:
        """
        Filtre une image pour vérifier si elle est relative au cancer du sein
        
        Args:
            image_path: Chemin de l'image à filtrer
            
        Returns:
            Dictionnaire avec le résultat du filtrage
        """
        try:
            # Si le modèle n'est pas chargé, accepter toutes les images
            if not self.is_loaded:
                logger.warning("Modèle de filtrage non disponible - image acceptée par défaut")
                return {
                    "accepted": True,
                    "reason": "Filtrage désactivé",
                    "confidence": 1.0,
                    "category": "unknown",
                    "category_name": "Filtrage désactivé"
                }
            
            # Prétraiter l'image
            input_tensor = self.preprocess_image(image_path)
            if input_tensor is None:
                return {
                    "accepted": False,
                    "reason": "Erreur de prétraitement",
                    "confidence": 0.0,
                    "category": "error"
                }
            
            # Effectuer l'inférence de filtrage
            logger.info("Exécution du filtrage d'image...")
            outputs = self.session.run(
                self.output_names,
                {self.input_name: input_tensor}
            )
            
            # Traiter les résultats
            logits = outputs[0][0]  # Première sortie, premier batch
            
            # Appliquer softmax pour obtenir des probabilités
            exp_logits = np.exp(logits - np.max(logits))  # Stabilité numérique
            probabilities = exp_logits / np.sum(exp_logits)
            
            logger.info(f"Probabilités de filtrage: {probabilities}")
            
            # Classes de filtrage - Vérifier l'ordre
            categories = ["non_medical", "medical_other", "breast_cancer"]
            category_names = ["Non-médical", "Médical autre", "Cancer du sein"]
            
            # Debug : Afficher les probabilités par classe
            logger.info(f"Probabilités par classe:")
            for i, (cat, name) in enumerate(zip(categories, category_names)):
                logger.info(f"  {name}: {probabilities[i]*100:.2f}%")
            
            # Trouver la catégorie prédite
            category_id = int(np.argmax(probabilities))
            category = categories[category_id]
            category_name = category_names[category_id]
            confidence = float(probabilities[category_id])
            
            # Déterminer si l'image est acceptée
            # Seules les images de cancer du sein sont acceptées
            # Ajuster le seuil de confiance pour être plus permissif
            accepted = (category == "breast_cancer") or (category == "medical_other" and confidence > 0.3)
            
            # Messages selon la catégorie
            if category == "non_medical":
                reason = "Image non-médicale détectée. Veuillez uploader une image médicale (mammographie, échographie mammaire, etc.)"
            elif category == "medical_other":
                reason = "Image médicale détectée mais non relative au cancer du sein. Veuillez uploader une image de mammographie ou d'échographie mammaire"
            else:  # breast_cancer
                reason = "Image relative au cancer du sein détectée"
            
            result = {
                "accepted": accepted,
                "reason": reason,
                "confidence": confidence * 100,
                "category": category,
                "category_name": category_name,
                "probabilities": {
                    name: float(prob) * 100 
                    for name, prob in zip(category_names, probabilities)
                }
            }
            
            logger.info(f"Filtrage: {category_name} ({confidence*100:.2f}%) - {'Accepté' if accepted else 'Rejeté'}")
            
            return result
            
        except Exception as e:
            logger.error(f"Erreur lors du filtrage: {e}")
            return {
                "accepted": False,
                "reason": f"Erreur de filtrage: {str(e)}",
                "confidence": 0.0,
                "category": "error"
            }
    
    def unload_model(self):
        """Décharge le modèle de filtrage de la mémoire"""
        self.session = None
        self.is_loaded = False
        logger.info("Modèle de filtrage déchargé")
    
    def get_model_info(self) -> Dict:
        """
        Retourne les informations sur le modèle de filtrage
        
        Returns:
            Dictionnaire avec les métadonnées du modèle
        """
        if not self.is_loaded:
            return {
                "loaded": False,
                "model_path": str(self.model_path),
                "model_exists": self.model_path.exists()
            }
        
        return {
            "loaded": True,
            "model_path": str(self.model_path),
            "model_exists": self.model_path.exists(),
            "input_name": self.input_name,
            "input_shape": self.input_shape,
            "output_names": self.output_names,
            "providers": self.session.get_providers() if self.session else []
        }


# Singleton global
_image_filter_instance: Optional[ImageFilter] = None


def get_image_filter() -> ImageFilter:
    """Retourne l'instance singleton du filtre d'images"""
    global _image_filter_instance
    if _image_filter_instance is None:
        _image_filter_instance = ImageFilter()
    return _image_filter_instance
