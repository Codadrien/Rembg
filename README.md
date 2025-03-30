# Remove Background GUI

Une application graphique pour supprimer le fond des images facilement.

## Fonctionnalités

- Interface graphique intuitive
- Support de plusieurs formats d'images (JPG, PNG, WebP, AVIF)
- Suppression automatique du fond
- Redimensionnement intelligent
- Sauvegarde en PNG ou WebP

## Prérequis

- Python 3.8 ou supérieur
- Node.js et npm (pour l'installation)

## Installation

1. Clonez le repository :
```bash
git clone https://github.com/votre-username/remove-bg-gui.git
cd remove-bg-gui
```

2. Installez les dépendances Python :
```bash
npm run install-deps
```

## Utilisation

1. Lancez l'application :
```bash
npm start
```

2. Cliquez sur "Choisir une image" pour sélectionner une image
3. L'application traitera automatiquement l'image
4. Cliquez sur "Sauvegarder" pour enregistrer le résultat

## Formats supportés

- Entrée : JPG, JPEG, PNG, BMP, GIF, WebP, AVIF
- Sortie : PNG, WebP

## Structure du projet

```
remove-bg-gui/
├── remove_bg_gui.py    # Application principale
├── remove_bg.py        # Module de traitement
├── requirements.txt    # Dépendances Python
├── package.json        # Configuration npm
└── README.md          # Documentation
```

## Licence

MIT

## Contribution

Les contributions sont les bienvenues ! N'hésitez pas à :
1. Fork le projet
2. Créer une branche pour votre fonctionnalité
3. Commiter vos changements
4. Pousser vers la branche
5. Ouvrir une Pull Request 