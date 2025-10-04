"""
DIANA - Version Web
Application web FastAPI modulaire avec composants réutilisables
"""

import io
import logging
import tempfile
import os
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, File, UploadFile, HTTPException, Form, Request
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image
import uvicorn

import config
from src.quota_manager import get_quota_manager
from src.auth_manager import get_auth_manager
from src.inference_engine import get_inference_engine

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Créer l'application FastAPI
app = FastAPI(
    title="DIANA Web",
    description="Diagnostic Intelligent Automatisé - Version Web",
    version=config.APP_VERSION
)

# Middleware pour limiter la taille des requêtes (50 MB)
@app.middleware("http")
async def limit_upload_size(request: Request, call_next):
    """Limite la taille des uploads à 50 MB"""
    if request.method == "POST":
        content_length = request.headers.get("content-length")
        if content_length:
            content_length = int(content_length)
            max_size = 50 * 1024 * 1024  # 50 MB
            if content_length > max_size:
                return JSONResponse(
                    status_code=413,
                    content={"detail": "Fichier trop volumineux. Maximum: 50 MB"}
                )
    response = await call_next(request)
    return response

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Monter le dossier static
app.mount("/static", StaticFiles(directory="static"), name="static")

# Initialiser les managers
quota_manager = get_quota_manager()
auth_manager = get_auth_manager()
inference_engine = get_inference_engine()

# Initialiser le filtre d'images
try:
    from src.image_filter import get_image_filter
    filter_engine = get_image_filter()
    filter_loaded = filter_engine.load_model()
    if filter_loaded:
        logger.info("✅ Filtre d'images initialisé pour l'API web")
    else:
        logger.warning("⚠️ Filtre d'images non disponible - toutes les images seront acceptées")
except Exception as e:
    logger.warning(f"Erreur initialisation filtre web: {e}")


# ========== ROUTES PRINCIPALES ==========

@app.get("/", response_class=HTMLResponse)
async def redirect_to_app():
    """Redirection vers l'application complète"""
    return RedirectResponse(url="/app")


@app.get("/app", response_class=HTMLResponse)
async def app_page():
    """Application complète avec composants modulaires"""
    
    stats = quota_manager.get_stats()
    
    return HTMLResponse(content=f"""
    <!DOCTYPE html>
    <html lang="fr">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>DIANA - Diagnostic IA Nouvelle Génération</title>
        <link rel="stylesheet" href="/static/css/styles.css">
    </head>
    <body class="theme-dark">
        <div class="container">
            <!-- Header -->
            <div class="header" id="mainHeader">
                <div class="header-buttons">
                    <button class="btn-header" id="homeBtn">🏠 Accueil</button>
                    <button class="btn-header" id="menuBtn">⚙️ Paramètres</button>
                    <button class="btn-header" id="loginBtn">🔐 Connexion</button>
                </div>
                <h1>🏥 DIANA</h1>
                <p>Diagnostic Intelligent Automatisé pour les Nouvelles Analyses</p>
            </div>
            
            <!-- Menu paramètres -->
            <div id="mainMenu" class="main-menu">
                <a href="#" onclick="AppState.navigateTo('profile'); return false;">👤 Mon Profil</a>
                <a href="#" onclick="AppState.navigateTo('settings'); return false;">🎨 Apparence</a>
                <a href="#" onclick="AppState.navigateTo('help'); return false;">❓ Aide & Support</a>
                <a href="#" onclick="AppState.navigateTo('signup'); return false;" id="signupLink">✨ S'inscrire</a>
                <a href="#" onclick="confirmLogout(); return false;" id="logoutLink" style="display: none;">🚪 Se déconnecter</a>
            </div>
            
            <!-- Contenu principal (pages dynamiques) -->
            <div id="mainContent"></div>
            
            <!-- Stats -->
            <div class="stats">
                <div class="stat-card">
                    <div class="stat-value">{stats['used']}</div>
                    <div class="stat-label">Analyses Effectuées</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">{'∞' if stats['is_premium'] else stats['remaining']}</div>
                    <div class="stat-label">Analyses Restantes</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">{'✨' if stats['is_premium'] else '🆓'}</div>
                    <div class="stat-label">{'Premium' if stats['is_premium'] else 'Gratuit'}</div>
                </div>
            </div>
            
            <!-- Footer -->
            <div class="footer">
                <p>DIANA v{config.APP_VERSION} - Diagnostic Intelligent Automatisé</p>
                <p style="margin-top: 12px;">⚠️ Outil d'aide au diagnostic • Consultez un professionnel de santé</p>
            </div>
        </div>
        
        <!-- Scripts modulaires -->
        <script src="/static/js/components.js?v=2"></script>
        <script src="/static/js/pages.js?v=2"></script>
        <script src="/static/js/app.js?v=2"></script>
    </body>
    </html>
    """)


# ========== ENDPOINTS API ==========

@app.post("/predict")
async def predict(file: UploadFile = File(...)):
    """Endpoint de prédiction"""
    temp_path = None
    try:
        logger.info(f"Réception d'un fichier: {file.filename} ({file.content_type})")
        
        # Vérifier le quota
        if not quota_manager.can_analyze():
            raise HTTPException(
                status_code=429,
                detail="Quota épuisé. Connectez-vous avec un compte Premium."
            )
        
        # Vérifier le type de fichier
        if not file.content_type or not file.content_type.startswith('image/'):
            raise HTTPException(
                status_code=400,
                detail="Le fichier doit être une image (JPG, PNG, BMP, etc.)"
            )
        
        # Lire le contenu du fichier
        contents = await file.read()
        logger.info(f"Fichier lu: {len(contents)} octets")
        
        if len(contents) == 0:
            raise HTTPException(status_code=400, detail="Le fichier est vide")
        
        # Vérifier que c'est une image valide
        try:
            image = Image.open(io.BytesIO(contents))
            logger.info(f"Image chargée: {image.size}, mode: {image.mode}")
        except Exception as e:
            logger.error(f"Erreur lors du chargement de l'image: {e}")
            raise HTTPException(
                status_code=400,
                detail=f"Impossible de lire l'image: {str(e)}"
            )
        
        # Créer un fichier temporaire sécurisé
        file_ext = os.path.splitext(file.filename)[1].lower()
        if not file_ext:
            file_ext = '.png'
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as temp_file:
            temp_path = Path(temp_file.name)
            image.save(temp_path)
            logger.info(f"Image sauvegardée temporairement: {temp_path}")
        
        # Faire la prédiction
        logger.info("Début de la prédiction...")
        result = inference_engine.predict(temp_path)
        
        if not result:
            raise HTTPException(status_code=500, detail="Erreur lors de la prédiction")
        
        # Vérifier si l'image a été rejetée par le filtre
        if result.get("error") and result.get("message"):
            logger.warning(f"Image rejetée: {result['message']}")
            raise HTTPException(
                status_code=400, 
                detail=result["message"]
            )
        
        logger.info(f"Prédiction réussie: {result['prediction']}")
        return JSONResponse(content=result)
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur prédiction: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
    
    finally:
        # Nettoyer le fichier temporaire
        if temp_path and temp_path.exists():
            try:
                temp_path.unlink()
                logger.info(f"Fichier temporaire supprimé: {temp_path}")
            except Exception as e:
                logger.warning(f"Impossible de supprimer le fichier temporaire: {e}")


@app.get("/api/stats")
async def get_stats():
    """Retourne les statistiques"""
    return JSONResponse(content=quota_manager.get_stats())


@app.get("/api/health")
async def health_check():
    """Health check"""
    return {"status": "ok", "version": config.APP_VERSION}


@app.get("/api/filter/status")
async def get_filter_status():
    """Statut du filtre d'images"""
    from src.image_filter import get_image_filter
    
    filter_engine = get_image_filter()
    filter_info = filter_engine.get_model_info()
    
    return JSONResponse(content={
        "filter_loaded": filter_info["loaded"],
        "model_exists": filter_info["model_exists"],
        "model_path": filter_info["model_path"],
        "message": "Filtre actif" if filter_info["loaded"] else "Filtre non disponible - toutes les images seront acceptées"
    })


@app.post("/api/auth/login")
async def login(email: str = Form(...), password: str = Form(...)):
    """Connexion utilisateur"""
    try:
        result = auth_manager.login(email, password)
        if result:
            return JSONResponse(content={
                "success": True,
                "user": result,
                "message": "Connexion réussie"
            })
        else:
            raise HTTPException(status_code=401, detail="Email ou mot de passe incorrect")
    except Exception as e:
        logger.error(f"Erreur login: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/auth/signup")
async def signup(email: str = Form(...), password: str = Form(...), name: str = Form(...)):
    """Inscription utilisateur"""
    try:
        result = auth_manager.register(email, password, name)
        if result:
            return JSONResponse(content={
                "success": True,
                "user": result,
                "message": "Inscription réussie"
            })
        else:
            raise HTTPException(status_code=400, detail="Erreur lors de l'inscription")
    except Exception as e:
        logger.error(f"Erreur signup: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/auth/logout")
async def logout():
    """Déconnexion utilisateur"""
    try:
        auth_manager.logout()
        return JSONResponse(content={
            "success": True,
            "message": "Déconnexion réussie"
        })
    except Exception as e:
        logger.error(f"Erreur logout: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/user/profile")
async def get_profile():
    """Obtenir le profil utilisateur"""
    try:
        user = auth_manager.get_current_user()
        if user:
            stats = quota_manager.get_stats()
            return JSONResponse(content={
                "success": True,
                "user": user,
                "stats": stats
            })
        else:
            raise HTTPException(status_code=401, detail="Non authentifié")
    except Exception as e:
        logger.error(f"Erreur profile: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ========== MAIN ==========

if __name__ == "__main__":
    import sys
    
    # Fix encoding pour Windows
    if sys.platform == 'win32':
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    
    print("=" * 64)
    print("🚀 DIANA - Serveur Web")
    print("=" * 64)
    print(f"📱 Interface web : http://localhost:8000")
    print(f"📚 API Docs : http://localhost:8000/docs")
    print("🛑 Ctrl+C pour arrêter")
    print("=" * 64)
    
    uvicorn.run(app, host="0.0.0.0", port=8000)

