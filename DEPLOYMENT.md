# 🚀 Guide de déploiement DIANA

Ce guide détaille le processus complet de déploiement de DIANA pour une distribution professionnelle.

## 📋 Table des matières

1. [Préparation du build](#préparation-du-build)
2. [Configuration Supabase](#configuration-supabase)
3. [Chiffrement du modèle](#chiffrement-du-modèle)
4. [Build des exécutables](#build-des-exécutables)
5. [Configuration du serveur de mises à jour](#configuration-du-serveur-de-mises-à-jour)
6. [Distribution](#distribution)
7. [Maintenance](#maintenance)

## 🔧 Préparation du build

### 1. Vérifier l'environnement

```bash
# Vérifier Python
python --version  # Doit être >= 3.9

# Vérifier pip
pip --version

# Vérifier PyInstaller
pip install pyinstaller
pyinstaller --version
```

### 2. Nettoyer les builds précédents

```bash
# Supprimer les anciens builds
rm -rf build/ dist/ *.spec

# Windows PowerShell
Remove-Item -Recurse -Force build, dist, *.spec
```

### 3. Installer toutes les dépendances

```bash
pip install -r requirements.txt
```

## 🗄️ Configuration Supabase

### 1. Créer un projet Supabase

1. Allez sur [https://supabase.com](https://supabase.com)
2. Créez un nouveau projet
3. Notez les credentials :
   - Project URL
   - anon public key
   - service_role key (secret)

### 2. Configurer la base de données

```bash
# Dans la console SQL de Supabase, exécutez :
scripts/setup_supabase.sql
```

Vérifications :
- [ ] Tables créées (users, user_devices, usage_logs)
- [ ] Index créés
- [ ] Triggers configurés
- [ ] RLS activé
- [ ] Politiques de sécurité actives

### 3. Configurer l'authentification

Dans les paramètres Supabase :

**Authentication > Providers**
- [ ] Email activé
- [ ] Confirmation email activée (optionnel)
- [ ] Google OAuth (optionnel)

**Authentication > Email Templates**
Personnalisez les templates :
- Confirmation email
- Reset password
- Magic link

### 4. Variables d'environnement

Mettez à jour `.env` :

```env
SUPABASE_URL=https://votre-projet.supabase.co
SUPABASE_ANON_KEY=eyJhbG...
SUPABASE_SERVICE_ROLE_KEY=eyJhbG...
```

## 🔐 Chiffrement du modèle

### 1. Préparer le modèle ONNX

Assurez-vous d'avoir un modèle ONNX valide :

```bash
# Tester le modèle avec onnxruntime
python -c "import onnxruntime; onnxruntime.InferenceSession('votre_modele.onnx')"
```

### 2. Générer une clé de chiffrement

```python
from cryptography.fernet import Fernet

# Générer une nouvelle clé
key = Fernet.generate_key()
print(key.decode())
```

Copiez cette clé dans `.env` :

```env
ENCRYPTION_KEY=votre_cle_generee_ici
```

### 3. Chiffrer le modèle

```bash
python scripts/encrypt_model.py
```

Suivez les instructions :
1. Entrez le chemin du modèle source
2. Confirmez le chemin de sortie
3. Vérifiez que le chiffrement est réussi

Vérifications :
- [ ] Fichier `.onnx.enc` créé
- [ ] Taille cohérente (légèrement plus grande que l'original)
- [ ] Vérification de déchiffrement réussie

### 4. Sécuriser la clé

⚠️ **IMPORTANT** : Ne commitez JAMAIS la clé de chiffrement dans Git !

```bash
# Vérifiez que .env est dans .gitignore
grep ".env" .gitignore
```

## 📦 Build des exécutables

### Build Windows

```bash
# Sur une machine Windows
python scripts/build.py
```

Options avancées :

```bash
# Build avec console (pour debug)
pyinstaller --name=DIANA \
    --onefile \
    --icon=assets/icon.ico \
    --add-data="models;models" \
    main.py

# Build sans console (production)
pyinstaller --name=DIANA \
    --onefile \
    --windowed \
    --icon=assets/icon.ico \
    --add-data="models;models" \
    main.py
```

### Build macOS

```bash
# Sur macOS
python scripts/build.py
```

Pour créer un DMG :

```bash
# Installer create-dmg
brew install create-dmg

# Créer le DMG
create-dmg \
    --volname "DIANA Installer" \
    --window-pos 200 120 \
    --window-size 800 400 \
    --icon-size 100 \
    --app-drop-link 600 185 \
    DIANA-1.0.0.dmg \
    dist/DIANA.app
```

### Build Linux

```bash
# Sur Linux
python scripts/build.py
```

Pour créer un AppImage :

```bash
# Installer appimagetool
wget https://github.com/AppImage/AppImageKit/releases/download/continuous/appimagetool-x86_64.AppImage
chmod +x appimagetool-x86_64.AppImage

# Créer la structure AppImage
mkdir -p DIANA.AppDir/usr/bin
cp dist/DIANA DIANA.AppDir/usr/bin/
cp assets/icon.png DIANA.AppDir/
cp assets/DIANA.desktop DIANA.AppDir/

# Générer l'AppImage
./appimagetool-x86_64.AppImage DIANA.AppDir DIANA-1.0.0-x86_64.AppImage
```

## 🌐 Configuration du serveur de mises à jour

### 1. Choisir un hébergement

Options recommandées :
- **GitHub Releases** (gratuit, facile)
- **AWS S3** (professionnel, évolutif)
- **Azure Blob Storage**
- **Serveur web personnel**

### 2. Structure des fichiers

```
update-server/
├── latest.json           # Métadonnées de la dernière version
├── releases/
│   ├── 1.0.0/
│   │   ├── DIANA-1.0.0-Windows.exe
│   │   ├── DIANA-1.0.0-macOS.dmg
│   │   └── DIANA-1.0.0-Linux.AppImage
│   └── 1.1.0/
│       ├── DIANA-1.1.0-Windows.exe
│       ├── DIANA-1.1.0-macOS.dmg
│       └── DIANA-1.1.0-Linux.AppImage
└── checksums/
    ├── 1.0.0.sha256
    └── 1.1.0.sha256
```

### 3. Générer les checksums

```bash
# Windows
Get-FileHash -Algorithm SHA256 DIANA-1.0.0-Windows.exe | Select-Object Hash

# macOS/Linux
shasum -a 256 DIANA-1.0.0-macOS.dmg
```

### 4. Créer latest.json

```json
{
  "version": "1.0.0",
  "release_date": "2025-10-02",
  "platforms": {
    "windows": {
      "download_url": "https://updates.diana-ai.com/releases/1.0.0/DIANA-1.0.0-Windows.exe",
      "checksum": "abc123def456...",
      "size_mb": 85.5
    },
    "darwin": {
      "download_url": "https://updates.diana-ai.com/releases/1.0.0/DIANA-1.0.0-macOS.dmg",
      "checksum": "def789ghi012...",
      "size_mb": 92.3
    },
    "linux": {
      "download_url": "https://updates.diana-ai.com/releases/1.0.0/DIANA-1.0.0-Linux.AppImage",
      "checksum": "ghi345jkl678...",
      "size_mb": 88.1
    }
  },
  "checksum_algorithm": "sha256",
  "release_notes": "🎉 Version initiale de DIANA\n\n✨ Nouvelles fonctionnalités :\n- Détection IA du cancer du sein\n- Mode freemium avec 5000 analyses gratuites\n- Compte premium avec analyses illimitées\n- Interface moderne avec thèmes clair/sombre\n- Mises à jour automatiques\n\n🔧 Corrections :\n- Aucune (première version)\n\n⚠️ Notes importantes :\n- Nécessite une connexion internet pour le mode Premium\n- Le modèle IA fonctionne en local (pas besoin d'internet pour les analyses)",
  "min_version": "1.0.0",
  "critical_update": false
}
```

### 5. Upload sur le serveur

#### Avec GitHub Releases

```bash
# Créer un tag
git tag -a v1.0.0 -m "Version 1.0.0"
git push origin v1.0.0

# Uploader les fichiers via l'interface web GitHub
# Ou avec gh CLI :
gh release create v1.0.0 \
    dist/DIANA-1.0.0-Windows.exe \
    dist/DIANA-1.0.0-macOS.dmg \
    dist/DIANA-1.0.0-Linux.AppImage \
    --title "DIANA v1.0.0" \
    --notes-file RELEASE_NOTES.md
```

#### Avec AWS S3

```bash
# Upload des fichiers
aws s3 cp dist/DIANA-1.0.0-Windows.exe s3://diana-updates/releases/1.0.0/
aws s3 cp latest.json s3://diana-updates/

# Rendre public
aws s3api put-object-acl --bucket diana-updates --key latest.json --acl public-read
```

### 6. Configurer CORS (si nécessaire)

Pour S3, créez une politique CORS :

```json
[
    {
        "AllowedHeaders": ["*"],
        "AllowedMethods": ["GET", "HEAD"],
        "AllowedOrigins": ["*"],
        "ExposeHeaders": []
    }
]
```

### 7. Tester les mises à jour

```bash
# Tester l'URL
curl https://updates.diana-ai.com/latest.json

# Vérifier le checksum
curl -O https://updates.diana-ai.com/releases/1.0.0/DIANA-1.0.0-Windows.exe
shasum -a 256 DIANA-1.0.0-Windows.exe
```

## 📤 Distribution

### 1. Créer un installateur Windows (optionnel)

Utilisez **Inno Setup** :

```iss
[Setup]
AppName=DIANA
AppVersion=1.0.0
DefaultDirName={pf}\DIANA
DefaultGroupName=DIANA
OutputDir=dist
OutputBaseFilename=DIANA-1.0.0-Setup

[Files]
Source: "dist\DIANA.exe"; DestDir: "{app}"
Source: "models\*"; DestDir: "{app}\models"

[Icons]
Name: "{group}\DIANA"; Filename: "{app}\DIANA.exe"
Name: "{commondesktop}\DIANA"; Filename: "{app}\DIANA.exe"
```

Compiler :

```bash
iscc installer.iss
```

### 2. Signer les exécutables (recommandé)

#### Windows

```bash
# Obtenir un certificat de signature de code
# Puis signer avec signtool.exe

signtool sign /f certificat.pfx /p password /t http://timestamp.digicert.com DIANA.exe
```

#### macOS

```bash
# Signer avec un Apple Developer ID
codesign --deep --force --verify --verbose --sign "Developer ID Application: Votre Nom" DIANA.app

# Notariser l'app
xcrun altool --notarize-app --file DIANA.dmg --primary-bundle-id com.diana.app
```

### 3. Tester sur machines propres

Testez sur des VMs ou machines fraîches :
- [ ] Windows 10/11
- [ ] macOS 12+
- [ ] Ubuntu 20.04/22.04

### 4. Distribuer

Options de distribution :
- Site web officiel
- Microsoft Store
- Mac App Store
- Snap Store (Linux)
- Distribution directe aux clients

## 🔄 Maintenance

### Mise à jour du modèle

```bash
# 1. Obtenir le nouveau modèle
# 2. Le chiffrer
python scripts/encrypt_model.py

# 3. Rebuild l'application
python scripts/build.py

# 4. Publier la nouvelle version
```

### Ajouter un utilisateur Premium manuellement

```sql
-- Dans Supabase SQL
UPDATE users
SET is_premium = TRUE
WHERE email = 'client@example.com';
```

### Monitoring

Créez une vue pour surveiller l'utilisation :

```sql
-- Statistiques journalières
SELECT
    DATE(timestamp) as date,
    COUNT(*) as analyses_count,
    COUNT(DISTINCT user_id) as unique_users
FROM usage_logs
WHERE action = 'prediction'
GROUP BY DATE(timestamp)
ORDER BY date DESC;
```

### Backup

```bash
# Backup quotidien de Supabase
# Configurez dans Supabase Dashboard > Database > Backups

# Backup local des données
cp -r data/ backup/data-$(date +%Y%m%d)/
```

## ✅ Checklist de déploiement

Avant chaque release :

### Préparation
- [ ] Tests unitaires passent
- [ ] Tests d'intégration passent
- [ ] Version incrémentée dans `config.py`
- [ ] Changelog mis à jour
- [ ] Documentation à jour

### Build
- [ ] Modèle chiffré à jour
- [ ] Builds pour toutes les plateformes
- [ ] Exécutables signés
- [ ] Checksums générés

### Serveur
- [ ] `latest.json` mis à jour
- [ ] Fichiers uploadés
- [ ] URLs testées
- [ ] Checksums vérifiés

### Tests finaux
- [ ] Installation sur machine propre
- [ ] Première exécution OK
- [ ] Authentification OK
- [ ] Prédictions OK
- [ ] Mise à jour automatique OK

### Post-déploiement
- [ ] Annonce sur les canaux officiels
- [ ] Monitoring actif
- [ ] Support prêt

---

**Félicitations ! Vous êtes prêt à déployer DIANA ! 🚀**

