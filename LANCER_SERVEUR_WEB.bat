@echo off
chcp 65001 >nul
:: DIANA - Lancer le serveur web

color 0A
echo ================================================================
echo   🌐 DIANA - SERVEUR WEB
echo ================================================================
echo.

:: Vérifier Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python n'est pas installé
    pause
    exit /b 1
)

:: Activer l'environnement
if exist "venv\Scripts\activate.bat" (
    echo ⚡ Activation de l'environnement...
    call venv\Scripts\activate.bat
) else (
    echo 📦 Création de l'environnement...
    python -m venv venv
    call venv\Scripts\activate.bat
)

:: Installer les dépendances
echo 📚 Installation des dépendances...
pip install -q -r requirements-web.txt
echo.

:: Vérifier si le modèle existe
if not exist "models\breast_cancer_model.onnx.enc" (
    echo.
    echo ⚠️  ATTENTION : Modèle ONNX introuvable
    echo ════════════════════════════════════════════════════════════
    echo.
    echo Pour utiliser DIANA, vous devez :
    echo 1. Placer votre modèle ONNX dans : models\breast_cancer_model.onnx
    echo 2. Le chiffrer avec : python scripts\encrypt_model.py
    echo.
    echo L'application va démarrer mais vous ne pourrez pas analyser
    echo d'images tant que le modèle n'est pas ajouté.
    echo.
    echo ════════════════════════════════════════════════════════════
    echo.
    timeout /t 5
)

:: Lancer le serveur
echo ================================================================
echo   🚀 LANCEMENT DU SERVEUR WEB
echo ================================================================
echo.
echo 📱 Ouvrez votre navigateur sur : http://localhost:8000
echo.
echo 🔗 Pour accéder depuis un autre appareil :
echo    http://[VOTRE_IP]:8000
echo.
echo 🛑 Appuyez sur Ctrl+C pour arrêter le serveur
echo.
echo ================================================================
echo.

python web_app.py

pause

