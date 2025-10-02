# 🧪 TEST UPLOAD ET LAYOUT

## ✅ Corrections Appliquées

### 🖥️ Desktop - Espacement des blocs
- ✅ Marges réduites : 20px (au lieu de 32px)
- ✅ Espacement entre blocs : 15-20px
- ✅ Padding cards : 15px (au lieu de 25px)
- ✅ Margin ajoutée aux cards : 5px
- ✅ Stats cards : padding 12px + margin 3px

### 🌐 Web - Upload réécrit complètement
- ✅ JavaScript réécrit from scratch
- ✅ Event listeners séparés (browseBtn + uploadZone)
- ✅ Console.log ajoutés pour debug
- ✅ Gestion d'erreurs améliorée
- ✅ Preview image avec max-width/max-height

---

## 🚀 TEST IMMÉDIAT

### Version Web (à tester EN PREMIER)

Le serveur tourne déjà ! Ouvrez :

```
http://localhost:8000
```

#### Test de l'upload :

1. **Ouvrez la console du navigateur** (F12)
   - Vous devriez voir les logs

2. **Cliquez sur la zone bleue** "Cliquez pour sélectionner"
   - Ça devrait ouvrir le dialogue de fichier
   - La console devrait afficher: "Fichier sélectionné: ..."

3. **OU cliquez sur le bouton "📂 Parcourir"**
   - Même chose

4. **Sélectionnez une image JPG ou PNG**
   - L'image devrait apparaître en preview
   - La console affiche: "Image chargée"
   - Le bouton "🔬 ANALYSER" devrait s'activer

5. **Cliquez sur "🔬 ANALYSER"**
   - Console: "Début de l'analyse..."
   - Console: "Envoi de la requête..."
   - Console: "Réponse reçue: 200"
   - Console: "Résultat: {..."
   - Résultats affichés avec couleurs

#### Si ça ne marche toujours PAS :

Regardez la **console (F12)** et dites-moi EXACTEMENT les erreurs !

---

### Version Desktop

```bash
python main.py
```

#### Vérification du layout :

1. **Les blocs doivent être espacés**
   - Header en haut (ne touche pas les stats)
   - Stats cards espacées horizontalement (gaps visibles)
   - Cards principale/résultats espacées (gap visible)

2. **Pas de superposition**
   - Aucun texte ne doit couper sur un autre
   - Les bordures doivent être visibles entre les blocs

3. **Test upload desktop** :
   - Clic sur "📂 Parcourir"
   - Sélectionner image
   - Image s'affiche (max 400x400)
   - Clic "🔬 ANALYSER"
   - Résultats

---

## 📊 Checklist Debug

### Web Upload NE FONCTIONNE PAS ?

Ouvrez F12 → Console et cherchez :

- ❌ `Uncaught ReferenceError` → Erreur JavaScript
- ❌ `Failed to fetch` → Problème serveur
- ❌ `404` ou `500` → Vérifier endpoint `/predict`
- ❌ `CORS error` → Redémarrer serveur

**Logs attendus** (si tout va bien) :
```
Fichier sélectionné: image.jpg
Image chargée
Début de l'analyse...
Envoi de la requête...
Réponse reçue: 200
Résultat: {prediction: "...", confidence: ...}
```

### Desktop Layout Problème ?

Si les blocs se touchent encore :

**Solution 1** : Augmenter les marges
```python
# src/ui/modern_main_window.py ligne 82
main_layout.setContentsMargins(30, 30, 30, 30)  # Au lieu de 20
```

**Solution 2** : Ajouter plus d'espace entre blocs
```python
# ligne 81
main_layout.setSpacing(25)  # Au lieu de 15
```

**Solution 3** : Vérifier la résolution écran
```python
# Afficher les dimensions
print(f"Écran: {self.screen().size()}")
```

Si écran < 1200px width → Ajuster la fenêtre :
```python
self.setMinimumSize(1000, 600)  # Encore plus compact
```

---

## 🎯 À FAIRE MAINTENANT

1. **TEST WEB** : Ouvrez http://localhost:8000
   - Appuyez sur F12 (console)
   - Essayez d'uploader une image
   - Copiez TOUS les messages de la console et dites-moi

2. **TEST DESKTOP** : Lance `python main.py`
   - Fais une capture d'écran si les blocs se touchent
   - Dis-moi quels blocs se superposent

---

## 🔧 Si RIEN ne marche

### Upload Web cassé ?
Retour à une version ULTRA simple :

```html
<input type="file" id="file" accept="image/*">
<button onclick="upload()">Envoyer</button>

<script>
function upload() {
    const file = document.getElementById('file').files[0];
    const formData = new FormData();
    formData.append('file', file);
    fetch('/predict', {method: 'POST', body: formData})
        .then(r => r.json())
        .then(console.log);
}
</script>
```

### Layout Desktop cassé ?
Interface ULTRA minimaliste sans design :

```python
# Dans main_window.py
self.setStyleSheet("")  # Supprimer TOUS les styles
```

---

**🚨 TESTE MAINTENANT et dis-moi ce que tu vois dans la console F12 !** 🚨

