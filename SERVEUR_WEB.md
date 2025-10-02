# 🌐 DIANA - Version Web (Serveur)

## 🎯 Qu'est-ce que c'est ?

Une **interface web** pour tester DIANA dans un navigateur, sans installer l'application desktop !

```
┌─────────────────────────────────────┐
│      Navigateur Web                 │
│  (Chrome, Firefox, Edge, etc.)      │
│                                     │
│  http://localhost:8000              │
│                                     │
│  [Interface moderne]                │
│  [Upload d'image]                   │
│  [Résultats en temps réel]          │
└─────────────────────────────────────┘
```

---

## 🚀 Lancer le serveur web

### Méthode 1 : Double-clic (recommandé)

```
📄 LANCER_SERVEUR_WEB.bat
   ↓
   Double-cliquez dessus !
```

### Méthode 2 : Commandes manuelles

```powershell
# Activer l'environnement
.\venv\Scripts\Activate.ps1

# Installer les dépendances web
pip install -r requirements-web.txt

# Lancer le serveur
python web_app.py
```

---

## 📱 Accéder à l'application

### Sur votre machine :

```
http://localhost:8000
```

### Depuis un autre appareil (même réseau WiFi) :

```
1. Trouvez votre IP :
   ipconfig  (Windows)
   
2. Notez l'adresse IPv4, par exemple : 192.168.1.42

3. Sur l'autre appareil (téléphone, tablette, autre PC) :
   http://192.168.1.42:8000
```

**Vous pouvez tester DIANA depuis votre téléphone ! 📱**

---

## ✨ Fonctionnalités de la version Web

### Page principale

```
╔═══════════════════════════════════════════════════════╗
║              🏥 DIANA                                 ║
║    Diagnostic Intelligent Automatisé                  ║
╠═══════════════════════════════════════════════════════╣
║                                                       ║
║  Statistiques :                                       ║
║  ┌─────────┬─────────────┬──────────┐                ║
║  │   42    │    4958     │  Gratuit │                ║
║  │ Utilisé │  Restantes  │  Statut  │                ║
║  └─────────┴─────────────┴──────────┘                ║
║                                                       ║
║  ┌──────────────────────┬──────────────────────┐     ║
║  │ 📁 Sélectionner      │ 📊 Résultats         │     ║
║  │                      │                      │     ║
║  │ [Upload Area]        │ [Aucune analyse]     │     ║
║  │                      │                      │     ║
║  │ [🔬 Analyser]        │                      │     ║
║  └──────────────────────┴──────────────────────┘     ║
║                                                       ║
╚═══════════════════════════════════════════════════════╝
```

### Fonctionnalités disponibles :

✅ **Upload d'images**
   - Glisser-déposer ou clic
   - Aperçu avant analyse
   - Formats : JPG, PNG, BMP, TIFF

✅ **Analyse IA**
   - Même moteur que l'app desktop
   - Résultats en temps réel
   - Niveau de confiance

✅ **Statistiques**
   - Compteur d'analyses
   - Quota restant
   - Statut (Gratuit/Premium)

✅ **Interface moderne**
   - Design responsive
   - Compatible mobile
   - Animations fluides

---

## 🔌 API Endpoints

### GET /

Page principale avec interface

### POST /analyze

Upload et analyse d'image

```javascript
// Exemple avec JavaScript
const formData = new FormData();
formData.append('file', imageFile);

fetch('http://localhost:8000/analyze', {
    method: 'POST',
    body: formData
})
.then(res => res.json())
.then(data => {
    console.log(data.result);
    // { prediction: "Bénin", confidence: 94.2, ... }
});
```

### GET /api/stats

Statistiques de l'application

```json
{
    "app_version": "1.0.0",
    "quota": {
        "used": 42,
        "remaining": 4958,
        "is_premium": false
    },
    "model": {
        "loaded": true,
        "providers": ["CPUExecutionProvider"]
    }
}
```

### GET /api/health

Health check

```json
{
    "status": "healthy",
    "app": "DIANA",
    "version": "1.0.0"
}
```

---

## 🌍 Déployer sur Internet

### Option 1 : Serveur cloud simple

```bash
# Sur un serveur Ubuntu/Debian
git clone <votre-repo>
cd DIANA

# Installer Python et dépendances
sudo apt update
sudo apt install python3 python3-pip python3-venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements-web.txt

# Lancer avec nohup (reste actif)
nohup python web_app.py &

# Ouvrir le port 8000
sudo ufw allow 8000
```

**Accès : http://[IP_SERVEUR]:8000**

### Option 2 : Avec Nginx (production)

```nginx
# /etc/nginx/sites-available/diana
server {
    listen 80;
    server_name diana.example.com;
    
    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### Option 3 : Docker

```dockerfile
FROM python:3.10-slim

WORKDIR /app
COPY . .

RUN pip install -r requirements-web.txt

EXPOSE 8000

CMD ["python", "web_app.py"]
```

```bash
docker build -t diana-web .
docker run -p 8000:8000 diana-web
```

---

## 🔒 Sécurité pour production

### À faire avant déploiement public :

1. **HTTPS obligatoire**
   ```bash
   # Avec Certbot (Let's Encrypt)
   sudo certbot --nginx -d diana.example.com
   ```

2. **Limiter les uploads**
   ```python
   # Déjà implémenté : taille max, formats validés
   ```

3. **Rate limiting**
   ```python
   # Installer slowapi
   pip install slowapi
   ```

4. **Variables d'environnement**
   ```bash
   # Utiliser .env pour les secrets
   # Ne jamais commiter les clés
   ```

5. **Monitoring**
   ```bash
   # Logs, alertes, uptime monitoring
   ```

---

## 📊 Comparaison Web vs Desktop

| Fonctionnalité | Desktop (PyQt6) | Web (FastAPI) |
|----------------|-----------------|---------------|
| **Installation** | Téléchargement EXE | Aucune |
| **Accès** | Local uniquement | Depuis n'importe où |
| **Performance** | ⚡ Très rapide | ⚡ Rapide |
| **Offline** | ✅ Oui | ❌ Besoin d'internet |
| **Multi-utilisateurs** | ❌ Non | ✅ Oui |
| **Mobile** | ❌ Non | ✅ Oui (responsive) |
| **Mise à jour** | Automatique | Immédiate |
| **Sécurité** | ✅ Locale | ⚠️ Dépend du serveur |

---

## 🎯 Cas d'usage

### Version Web idéale pour :

✅ **Démonstration** : Montrer DIANA à des clients/investisseurs  
✅ **Test rapide** : Tester sans installer  
✅ **Mobile** : Utiliser depuis un smartphone/tablette  
✅ **Partage** : Plusieurs personnes testent en même temps  
✅ **Beta testing** : Tests avant le build desktop  

### Version Desktop idéale pour :

✅ **Production clinique** : Hôpitaux, cliniques  
✅ **Offline** : Pas de connexion internet  
✅ **Performance maximale** : GPU local  
✅ **Confidentialité** : Données restent locales  
✅ **Usage intensif** : Milliers d'analyses  

---

## 🐛 Dépannage

### Port 8000 déjà utilisé

```powershell
# Changer le port dans web_app.py
uvicorn.run(app, host="0.0.0.0", port=8080)
```

### Impossible d'accéder depuis un autre appareil

```powershell
# Vérifier le firewall Windows
netsh advfirewall firewall add rule name="DIANA Web" dir=in action=allow protocol=TCP localport=8000
```

### Erreur "Cannot decrypt model"

```bash
# Re-chiffrer le modèle
python scripts/encrypt_model.py
```

---

## 🚀 Lancement rapide

```bash
# En une commande !
python web_app.py
```

Ou double-cliquez sur : **LANCER_SERVEUR_WEB.bat**

Puis ouvrez : **http://localhost:8000** dans votre navigateur ! 🎉

---

## 📱 Exemple d'utilisation mobile

```
1. Lancez le serveur sur votre PC
2. Notez votre IP (exemple : 192.168.1.42)
3. Sur votre smartphone :
   - Ouvrez Chrome/Safari
   - Tapez : http://192.168.1.42:8000
   - Prenez une photo avec votre téléphone
   - Uploadez et analysez !
```

**DIANA fonctionne sur mobile ! 📱✨**

