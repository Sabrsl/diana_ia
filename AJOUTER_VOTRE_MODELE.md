# 🤖 Comment ajouter VOTRE modèle ONNX à DIANA

## 🎯 Vue d'ensemble

DIANA utilise **VOTRE propre modèle ONNX** pour effectuer les analyses. Voici comment l'ajouter :

---

## 📋 Étapes simples

### 1️⃣ Préparez votre modèle ONNX

Vous devez avoir un fichier `.onnx` (par exemple : `mon_modele.onnx`)

**Format requis :**
- Extension : `.onnx`
- Input : `[batch, channels, height, width]` (ex: `[1, 3, 224, 224]`)
- Output : `[batch, num_classes]` (ex: `[1, 2]` pour bénin/malin)

### 2️⃣ Placez votre modèle

```
Copiez votre fichier dans le dossier models/ et renommez-le :

C:\Users\badza\Desktop\DIANA\models\breast_cancer_model.onnx
                                    ↑
                            Nom exact requis !
```

**Commande :**
```powershell
copy "C:\chemin\vers\mon_modele.onnx" "models\breast_cancer_model.onnx"
```

### 3️⃣ Chiffrez le modèle

Pour la sécurité, le modèle doit être chiffré :

```powershell
python scripts\encrypt_model.py
```

Le script va vous demander :
- ✅ Chemin du modèle : `models/breast_cancer_model.onnx`
- ✅ Chemin de sortie : (appuyez sur Entrée)
- ✅ Lancer le chiffrement : `o`

### 4️⃣ C'est prêt ! 🎉

Vous aurez maintenant :
```
models\
  ├── breast_cancer_model.onnx       ← Votre modèle original
  └── breast_cancer_model.onnx.enc   ← Version chiffrée (utilisée par DIANA)
```

**Lancez l'application :**
```powershell
python main.py
```

Ou pour la version web :
```powershell
python web_app.py
```

---

## ✅ Vérification

### Comment savoir si mon modèle fonctionne ?

1. **Au lancement**, les logs doivent afficher :
   ```
   ✅ Modèle chiffré détecté: models\breast_cancer_model.onnx.enc
   ```

2. **Dans l'interface**, le bouton "Analyser" doit fonctionner

3. **Les analyses** retournent des résultats cohérents

---

## 🔄 Changer de modèle

Pour utiliser un autre modèle :

```powershell
# 1. Remplacer le fichier
copy "C:\nouveau_modele.onnx" "models\breast_cancer_model.onnx"

# 2. Re-chiffrer
python scripts\encrypt_model.py

# 3. Relancer l'application
python main.py
```

---

## ⚠️ Si le modèle n'existe pas

### L'application va quand même s'ouvrir !

Mais quand vous essayez d'analyser une image, vous verrez :

```
╔═══════════════════════════════════════════════╗
║  ❌ Modèle ONNX chiffré introuvable          ║
╠═══════════════════════════════════════════════╣
║                                               ║
║  Veuillez placer votre modèle dans :         ║
║  models\breast_cancer_model.onnx.enc          ║
║                                               ║
║  Ou chiffrez votre modèle avec :             ║
║  python scripts\encrypt_model.py             ║
║                                               ║
╚═══════════════════════════════════════════════╝
```

**C'est normal !** Ajoutez simplement votre modèle et rechiffrez.

---

## 📊 Format détaillé du modèle

### Input attendu

```python
Shape : [batch_size, channels, height, width]
Type  : float32
Exemple : [1, 3, 224, 224]

Normalisation : valeurs entre 0 et 1
```

### Output attendu

**Classification binaire (bénin/malin) :**
```python
Shape : [batch_size, 2]
Type  : float32
Exemple : [1, 2]

Format : [probabilité_bénin, probabilité_malin]
Exemple : [0.94, 0.06] → 94% bénin, 6% malin
```

**Classification multi-classes :**
```python
Shape : [batch_size, num_classes]
Type  : float32

Le modèle retournera le résultat de la classe avec la plus haute probabilité
```

---

## 🧪 Tester votre modèle localement

Avant de l'ajouter à DIANA, testez-le :

```python
import onnxruntime as ort
import numpy as np

# Charger le modèle
session = ort.InferenceSession("models/breast_cancer_model.onnx")

# Vérifier les inputs/outputs
print("Input:", session.get_inputs()[0].name, session.get_inputs()[0].shape)
print("Output:", session.get_outputs()[0].name, session.get_outputs()[0].shape)

# Test avec données aléatoires
input_data = np.random.randn(1, 3, 224, 224).astype(np.float32)
output = session.run(None, {session.get_inputs()[0].name: input_data})
print("Résultat:", output[0])
```

Si ça fonctionne, votre modèle est compatible avec DIANA ! ✅

---

## 🔐 Pourquoi chiffrer le modèle ?

**Sécurité** : Le modèle est votre propriété intellectuelle
- ✅ Empêche la copie non autorisée
- ✅ Protège votre travail d'entraînement
- ✅ Permet la distribution sécurisée

**Comment ça marche** :
1. Le modèle `.onnx` est chiffré en `.onnx.enc` (AES-256)
2. Au runtime, DIANA le déchiffre **en mémoire uniquement**
3. Le modèle déchiffré n'est **jamais écrit sur le disque**
4. Impossible d'extraire le modèle de l'application

---

## 🚀 En production

Quand vous créez l'exécutable `DIANA.exe` :

```powershell
python scripts\build.py
```

Le fichier `.onnx.enc` est **automatiquement inclus** dans l'EXE.

Les utilisateurs finaux n'ont **jamais accès** au modèle non chiffré ! 🔒

---

## 💡 Astuces

### Vérifier que le modèle est bien chiffré

```powershell
# Fichier chiffré = impossible à lire
type models\breast_cancer_model.onnx.enc
# Devrait afficher des caractères illisibles

# Fichier original = lisible
type models\breast_cancer_model.onnx
# Devrait afficher "ONNX..." au début
```

### Taille du fichier

Le fichier `.onnx.enc` est légèrement plus grand que `.onnx` :
- Modèle : 50 MB → Chiffré : ~50.1 MB

### Performance

Le déchiffrement est **très rapide** (< 1 seconde même pour de gros modèles).

---

## 🆘 Problèmes courants

### ❌ "Cannot decrypt model"

**Solution :** La clé de chiffrement a changé ou le fichier est corrompu

```powershell
# Re-chiffrer avec la bonne clé
python scripts\encrypt_model.py
```

### ❌ "Invalid ONNX model"

**Solution :** Votre modèle n'est pas au format ONNX valide

```powershell
# Vérifier avec onnxruntime
python -c "import onnxruntime; onnxruntime.InferenceSession('models/breast_cancer_model.onnx')"
```

### ❌ "Input shape mismatch"

**Solution :** L'image est redimensionnée automatiquement, mais vérifiez les dimensions attendues

```python
# Voir dans les logs au lancement :
# "Input shape: [1, 3, 224, 224]"
```

---

## 📚 Ressources

- **ONNX Documentation** : https://onnx.ai/
- **ONNX Runtime** : https://onnxruntime.ai/
- **PyTorch → ONNX** : https://pytorch.org/docs/stable/onnx.html
- **TensorFlow → ONNX** : https://github.com/onnx/tensorflow-onnx

---

## ✅ Checklist finale

Avant de lancer DIANA en production :

- [ ] Votre modèle est au format `.onnx`
- [ ] Le modèle fonctionne avec ONNX Runtime
- [ ] Input shape : `[1, 3, H, W]` (H et W peuvent varier)
- [ ] Output shape : `[1, num_classes]`
- [ ] Le modèle est placé dans `models/breast_cancer_model.onnx`
- [ ] Le modèle est chiffré (fichier `.onnx.enc` existe)
- [ ] L'application se lance sans erreur
- [ ] Une analyse de test fonctionne
- [ ] Les résultats sont cohérents

**Si tout est ✅, vous êtes prêt ! 🎉**


