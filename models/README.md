# Modèles DIANA

Ce dossier contient les modèles d'intelligence artificielle utilisés par DIANA.

## 📁 Structure

```
models/
├── breast_cancer_model.onnx.enc  # Modèle chiffré (production)
├── breast_cancer_model.onnx      # Modèle déchiffré (ne pas commiter!)
└── README.md                      # Ce fichier
```

## 🔐 Sécurité

⚠️ **IMPORTANT** : Seuls les modèles chiffrés (`.onnx.enc`) doivent être versionnés dans Git.

Les fichiers `.onnx` déchiffrés sont :
- Automatiquement ignorés par `.gitignore`
- Générés à la volée lors de l'exécution
- Supprimés après utilisation (mode mémoire)

## 📝 Format du modèle

### Spécifications requises

Le modèle ONNX doit respecter :

**Input:**
- Format : `float32[batch, channels, height, width]`
- Taille recommandée : `[1, 3, 224, 224]`
- Normalisation : valeurs entre 0 et 1

**Output:**
- Format : `float32[batch, num_classes]`
- Classes : 2 (bénin, malin) ou plus
- Valeurs : probabilités (softmax ou sigmoid)

### Exemple de structure

```
Input: "input" (1x3x224x224)
  ↓
Conv2D + BatchNorm + ReLU
  ↓
MaxPool
  ↓
... (ResNet, VGG, EfficientNet, etc.)
  ↓
GlobalAveragePool
  ↓
Dense Layer
  ↓
Softmax
  ↓
Output: "output" (1x2)
```

## 🔄 Workflow

### 1. Entraînement du modèle

```python
# Avec PyTorch
import torch
import torch.onnx

# Votre modèle entraîné
model = YourTrainedModel()
model.eval()

# Export ONNX
dummy_input = torch.randn(1, 3, 224, 224)
torch.onnx.export(
    model,
    dummy_input,
    "models/breast_cancer_model.onnx",
    export_params=True,
    opset_version=14,
    do_constant_folding=True,
    input_names=['input'],
    output_names=['output'],
    dynamic_axes={
        'input': {0: 'batch_size'},
        'output': {0: 'batch_size'}
    }
)
```

### 2. Validation du modèle

```python
import onnxruntime as ort
import numpy as np

# Charger le modèle
session = ort.InferenceSession("models/breast_cancer_model.onnx")

# Tester
input_data = np.random.randn(1, 3, 224, 224).astype(np.float32)
outputs = session.run(None, {'input': input_data})
print(f"Output shape: {outputs[0].shape}")
print(f"Probabilities: {outputs[0]}")
```

### 3. Chiffrement

```bash
python scripts/encrypt_model.py
```

### 4. Déploiement

Le modèle chiffré `.onnx.enc` peut être :
- Versionné dans Git
- Distribué avec l'application
- Mis à jour via le système d'update

## 🧪 Modèle de test (dummy)

Pour le développement sans modèle réel :

```python
# scripts/create_dummy_model.py
import torch
import torch.nn as nn

class DummyBreastCancerModel(nn.Module):
    """Modèle dummy pour tests"""
    
    def __init__(self):
        super().__init__()
        self.features = nn.Sequential(
            nn.Conv2d(3, 64, 7, stride=2, padding=3),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(3, stride=2, padding=1),
            nn.AdaptiveAvgPool2d((1, 1))
        )
        self.classifier = nn.Sequential(
            nn.Flatten(),
            nn.Linear(64, 2),
            nn.Softmax(dim=1)
        )
    
    def forward(self, x):
        x = self.features(x)
        x = self.classifier(x)
        return x

# Créer et exporter
model = DummyBreastCancerModel()
model.eval()

dummy_input = torch.randn(1, 3, 224, 224)
torch.onnx.export(
    model,
    dummy_input,
    "models/breast_cancer_model.onnx",
    input_names=['input'],
    output_names=['output'],
    opset_version=14
)

print("✅ Modèle dummy créé : models/breast_cancer_model.onnx")
```

## 📊 Performance

### Benchmarks recommandés

Pour un modèle de production :

- **Accuracy** : > 90% sur validation set
- **Sensitivity (Recall)** : > 95% (crucial en médical)
- **Specificity** : > 85%
- **AUC-ROC** : > 0.95
- **Latence** : < 2 secondes sur CPU
- **Taille** : < 100 MB pour faciliter la distribution

### Optimisations

```python
# Quantization pour réduire la taille
import onnxruntime as ort
from onnxruntime.quantization import quantize_dynamic

quantize_dynamic(
    "breast_cancer_model.onnx",
    "breast_cancer_model_quantized.onnx",
    weight_type=QuantType.QUInt8
)
```

## 🔬 Datasets recommandés

Pour l'entraînement :

- **CBIS-DDSM** : Mammographies annotées
- **INbreast** : Base portugaise de mammographies
- **MIAS** : Mammography Image Analysis Society
- **Private hospital data** : Avec autorisation éthique

## ⚠️ Considérations médicales

### Disclaimer obligatoire

Le modèle est un **outil d'aide au diagnostic** :
- Ne remplace PAS un médecin
- Doit être validé cliniquement
- Nécessite une certification médicale pour usage clinique
- Doit respecter les normes (CE, FDA, etc.)

### Validation clinique

Avant déploiement en production :
1. ✅ Validation sur dataset indépendant
2. ✅ Revue par des radiologues
3. ✅ Tests en conditions réelles
4. ✅ Conformité RGPD/HIPAA
5. ✅ Certification médicale (si applicable)

## 📚 Ressources

- [ONNX Documentation](https://onnx.ai/)
- [ONNX Runtime](https://onnxruntime.ai/)
- [PyTorch to ONNX](https://pytorch.org/docs/stable/onnx.html)
- [TensorFlow to ONNX](https://github.com/onnx/tensorflow-onnx)

## 🆘 Support

Pour des questions sur les modèles :
- Email : ml@diana-ai.com
- Slack : #diana-ml

---

**Note** : Ce dossier est critique pour le fonctionnement de l'application. Ne supprimez pas les fichiers `.onnx.enc` !

