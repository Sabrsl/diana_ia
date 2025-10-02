"""
DIANA - Générateur de fichier latest.json
Crée automatiquement le fichier JSON pour les mises à jour
"""

import json
import hashlib
import sys
from pathlib import Path
from datetime import datetime


def calculate_checksum(file_path: Path, algorithm: str = 'sha256') -> str:
    """Calcule le checksum d'un fichier"""
    hash_func = hashlib.new(algorithm)
    
    with open(file_path, 'rb') as f:
        while chunk := f.read(8192):
            hash_func.update(chunk)
    
    return hash_func.hexdigest()


def get_file_size_mb(file_path: Path) -> float:
    """Retourne la taille du fichier en MB"""
    return file_path.stat().st_size / (1024 * 1024)


def generate_update_json(version: str, base_url: str, dist_dir: Path):
    """Génère le fichier latest.json"""
    
    print("=" * 60)
    print("DIANA - Génération de latest.json")
    print("=" * 60)
    
    platforms = {}
    
    # Fichiers à chercher
    files_to_check = {
        'windows': f'DIANA-{version}-Windows.exe',
        'darwin': f'DIANA-{version}-macOS.dmg',
        'linux': f'DIANA-{version}-Linux.AppImage'
    }
    
    for platform, filename in files_to_check.items():
        file_path = dist_dir / filename
        
        if file_path.exists():
            print(f"\n📦 {platform.upper()}")
            print(f"   Fichier: {filename}")
            
            checksum = calculate_checksum(file_path)
            size_mb = get_file_size_mb(file_path)
            
            print(f"   Taille: {size_mb:.2f} MB")
            print(f"   Checksum: {checksum[:16]}...")
            
            platforms[platform] = {
                "download_url": f"{base_url}/releases/{version}/{filename}",
                "checksum": checksum,
                "size_mb": round(size_mb, 2)
            }
        else:
            print(f"\n⚠️  {platform.upper()}: {filename} non trouvé")
    
    if not platforms:
        print("\n❌ Aucun fichier trouvé dans dist/")
        return None
    
    # Demander les notes de version
    print("\n" + "=" * 60)
    print("Notes de version (tapez 'END' sur une ligne vide pour terminer):")
    release_notes_lines = []
    while True:
        line = input()
        if line.strip() == 'END':
            break
        release_notes_lines.append(line)
    
    release_notes = "\n".join(release_notes_lines)
    
    # Créer le JSON
    update_data = {
        "version": version,
        "release_date": datetime.now().strftime("%Y-%m-%d"),
        "platforms": platforms,
        "checksum_algorithm": "sha256",
        "release_notes": release_notes,
        "min_version": "1.0.0",
        "critical_update": False
    }
    
    return update_data


def main():
    """Fonction principale"""
    
    # Demander la version
    version = input("\nVersion (ex: 1.0.0): ").strip()
    if not version:
        print("❌ Version requise")
        return
    
    # Demander l'URL de base
    base_url = input("URL de base (ex: https://updates.diana-ai.com): ").strip()
    if not base_url:
        print("❌ URL de base requise")
        return
    
    # Demander le dossier dist
    dist_dir = input("Dossier dist (défaut: dist): ").strip()
    if not dist_dir:
        dist_dir = "dist"
    
    dist_dir = Path(dist_dir)
    
    if not dist_dir.exists():
        print(f"❌ Dossier introuvable: {dist_dir}")
        return
    
    # Générer le JSON
    update_data = generate_update_json(version, base_url, dist_dir)
    
    if not update_data:
        return
    
    # Sauvegarder
    output_file = dist_dir / "latest.json"
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(update_data, f, indent=2, ensure_ascii=False)
    
    print("\n" + "=" * 60)
    print(f"✅ Fichier créé: {output_file}")
    print("\nContenu:")
    print("=" * 60)
    print(json.dumps(update_data, indent=2, ensure_ascii=False))
    print("=" * 60)


if __name__ == "__main__":
    main()

