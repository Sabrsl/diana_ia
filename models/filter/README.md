# Modèle de Filtrage d'Images

Ce dossier contient le modèle ONNX de filtrage pour vérifier si les images sont relatives au cancer du sein.

## Structure attendue

```
models/filter/
├── breast_cancer_filter.onnx    # Modèle de filtrage ONNX
└── README.md                    # Ce fichier
```

## Utilisation

Le modèle de filtrage sera automatiquement chargé par le système pour vérifier les images avant de les passer au modèle principal.

### Classes de sortie attendues

- **0**: Non-médical (image rejetée)
- **1**: Médical autre (image rejetée) 
- **2**: Cancer du sein (image acceptée)

### Format d'entrée

- Taille d'image: 224x224 pixels
- Format: RGB
- Normalisation: 0-1 (valeurs divisées par 255)

## Installation

1. Placez votre modèle `breast_cancer_filter.onnx` dans ce dossier
2. Le système le détectera automatiquement au prochain démarrage
