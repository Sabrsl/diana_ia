# 🎯 Démonstration du Système de Filtrage DIANA

## Vue d'ensemble

Ce guide vous montre comment utiliser le nouveau système de filtrage d'images intégré à DIANA.

## 🚀 Démarrage rapide

### 1. Créer un modèle de test (optionnel)

Pour tester le système sans votre vrai modèle :

```bash
python scripts/create_dummy_filter.py
```

### 2. Tester le système

```bash
python scripts/test_filter.py
```

### 3. Lancer l'application

```bash
# Application desktop
python main.py

# Ou serveur web
python web_app.py
```

## 📋 Fonctionnement

### Pipeline de traitement

```
Image Upload
     ↓
🔍 Filtre ONNX
     ↓
✅ Accepté → 🧠 Modèle Principal → 📊 Résultat
     ↓
❌ Rejeté → 🚫 Message d'erreur
```

### Types d'images

| Type | Exemple | Action |
|------|---------|--------|
| **Non-médical** | Photo, dessin, graphique | ❌ Rejeté |
| **Médical autre** | Radiographie, IRM, scanner | ❌ Rejeté |
| **Cancer du sein** | Mammographie, échographie mammaire | ✅ Accepté |

## 🧪 Tests

### Test automatique

```bash
python scripts/test_filter.py
```

Résultat attendu :
```
🧪 DIANA - Test du Système de Filtrage
============================================================
📁 Modèle: models/filter/breast_cancer_filter.onnx
📊 Existe: True
🔄 Chargé: True

🔍 Test: non_medical
   Résultat: ❌ Rejeté
   Catégorie: Non-médical
   Confiance: 85.2%
   Raison: Image non-médicale détectée

🔍 Test: medical_other
   Résultat: ❌ Rejeté
   Catégorie: Médical autre
   Confiance: 78.1%
   Raison: Image médicale non relative au cancer du sein

🔍 Test: breast_cancer
   Résultat: ✅ Accepté
   Catégorie: Cancer du sein
   Confiance: 92.3%
   Raison: Image relative au cancer du sein

📊 RÉSUMÉ DES TESTS
============================================================
✅ PASS non_medical: Non-médical (85.2%)
✅ PASS medical_other: Médical autre (78.1%)
✅ PASS breast_cancer: Cancer du sein (92.3%)
```

### Test via API

```bash
# Vérifier le statut du filtre
curl http://localhost:8000/api/filter/status

# Tester avec une image
curl -X POST -F "file=@test_image.jpg" http://localhost:8000/predict
```

## 🔧 Configuration

### Placer votre modèle

1. Entraînez votre modèle de filtrage avec 3 classes :
   - Classe 0 : Non-médical
   - Classe 1 : Médical autre  
   - Classe 2 : Cancer du sein

2. Exportez-le au format ONNX

3. Placez-le dans : `models/filter/breast_cancer_filter.onnx`

### Format attendu

- **Entrée** : `[batch, 3, 224, 224]` (RGB, 224x224)
- **Sortie** : `[batch, 3]` (logits pour 3 classes)
- **Normalisation** : Valeurs 0-1 (divisées par 255)

## 📊 Monitoring

### Logs de l'application

```
2024-01-15 10:30:15 - src.image_filter - INFO - Image acceptée par le filtre: Cancer du sein (92.30%)
2024-01-15 10:31:22 - src.image_filter - WARNING - Image rejetée par le filtre: Image non-médicale détectée
```

### API de statut

```json
{
  "filter_loaded": true,
  "model_exists": true,
  "model_path": "models/filter/breast_cancer_filter.onnx",
  "message": "Filtre actif"
}
```

## 🚨 Messages d'erreur

### Image rejetée

```json
{
  "error": "Image rejetée",
  "message": "Image non-médicale détectée",
  "filter_result": {
    "accepted": false,
    "reason": "Image non-médicale détectée",
    "confidence": 85.2,
    "category": "non_medical",
    "category_name": "Non-médical",
    "probabilities": {
      "Non-médical": 85.2,
      "Médical autre": 12.1,
      "Cancer du sein": 2.7
    }
  }
}
```

## 🔍 Dépannage

### Le filtre ne se charge pas

1. Vérifiez que le fichier existe :
   ```bash
   ls -la models/filter/breast_cancer_filter.onnx
   ```

2. Vérifiez les permissions :
   ```bash
   chmod 644 models/filter/breast_cancer_filter.onnx
   ```

3. Consultez les logs :
   ```bash
   tail -f logs/diana.log
   ```

### Images toujours acceptées

- Le modèle de filtrage n'est pas chargé
- Vérifiez avec : `curl http://localhost:8000/api/filter/status`

### Erreurs de format

- Vérifiez que votre modèle accepte des images 224x224 RGB
- Assurez-vous que la sortie est bien [batch, 3]

## 📈 Performance

- **Temps de filtrage** : ~50-100ms
- **Mémoire** : ~50-100MB
- **GPU** : Support automatique si CUDA disponible

## 🔒 Sécurité

- Aucune donnée sensible stockée
- Images rejetées supprimées immédiatement
- Modèle chargé en mémoire uniquement

## 🎯 Prochaines étapes

1. **Entraînez votre modèle** avec vos données spécifiques
2. **Testez** avec des images réelles
3. **Ajustez** les seuils si nécessaire
4. **Déployez** en production

## 📞 Support

- Documentation : `FILTRE_IMAGES.md`
- Tests : `scripts/test_filter.py`
- Logs : `logs/diana.log`
