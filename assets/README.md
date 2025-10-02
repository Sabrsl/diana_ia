# Assets DIANA

Ce dossier contient les ressources graphiques de l'application.

## Fichiers requis

### Icônes

- `icon.ico` - Icône Windows (256x256, format ICO)
- `icon.icns` - Icône macOS (format ICNS)
- `icon.png` - Icône Linux (512x512, format PNG)

### Images

- `logo.png` - Logo de l'application
- `splash.png` - Écran de démarrage (optionnel)

## Génération des icônes

### À partir d'un PNG

```bash
# Windows ICO
convert icon.png -resize 256x256 icon.ico

# macOS ICNS
mkdir icon.iconset
sips -z 16 16     icon.png --out icon.iconset/icon_16x16.png
sips -z 32 32     icon.png --out icon.iconset/icon_16x16@2x.png
sips -z 32 32     icon.png --out icon.iconset/icon_32x32.png
sips -z 64 64     icon.png --out icon.iconset/icon_32x32@2x.png
sips -z 128 128   icon.png --out icon.iconset/icon_128x128.png
sips -z 256 256   icon.png --out icon.iconset/icon_128x128@2x.png
sips -z 256 256   icon.png --out icon.iconset/icon_256x256.png
sips -z 512 512   icon.png --out icon.iconset/icon_256x256@2x.png
sips -z 512 512   icon.png --out icon.iconset/icon_512x512.png
sips -z 1024 1024 icon.png --out icon.iconset/icon_512x512@2x.png
iconutil -c icns icon.iconset
```

## Recommandations de design

- **Style** : Moderne, médical, professionnel
- **Couleurs** : Bleu (#89b4fa), vert (#a6e3a1), blanc
- **Format** : Vectoriel si possible (SVG)
- **Taille** : Au moins 512x512 pour une qualité optimale

## Outils recommandés

- **Figma** - Design d'interface
- **GIMP** - Édition d'images
- **Inkscape** - Design vectoriel
- **ImageMagick** - Conversion de formats

