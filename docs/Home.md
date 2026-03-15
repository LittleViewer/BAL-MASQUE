# 🎭 Bal Masqué — Wiki

> **[Version française ci-dessous](#-bal-masqué--wiki-fr)**

---

## 🇬🇧 Bal Masqué — Wiki (EN)

### What is Bal Masqué?

Bal Masqué is a **privacy-first face anonymisation and metadata removal tool**. It detects faces in images and applies blurring effects to protect identities. It also strips all sensitive metadata (EXIF, GPS, XMP, ICC profiles) from images before sharing.

**100% offline — No data ever leaves your device.**

### Platforms

| Platform | Technology | Status |
|----------|-----------|--------|
| 🪟 Windows | Python / Tkinter / PyInstaller | ✅ Supported |
| 🐧 Linux | Python / Tkinter / PyInstaller | ✅ Supported |
| 🍎 macOS (Intel) | Python / Tkinter / PyInstaller | ✅ Supported |
| 🍎 macOS (Apple Silicon) | Python / Tkinter / PyInstaller | ✅ Supported |
| 🤖 Android (5.0+) | Python / Kivy / Buildozer | ✅ Supported |

### Features

- **Automatic face detection** using OpenCV Haar cascades (3 classifiers: frontal, alternative, profile)
- **3 blur effects**: Pixelisation, Gaussian blur, Black mask
- **Adjustable intensity** (5–50 slider)
- **Complete metadata removal**: EXIF, GPS coordinates, XMP, ICC profiles, IPTC, JPEG APP segments
- **Risk scoring**: Analyses image metadata and assigns a privacy risk score (0–100)
- **Secure cleanup**: Overwrites temporary files with zeros before deletion
- **Android share integration**: Appears in the "Share with" menu for images

### Installation

#### From release (recommended)

Download the latest release from the [Releases page](https://github.com/comenottaris/BAL-MASQUE/releases):

- **Windows**: Extract the ZIP and run `BalMasque.exe`
- **Linux**: Extract the tarball, `chmod +x BalMasque`, then run `./BalMasque`
- **macOS**: Extract the tarball, then `open BalMasque.app`
- **Android**: Extract the ZIP, enable "Unknown sources" in Settings, install the APK

#### From source

```bash
git clone https://github.com/comenottaris/BAL-MASQUE.git
cd BAL-MASQUE
pip install -r requirements.txt
python bal_masque.py
```

### Usage

1. **Open** an image (drag & drop or file picker)
2. **Detect** faces (automatic detection with 25% margin expansion)
3. **Blur** detected faces (choose effect and intensity)
4. **Save** the anonymised image (metadata is automatically stripped)

### Keyboard shortcuts (Desktop)

| Shortcut | Action |
|----------|--------|
| `Ctrl+O` | Open image |
| `Ctrl+D` | Detect faces |
| `Ctrl+B` | Apply blur |
| `Ctrl+S` | Save image |
| `Ctrl+Z` | Undo |
| `Ctrl+M` | Show metadata |

### Android security

The Android app is configured for safe sideloading:

- **No internet permission**: The app is fully offline, no data is transmitted
- **Scoped storage**: Uses MediaStore API on Android 10+ for proper storage access
- **Backup disabled**: `android:allowBackup="false"` prevents cloud backup of processed images
- **Minimal permissions**: Only `READ_EXTERNAL_STORAGE`, `WRITE_EXTERNAL_STORAGE`, and `READ_MEDIA_IMAGES`
- **Secure cleanup**: Temporary files are overwritten with zeros before deletion
- **Target API 34**: Compatible with Android 14 security requirements

### Project structure

```
BAL-MASQUE/
├── bal_masque.py            # Desktop application (Tkinter)
├── bal_masque_mobile.py     # Android application (Kivy)
├── buildozer.spec           # Android build configuration
├── intent_filter.xml        # Android share intent filter
├── requirements.txt         # Desktop dependencies
├── requirements-mobile.txt  # Mobile dependencies
├── logo.png                 # Application icon
├── tests/
│   └── test_bal_masque.py   # Unit tests
├── docs/                    # Documentation / Wiki
├── screenshots/             # UI screenshots
└── .github/workflows/
    └── release.yml          # CI/CD pipeline
```

### License

GPL-3.0 — Free and open-source software.

---

## 🇫🇷 Bal Masqué — Wiki (FR)

### Qu'est-ce que Bal Masqué ?

Bal Masqué est un **outil militant d'anonymisation des visages et de suppression des métadonnées**. Il détecte les visages dans les images et applique des effets de flou pour protéger les identités. Il supprime également toutes les métadonnées sensibles (EXIF, GPS, XMP, profils ICC) des images avant leur partage.

**100% hors-ligne — Aucune donnée ne quitte jamais votre appareil.**

### Plateformes

| Plateforme | Technologie | Statut |
|-----------|------------|--------|
| 🪟 Windows | Python / Tkinter / PyInstaller | ✅ Supporté |
| 🐧 Linux | Python / Tkinter / PyInstaller | ✅ Supporté |
| 🍎 macOS (Intel) | Python / Tkinter / PyInstaller | ✅ Supporté |
| 🍎 macOS (Apple Silicon) | Python / Tkinter / PyInstaller | ✅ Supporté |
| 🤖 Android (5.0+) | Python / Kivy / Buildozer | ✅ Supporté |

### Fonctionnalités

- **Détection automatique des visages** via OpenCV Haar cascades (3 classificateurs : frontal, alternatif, profil)
- **3 effets de flou** : Pixelisation, Flou gaussien, Masque noir
- **Intensité réglable** (curseur 5–50)
- **Suppression complète des métadonnées** : EXIF, coordonnées GPS, XMP, profils ICC, IPTC, segments APP JPEG
- **Score de risque** : Analyse les métadonnées et attribue un score de risque vie privée (0–100)
- **Nettoyage sécurisé** : Écrase les fichiers temporaires avec des zéros avant suppression
- **Intégration partage Android** : Apparaît dans le menu « Partager avec » pour les images

### Installation

#### Depuis les releases (recommandé)

Téléchargez la dernière version depuis la [page des Releases](https://github.com/comenottaris/BAL-MASQUE/releases) :

- **Windows** : Extraire le ZIP et lancer `BalMasque.exe`
- **Linux** : Extraire l'archive, `chmod +x BalMasque`, puis `./BalMasque`
- **macOS** : Extraire l'archive, puis `open BalMasque.app`
- **Android** : Extraire le ZIP, activer « Sources inconnues » dans les paramètres, installer l'APK

#### Depuis les sources

```bash
git clone https://github.com/comenottaris/BAL-MASQUE.git
cd BAL-MASQUE
pip install -r requirements.txt
python bal_masque.py
```

### Utilisation

1. **Ouvrir** une image (glisser-déposer ou sélecteur de fichier)
2. **Détecter** les visages (détection automatique avec élargissement de 25%)
3. **Flouter** les visages détectés (choisir l'effet et l'intensité)
4. **Sauvegarder** l'image anonymisée (les métadonnées sont automatiquement supprimées)

### Raccourcis clavier (Bureau)

| Raccourci | Action |
|-----------|--------|
| `Ctrl+O` | Ouvrir une image |
| `Ctrl+D` | Détecter les visages |
| `Ctrl+B` | Appliquer le flou |
| `Ctrl+S` | Sauvegarder l'image |
| `Ctrl+Z` | Annuler |
| `Ctrl+M` | Afficher les métadonnées |

### Sécurité Android

L'application Android est configurée pour une installation sécurisée en sideloading :

- **Aucune permission internet** : L'application est entièrement hors-ligne, aucune donnée n'est transmise
- **Stockage scopé** : Utilise l'API MediaStore sur Android 10+ pour un accès au stockage conforme
- **Sauvegarde désactivée** : `android:allowBackup="false"` empêche la sauvegarde cloud des images traitées
- **Permissions minimales** : Uniquement `READ_EXTERNAL_STORAGE`, `WRITE_EXTERNAL_STORAGE` et `READ_MEDIA_IMAGES`
- **Nettoyage sécurisé** : Les fichiers temporaires sont écrasés avec des zéros avant suppression
- **API cible 34** : Compatible avec les exigences de sécurité d'Android 14

### Structure du projet

```
BAL-MASQUE/
├── bal_masque.py            # Application bureau (Tkinter)
├── bal_masque_mobile.py     # Application Android (Kivy)
├── buildozer.spec           # Configuration build Android
├── intent_filter.xml        # Filtre d'intent partage Android
├── requirements.txt         # Dépendances bureau
├── requirements-mobile.txt  # Dépendances mobile
├── logo.png                 # Icône de l'application
├── tests/
│   └── test_bal_masque.py   # Tests unitaires
├── docs/                    # Documentation / Wiki
├── screenshots/             # Captures d'écran
└── .github/workflows/
    └── release.yml          # Pipeline CI/CD
```

### Licence

GPL-3.0 — Logiciel libre et open-source.
