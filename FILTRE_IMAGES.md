# 🔍 Système de Filtrage d'Images - DIANA

## Vue d'ensemble

Le système de filtrage d'images DIANA vérifie automatiquement si les images uploadées sont relatives au cancer du sein avant de les passer au modèle principal. Cela évite les analyses inutiles et améliore la qualité des résultats.

## 🏗️ Architecture

```
Image Upload → Filtre ONNX → Modèle Principal → Résultat
     ↓              ↓
   Rejeté      Accepté
```

## 📁 Structure des fichiers

```
models/filter/
├── breast_cancer_filter.onnx    # Modèle de filtrage (à ajouter)
└── README.md                    # Documentation du modèle

src/
├── image_filter.py              # Moteur de filtrage
└── inference_engine.py          # Intégration du filtrage
```

## 🎯 Classes de filtrage

Le modèle de filtrage doit classifier les images en 3 catégories :

| Classe | ID | Description | Action |
|--------|----|--------------|---------|
| **Non-médical** | 0 | Images non-médicales (photos, dessins, etc.) | ❌ Rejeté |
| **Médical autre** | 1 | Images médicales non relatives au cancer du sein | ❌ Rejeté |
| **Cancer du sein** | 2 | Images de mammographies, échographies, etc. | ✅ Accepté |

## 🚀 Installation

### 1. Placer le modèle de filtrage

Placez votre modèle ONNX dans le dossier :
```
models/filter/breast_cancer_filter.onnx
```

### 2. Format du modèle attendu

- **Entrée** : Image RGB 224x224 pixels, normalisée (0-1)
- **Sortie** : Logits pour 3 classes [non_medical, medical_other, breast_cancer]
- **Format** : ONNX standard

### 3. Vérification

Lancez le script de test :
```bash
python scripts/init_filter.py
```

## 🔧 Utilisation

### Application Desktop

Le filtrage est automatiquement intégré dans l'application PyQt6. Aucune action supplémentaire requise.

### API Web

Le filtrage est automatiquement intégré dans l'API FastAPI. Vérifiez le statut :

```bash
curl http://localhost:8000/api/filter/status
```

### Messages d'erreur

Lorsqu'une image est rejetée, l'API retourne :

```json
{
  "error": "Image rejetée",
  "message": "Image non-médicale détectée",
  "filter_result": {
    "accepted": false,
    "reason": "Image non-médicale détectée",
    "confidence": 85.2,
    "category": "non_medical",
    "category_name": "Non-médical"
  }
}
```

## 📊 Monitoring

### Statut du filtre

```bash
# Vérifier si le filtre est actif
GET /api/filter/status
```

Réponse :
```json
{
  "filter_loaded": true,
  "model_exists": true,
  "model_path": "models/filter/breast_cancer_filter.onnx",
  "message": "Filtre actif"
}
```

### Logs

Le système log automatiquement :
- ✅ Images acceptées avec leur catégorie
- ❌ Images rejetées avec la raison
- ⚠️ Erreurs de filtrage

## 🔧 Configuration

### Désactiver le filtrage

Si le modèle de filtrage n'est pas disponible, le système accepte automatiquement toutes les images avec un avertissement dans les logs.

### Personnaliser le seuil

Modifiez `src/image_filter.py` pour ajuster les seuils de confiance si nécessaire.

## 🧪 Tests

### Test manuel

1. Uploadez une image non-médicale → Doit être rejetée
2. Uploadez une image médicale autre → Doit être rejetée  
3. Uploadez une mammographie → Doit être acceptée

### Test automatique

```bash
python -m pytest tests/test_image_filter.py
```

## 🚨 Dépannage

### Le filtre ne se charge pas

1. Vérifiez que le fichier existe : `models/filter/breast_cancer_filter.onnx`
2. Vérifiez les permissions de lecture
3. Consultez les logs pour les erreurs détaillées

### Images toujours acceptées

- Le modèle de filtrage n'est pas chargé
- Vérifiez le statut avec `/api/filter/status`

### Erreurs de prédiction

- Vérifiez le format du modèle ONNX
- Assurez-vous que le modèle accepte des images 224x224 RGB

## 📈 Performance

- **Temps de filtrage** : ~50-100ms par image
- **Mémoire** : ~50-100MB pour le modèle
- **GPU** : Support automatique si CUDA disponible

## 🔒 Sécurité

- Le modèle de filtrage est chargé en mémoire
- Aucune donnée sensible n'est stockée
- Les images rejetées ne sont pas sauvegardées
