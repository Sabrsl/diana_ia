"""
DIANA - Script de build
Génère les exécutables pour différentes plateformes avec PyInstaller
"""

import sys
import os
import platform
import subprocess
from pathlib import Path


def get_platform_config():
    """Retourne la configuration pour la plateforme actuelle"""
    system = platform.system()
    
    if system == "Windows":
        return {
            "name": "DIANA.exe",
            "icon": "assets/icon.ico",
            "separator": ";",
            "hidden_imports": [
                "PyQt6.QtCore",
                "PyQt6.QtGui",
                "PyQt6.QtWidgets",
                "onnxruntime",
                "supabase",
                "cryptography"
            ]
        }
    elif system == "Darwin":  # macOS
        return {
            "name": "DIANA.app",
            "icon": "assets/icon.icns",
            "separator": ":",
            "hidden_imports": [
                "PyQt6.QtCore",
                "PyQt6.QtGui",
                "PyQt6.QtWidgets",
                "onnxruntime",
                "supabase",
                "cryptography"
            ]
        }
    else:  # Linux
        return {
            "name": "DIANA",
            "icon": "assets/icon.png",
            "separator": ":",
            "hidden_imports": [
                "PyQt6.QtCore",
                "PyQt6.QtGui",
                "PyQt6.QtWidgets",
                "onnxruntime",
                "supabase",
                "cryptography"
            ]
        }


def build_executable():
    """Construit l'exécutable avec PyInstaller"""
    print("=" * 60)
    print("DIANA - Build de l'application")
    print("=" * 60)
    
    # Récupérer la configuration
    config = get_platform_config()
    
    print(f"\n🖥️  Plateforme: {platform.system()}")
    print(f"📦 Exécutable: {config['name']}")
    
    # Préparer les arguments PyInstaller
    args = [
        "pyinstaller",
        "--name=DIANA",
        "--onefile",  # Un seul fichier
        "--windowed",  # Pas de console (GUI)
        f"--icon={config['icon']}" if Path(config['icon']).exists() else "",
        
        # Ajouter les données nécessaires
        "--add-data=models{sep}models".format(sep=config['separator']),
        "--add-data=.env{sep}.".format(sep=config['separator']),
        
        # Hidden imports
        *[f"--hidden-import={imp}" for imp in config['hidden_imports']],
        
        # Optimisations
        "--strip",  # Retirer les symboles de debug
        "--clean",  # Nettoyer avant build
        
        # Point d'entrée
        "main.py"
    ]
    
    # Filtrer les arguments vides
    args = [arg for arg in args if arg]
    
    print(f"\n🔨 Commande PyInstaller:")
    print(" ".join(args))
    
    confirm = input("\n📦 Lancer le build ? (o/n): ").strip().lower()
    
    if confirm != 'o':
        print("❌ Build annulé")
        return
    
    # Lancer PyInstaller
    print("\n🚀 Build en cours...\n")
    
    try:
        result = subprocess.run(args, check=True)
        
        print("\n✅ Build terminé avec succès !")
        print(f"📁 Exécutable disponible dans: dist/{config['name']}")
        
        # Afficher la taille
        dist_path = Path("dist") / config['name']
        if dist_path.exists():
            size_mb = dist_path.stat().st_size / (1024 * 1024)
            print(f"📊 Taille: {size_mb:.2f} MB")
        
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Erreur lors du build: {e}")
        sys.exit(1)


def main():
    """Fonction principale"""
    # Vérifier que nous sommes à la racine du projet
    if not Path("main.py").exists():
        print("❌ Erreur: Ce script doit être exécuté depuis la racine du projet")
        sys.exit(1)
    
    # Vérifier que PyInstaller est installé
    try:
        subprocess.run(["pyinstaller", "--version"], 
                      capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ PyInstaller n'est pas installé")
        print("💡 Installez-le avec: pip install pyinstaller")
        sys.exit(1)
    
    # Lancer le build
    build_executable()


if __name__ == "__main__":
    main()

