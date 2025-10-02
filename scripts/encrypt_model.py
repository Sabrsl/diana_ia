"""
DIANA - Script de chiffrement du modèle
Utilitaire pour chiffrer le modèle ONNX avant distribution
"""

import sys
from pathlib import Path

# Ajouter le répertoire parent au path
sys.path.insert(0, str(Path(__file__).parent.parent))

import config
from src.encryption_manager import EncryptionManager


def main():
    """Chiffre un modèle ONNX"""
    print("=" * 60)
    print("DIANA - Chiffrement de modèle ONNX")
    print("=" * 60)
    
    # Demander le chemin du modèle source
    model_path = input("\nChemin du modèle ONNX à chiffrer: ").strip()
    
    if not model_path:
        print("❌ Aucun chemin spécifié")
        return
    
    model_path = Path(model_path)
    
    if not model_path.exists():
        print(f"❌ Fichier introuvable: {model_path}")
        return
    
    if not model_path.suffix == '.onnx':
        print("⚠️  Attention: Le fichier n'a pas l'extension .onnx")
        confirm = input("Continuer quand même ? (o/n): ").strip().lower()
        if confirm != 'o':
            return
    
    # Demander le chemin de sortie
    output_path = input(f"Chemin de sortie (défaut: {config.MODEL_ENCRYPTED_PATH}): ").strip()
    
    if not output_path:
        output_path = config.MODEL_ENCRYPTED_PATH
    else:
        output_path = Path(output_path)
    
    # Créer le dossier de sortie si nécessaire
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    print(f"\n📁 Source: {model_path}")
    print(f"📁 Destination: {output_path}")
    print(f"🔑 Clé de chiffrement: {'*' * 20}...")
    
    confirm = input("\nLancer le chiffrement ? (o/n): ").strip().lower()
    
    if confirm != 'o':
        print("❌ Opération annulée")
        return
    
    # Chiffrer le modèle
    print("\n🔐 Chiffrement en cours...")
    
    encryption_manager = EncryptionManager()
    success = encryption_manager.encrypt_file(model_path, output_path)
    
    if success:
        print(f"✅ Modèle chiffré avec succès !")
        print(f"📊 Taille: {output_path.stat().st_size / (1024*1024):.2f} MB")
        
        # Vérifier le fichier chiffré
        print("\n🔍 Vérification du fichier chiffré...")
        if encryption_manager.verify_encrypted_file(output_path):
            print("✅ Fichier valide et déchiffrable")
        else:
            print("⚠️  Attention: Le fichier chiffré semble invalide")
    else:
        print("❌ Échec du chiffrement")


if __name__ == "__main__":
    main()

