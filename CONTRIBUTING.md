# 🤝 Contribution à DIANA

Merci de votre intérêt pour contribuer à DIANA !

## ⚠️ Important

DIANA est un logiciel **propriétaire** à usage médical. Les contributions sont limitées aux membres autorisés de l'équipe de développement.

## 📝 Guide de contribution (équipe interne)

### Workflow Git

1. **Créer une branche**

```bash
git checkout -b feature/nom-de-la-fonctionnalite
```

Convention de nommage :
- `feature/` - Nouvelle fonctionnalité
- `bugfix/` - Correction de bug
- `hotfix/` - Correction urgente
- `refactor/` - Refactorisation
- `docs/` - Documentation

2. **Développer**

- Suivre les conventions de code Python (PEP 8)
- Ajouter des tests pour toute nouvelle fonctionnalité
- Documenter le code avec des docstrings
- Commiter régulièrement avec des messages clairs

3. **Tester**

```bash
# Tests unitaires
pytest tests/

# Linting
flake8 src/
black src/ --check

# Type checking
mypy src/
```

4. **Créer une Pull Request**

- Description claire des changements
- Référencer les issues liées
- S'assurer que tous les tests passent
- Demander une revue de code

### Conventions de code

#### Python

```python
"""
Module docstring expliquant le but du module
"""

import standard_library
import third_party
import local_module


class MyClass:
    """Docstring de la classe"""
    
    def __init__(self):
        """Initialisation"""
        self.attribute = None
    
    def my_method(self, param: str) -> bool:
        """
        Description de la méthode
        
        Args:
            param: Description du paramètre
            
        Returns:
            Description du retour
        """
        pass
```

#### Commits

Format :
```
type(scope): description courte

Description détaillée si nécessaire

Références: #123
```

Types :
- `feat` - Nouvelle fonctionnalité
- `fix` - Correction de bug
- `docs` - Documentation
- `style` - Formatage
- `refactor` - Refactorisation
- `test` - Tests
- `chore` - Maintenance

Exemples :
```
feat(auth): ajout de l'authentification Google OAuth

fix(inference): correction du preprocessing des images DICOM

docs(readme): mise à jour des instructions d'installation
```

### Tests

#### Tests unitaires

```python
import pytest

def test_function_name():
    """Test de la fonction"""
    # Arrange
    expected = True
    
    # Act
    result = my_function()
    
    # Assert
    assert result == expected
```

#### Tests d'intégration

```python
@pytest.mark.integration
def test_full_workflow():
    """Test du workflow complet"""
    # Test end-to-end
    pass
```

### Documentation

- Documenter toutes les fonctions publiques
- Mettre à jour README.md si nécessaire
- Ajouter des exemples d'utilisation
- Documenter les breaking changes

## 🔐 Sécurité

### Reporting de vulnérabilités

**NE PAS** créer d'issue publique pour les vulnérabilités de sécurité.

Envoyer un email à : security@diana-ai.com

Inclure :
- Description de la vulnérabilité
- Steps to reproduce
- Impact potentiel
- Suggestion de correction (optionnel)

### Données sensibles

**JAMAIS** commiter :
- Clés API
- Mots de passe
- Tokens
- Données patients
- Modèles non chiffrés
- Fichiers `.env`

## 📋 Checklist avant PR

- [ ] Code testé localement
- [ ] Tests unitaires ajoutés/mis à jour
- [ ] Tests passent (`pytest`)
- [ ] Code formaté (`black`)
- [ ] Linting OK (`flake8`)
- [ ] Documentation mise à jour
- [ ] Changelog mis à jour
- [ ] Pas de données sensibles
- [ ] Commit messages suivent la convention

## 🎨 Standards UI

### Thèmes

Utiliser les couleurs Catppuccin :
- Dark theme : Mocha
- Light theme : Latte

### Accessibilité

- Contraste minimum : 4.5:1
- Support du clavier
- Labels pour screen readers
- Tailles de police ajustables

## 📚 Ressources

- [PEP 8 - Style Guide](https://www.python.org/dev/peps/pep-0008/)
- [PyQt6 Documentation](https://doc.qt.io/qtforpython/)
- [ONNX Runtime](https://onnxruntime.ai/)
- [Supabase Docs](https://supabase.com/docs)

## 💬 Communication

- **Slack** : #diana-dev
- **Meetings** : Lundi 10h, Jeudi 15h
- **Email** : dev@diana-ai.com

## ❓ Questions

Pour toute question :
1. Vérifier la documentation
2. Chercher dans les issues existantes
3. Demander sur Slack #diana-dev
4. Contacter un lead developer

---

Merci de contribuer à DIANA ! 🏥💙

