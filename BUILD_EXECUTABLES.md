# 🚀 Créer l'exécutable DIANA (Application standalone)

## 🎯 Objectif

Créer un fichier **DIANA.exe** qui se lance en double-cliquant, comme n'importe quelle application Windows (CapCut, VSCode, etc.).

---

## ⚡ Processus COMPLET (étape par étape)

### ✅ Étape 1 : Préparer l'environnement (une seule fois)

```powershell
# Ouvrir PowerShell dans le dossier DIANA
cd C:\Users\badza\Desktop\DIANA

# Créer un environnement virtuel
python -m venv venv

# Activer l'environnement
.\venv\Scripts\Activate.ps1

# Installer toutes les dépendances
pip install -r requirements.txt

# Installer PyInstaller pour créer l'exécutable
pip install pyinstaller
```

### ✅ Étape 2 : Créer un modèle de test (si vous n'en avez pas)

```powershell
# Créer un modèle dummy pour tester
python scripts/create_dummy_model.py
# Appuyez sur Entrée pour accepter les valeurs par défaut
```

### ✅ Étape 3 : Chiffrer le modèle

```powershell
python scripts/encrypt_model.py
# Chemin du modèle : models/breast_cancer_model.onnx
# Chemin de sortie : (appuyez sur Entrée)
# Lancer le chiffrement : o
```

### ✅ Étape 4 : Créer l'exécutable Windows

```powershell
# Lancer le script de build
python scripts/build.py
# Confirmer : o
```

**⏱️ Durée** : 2-5 minutes selon votre machine

### ✅ Étape 5 : Trouver votre exécutable

```
📂 C:\Users\badza\Desktop\DIANA\
   └── 📂 dist\
       └── 🚀 DIANA.exe  ← VOTRE APPLICATION !
```

---

## 🎉 Utilisation de l'application

### Double-cliquez sur DIANA.exe

```
dist/DIANA.exe  ← Double-clic pour lancer !
```

L'application se lance comme n'importe quelle application Windows :
- ✅ Fenêtre moderne
- ✅ Interface graphique complète
- ✅ Aucune ligne de commande visible
- ✅ Fonctionne sans Python installé

---

## 📦 Distribution de l'application

### Option 1 : Distribuer juste l'EXE

```
Envoyez simplement :
📄 DIANA.exe (dans dist/)
```

L'utilisateur n'a qu'à :
1. Double-cliquer sur DIANA.exe
2. C'est tout !

### Option 2 : Créer un installateur Windows (professionnel)

Utilisez **Inno Setup** :

1. **Télécharger Inno Setup** : https://jrsoftware.org/isdl.php

2. **Créer le fichier de configuration** (déjà fourni ci-dessous)

3. **Compiler l'installateur**

---

## 🎯 Créer un VRAI installateur (Setup.exe)

### Fichier de configuration Inno Setup

Créez `installer.iss` :

```iss
[Setup]
AppName=DIANA
AppVersion=1.0.0
AppPublisher=DIANA Team
DefaultDirName={autopf}\DIANA
DefaultGroupName=DIANA
OutputDir=dist\installer
OutputBaseFilename=DIANA-Setup-1.0.0
Compression=lzma2
SolidCompression=yes
PrivilegesRequired=admin
SetupIconFile=assets\icon.ico
UninstallDisplayIcon={app}\DIANA.exe

[Files]
Source: "dist\DIANA.exe"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\DIANA"; Filename: "{app}\DIANA.exe"
Name: "{group}\Désinstaller DIANA"; Filename: "{uninstallexe}"
Name: "{autodesktop}\DIANA"; Filename: "{app}\DIANA.exe"; Tasks: desktopicon
Name: "{autostartup}\DIANA"; Filename: "{app}\DIANA.exe"; Tasks: startupicon

[Tasks]
Name: "desktopicon"; Description: "Créer un raccourci sur le Bureau"
Name: "startupicon"; Description: "Lancer au démarrage de Windows"

[Run]
Filename: "{app}\DIANA.exe"; Description: "Lancer DIANA"; Flags: nowait postinstall skipifsilent
```

### Compiler l'installateur

```powershell
# Si Inno Setup est installé
"C:\Program Files (x86)\Inno Setup 6\ISCC.exe" installer.iss
```

**Résultat** :
```
📂 dist\installer\
   └── 🎁 DIANA-Setup-1.0.0.exe  ← INSTALLATEUR PROFESSIONNEL !
```

---

## 🔧 Options avancées du build

### Build avec console (pour debug)

Si vous voulez voir les logs pendant le développement :

```powershell
pyinstaller --name=DIANA --onefile --icon=assets/icon.ico main.py
```

### Build sans console (production)

Pour une vraie application sans console :

```powershell
pyinstaller --name=DIANA --onefile --windowed --icon=assets/icon.ico main.py
```

---

## 📋 Checklist avant distribution

- [ ] Modèle ONNX chiffré présent dans `models/`
- [ ] Build réussi sans erreurs
- [ ] Test de l'exécutable sur machine propre
- [ ] Icône Windows présente (optionnel)
- [ ] Installateur créé (optionnel mais recommandé)

---

## 🎨 Ajouter une icône Windows

### Créer une icône .ico

1. **Préparez une image PNG** (512x512 minimum)

2. **Convertir en .ico** :
   - En ligne : https://convertico.com/
   - Ou avec ImageMagick : `convert icon.png -resize 256x256 icon.ico`

3. **Placer l'icône** :
   ```
   📂 assets\
      └── icon.ico
   ```

4. **Rebuild avec l'icône** :
   ```powershell
   python scripts/build.py
   ```

---

## 🚀 Lancement automatique au démarrage Windows

### Option 1 : Pendant l'installation (Inno Setup)

Cochez l'option "Lancer au démarrage" pendant l'installation.

### Option 2 : Manuellement

```powershell
# Créer un raccourci dans le dossier Démarrage
$WshShell = New-Object -comObject WScript.Shell
$Shortcut = $WshShell.CreateShortcut("$env:APPDATA\Microsoft\Windows\Start Menu\Programs\Startup\DIANA.lnk")
$Shortcut.TargetPath = "C:\Program Files\DIANA\DIANA.exe"
$Shortcut.Save()
```

### Option 3 : Via le registre Windows

```powershell
# Ajouter au démarrage via le registre
New-ItemProperty -Path "HKCU:\Software\Microsoft\Windows\CurrentVersion\Run" -Name "DIANA" -Value "C:\Program Files\DIANA\DIANA.exe" -PropertyType String -Force
```

---

## 🎯 Résumé : De zéro à l'application finale

```powershell
# 1. Setup initial (une fois)
cd C:\Users\badza\Desktop\DIANA
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt

# 2. Préparer le modèle
python scripts/create_dummy_model.py
python scripts/encrypt_model.py

# 3. Créer l'exécutable
python scripts/build.py

# 4. Tester
.\dist\DIANA.exe

# 5. (Optionnel) Créer l'installateur
# Installer Inno Setup puis compiler installer.iss
```

---

## ✅ Résultat final

Vous obtenez :

### Version simple
```
📄 DIANA.exe  ← 80-150 MB
```
Double-clic → L'app se lance !

### Version professionnelle
```
🎁 DIANA-Setup-1.0.0.exe  ← 80-150 MB
```
Double-clic → Installation → Raccourci Bureau → App installée !

---

## 🐛 Problèmes courants

### Erreur : "PyInstaller not found"
```powershell
pip install pyinstaller
```

### Erreur : "Failed to execute script"
```powershell
# Build avec console pour voir l'erreur
pyinstaller --name=DIANA --onefile main.py
# Puis lancer pour voir les logs
.\dist\DIANA.exe
```

### L'EXE est trop gros (>200MB)
```powershell
# Utiliser UPX pour compresser
pip install pyinstaller[upx]
python scripts/build.py
```

### Antivirus bloque l'EXE
C'est normal pour les nouveaux EXE. Solutions :
1. Signer l'exécutable avec un certificat de code
2. Soumettre à Microsoft Defender (whitelist)
3. Ajouter une exception dans l'antivirus

---

## 💡 Prochaines étapes

Une fois l'exécutable créé :

1. ✅ Testez sur plusieurs machines Windows
2. ✅ Créez l'installateur professionnel
3. ✅ Distribuez aux utilisateurs
4. ✅ Configurez le système d'auto-update

**L'application est maintenant STANDALONE et PROFESSIONNELLE !** 🎉

