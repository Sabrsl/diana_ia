# 🧪 Test de l'Interface DIANA

## ✅ Corrections Effectuées

### Version Desktop (PyQt6)

**Problème** : Textes et boutons tronqués  
**Solution** : Réduction drastique de toutes les tailles de police

| Élément | Avant | Après |
|---------|-------|-------|
| Titre principal | 28px | 20px |
| Sous-titre | 13px | 11px |
| Sections | 16px | 14px |
| Boutons | 14px | 12px |
| Bouton ANALYSER | 14px | 13px |
| Stats valeur | 32px | 24px |
| Stats label | 11px | 10px |
| Header hauteur | 80px | 65px |
| Stats hauteur | 90px | 75px |

**Padding réduits** :
- Boutons : 8px 16px (au lieu de 12px 24px)
- Header : 20px (au lieu de 30px)
- Border radius : 8px (au lieu de 12px)

---

### Version Web (FastAPI)

**Problème** : Upload ne fonctionnait pas  
**Code vérifié** : Le JavaScript est correct

#### Comment tester l'upload web :

1. **Lancer le serveur** :
```bash
python web_app.py
```

2. **Ouvrir le navigateur** :
```
http://localhost:8000
```

3. **Test de l'upload** :
   - Cliquer sur la zone "📁 Cliquez pour sélectionner"
   - OU cliquer sur le bouton "📂 Parcourir"
   - Sélectionner une image (JPG, PNG, etc.)
   - L'image devrait s'afficher en preview
   - Le bouton "🔬 ANALYSER" devrait s'activer
   - Cliquer sur ANALYSER

4. **Vérifier** :
   - Un loader devrait apparaître
   - Les résultats devraient s'afficher avec :
     - Emoji (✅ Bénin, ⚠️ Malin, ℹ️ Normal)
     - Prédiction
     - Confiance en %
     - Barres de probabilités

---

## 🚀 Test de la Version Desktop

```bash
python main.py
```

### Ce qui devrait s'afficher :

1. **Header gradient violet** (65px de haut)
   - "🏥 DIANA" (20px)
   - "DIAGNOSTIC INTELLIGENT..." (11px)
   - Bouton "Se connecter Premium"

2. **3 Stats Cards** (75px de haut)
   - Analyses effectuées
   - Analyses restantes
   - Statut

3. **2 Panneaux côte à côte** :
   - **Gauche** : Upload d'image
     - Zone avec texte "Cliquez sur 'Parcourir'"
     - Bouton "📂 Parcourir" (12px)
     - Bouton "🔬 ANALYSER" (13px)
   
   - **Droite** : Résultats
     - "En attente d'analyse..."

### Test Upload Desktop :

1. Cliquer sur "📂 Parcourir"
2. Sélectionner une image
3. L'image devrait s'afficher (max 400x400px)
4. Bouton ANALYSER s'active
5. Cliquer sur ANALYSER
6. Résultats s'affichent avec :
   - Couleur de fond selon le diagnostic
   - Probabilités en barres HTML

---

## 🐛 Dépannage

### Si les textes sont ENCORE tronqués (Desktop) :

#### Option 1 : Augmenter la fenêtre
```python
# Dans src/ui/modern_main_window.py ligne 66
self.setMinimumSize(1400, 800)  # Au lieu de 1200x700
```

#### Option 2 : Supprimer les emojis des boutons
```python
# Ligne 236 et 241
select_btn = QPushButton("Parcourir")  # Sans 📂
self.analyze_btn = QPushButton("ANALYSER")  # Sans 🔬
```

#### Option 3 : Réduire encore les paddings
Dans `src/ui/modern_styles.py` :
```css
QPushButton {
    padding: 6px 12px;  /* Au lieu de 8px 16px */
    font-size: 11px;    /* Au lieu de 12px */
}
```

---

### Si l'upload web ne fonctionne PAS :

#### Vérifier 1 : Le serveur tourne
```bash
# Devrait afficher :
# ================================================================
# 🚀 DIANA - Serveur Web
# ================================================================
# 📱 Interface web : http://localhost:8000
```

#### Vérifier 2 : Le modèle est présent
```bash
ls models\breast_cancer_model.onnx.enc
```

Si absent :
```bash
python scripts\encrypt_model.py
```

#### Vérifier 3 : Console navigateur (F12)
- Ouvrir les DevTools (F12)
- Onglet Console
- Chercher des erreurs JavaScript
- Si erreur CORS : Redémarrer le serveur

#### Vérifier 4 : Test manuel API
```bash
curl -X POST http://localhost:8000/predict -F "file=@chemin/vers/image.jpg"
```

---

## 📊 Tests de Validation

### ✅ Checklist Desktop

- [ ] Fenêtre s'ouvre (1200x700)
- [ ] Header visible avec titre complet
- [ ] 3 stats cards lisibles
- [ ] Bouton "Parcourir" cliquable et texte visible
- [ ] Bouton "ANALYSER" lisible (désactivé)
- [ ] Clic sur Parcourir ouvre dialogue
- [ ] Sélection image → preview s'affiche
- [ ] Bouton ANALYSER s'active
- [ ] Clic ANALYSER → loader + analyse
- [ ] Résultats s'affichent correctement

### ✅ Checklist Web

- [ ] Page charge à http://localhost:8000
- [ ] Header visible
- [ ] 3 stats affichées
- [ ] Zone upload cliquable
- [ ] Clic zone → dialogue fichier
- [ ] Sélection image → preview
- [ ] Bouton ANALYSER actif
- [ ] Clic ANALYSER → loader
- [ ] Résultats affichés avec couleurs
- [ ] Barres de probabilités animées

---

## 📝 Notes Importantes

1. **Emojis** : Si problème d'affichage, les enlever
2. **Taille écran** : Minimum 1200px largeur recommandé
3. **Modèle** : DOIT être chiffré dans `models/breast_cancer_model.onnx.enc`
4. **Logs** : Vérifier `%LOCALAPPDATA%\DIANA\logs\` si erreur

---

## 🎯 Si TOUT est tronqué malgré les corrections

**Solution radicale** : Mode compact

Remplacer dans `src/ui/modern_main_window.py` :

```python
def __init__(self):
    super().__init__()
    # ... (code existant) ...
    
    # FORCER la fenêtre en plein écran
    self.showMaximized()  # Ajouter cette ligne après setup_ui()
```

Ou utiliser une interface **encore plus simple** :

```python
# Remplacer ligne 66
self.setMinimumSize(1000, 600)  # Très compact
```

Et dans `modern_styles.py`, TOUT réduire à :
```css
font-size: 10px;  /* Partout */
padding: 4px 8px; /* Tous les boutons */
```

---

**DIANA v1.0.0** - Interface moderne adaptative

