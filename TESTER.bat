@echo off
chcp 65001 >nul
cls

echo.
echo ════════════════════════════════════════════════════════════
echo                    🧪 TEST DIANA
echo ════════════════════════════════════════════════════════════
echo.
echo Choisissez la version à tester :
echo.
echo   1. 🖥️  Version Desktop (PyQt6)
echo   2. 🌐 Version Web (navigateur)
echo   3. ❌ Annuler
echo.
echo ════════════════════════════════════════════════════════════
echo.

set /p choice="Votre choix (1-3) : "

if "%choice%"=="1" goto desktop
if "%choice%"=="2" goto web
if "%choice%"=="3" goto end

echo Choix invalide !
timeout /t 2
goto end

:desktop
cls
echo.
echo ════════════════════════════════════════════════════════════
echo              🖥️  LANCEMENT VERSION DESKTOP
echo ════════════════════════════════════════════════════════════
echo.
echo ⏳ Activation de l'environnement virtuel...
call venv\Scripts\activate.bat
echo.
echo 🚀 Lancement de l'application...
echo.
python main.py
goto end

:web
cls
echo.
echo ════════════════════════════════════════════════════════════
echo                🌐 LANCEMENT VERSION WEB
echo ════════════════════════════════════════════════════════════
echo.
echo ⏳ Activation de l'environnement virtuel...
call venv\Scripts\activate.bat
echo.
echo 🚀 Démarrage du serveur...
echo.
echo 📱 Ouvrez votre navigateur sur : http://localhost:8000
echo 🛑 Appuyez sur Ctrl+C pour arrêter
echo.
python web_app.py
goto end

:end
echo.
pause

