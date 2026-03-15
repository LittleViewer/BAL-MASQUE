# Bal Masque

**Logiciel libre de floutage de visages et de suppression de metadonnees**

![Version](https://img.shields.io/badge/version-2.2-ff2d55)
![Licence](https://img.shields.io/badge/licence-GPL--3.0-00e5a0)
![Python](https://img.shields.io/badge/python-3.8+-5cb8ff)
![Plateformes](https://img.shields.io/badge/plateformes-Windows%20%7C%20Linux%20%7C%20Mac%20%7C%20Android-blue)

---

## Description

**Bal Masque** est un outil de protection de la vie privee permettant de :
- **Flouter automatiquement ou manuellement** les visages sur vos photos
- **Supprimer les metadonnees** sensibles (GPS, EXIF, donnees d'identification)
- **Analyser la securite** de vos images avant partage

100% hors-ligne, 100% open-source, 0% de donnees envoyees.

---

## Fonctionnalites

### Floutage de visages
- **Detection automatique** des visages (OpenCV -- 3 classificateurs Haar, detection frontale + profils)
- **Marges de securite** de 25% autour des visages detectes
- **Mode manuel** pour selectionner des zones personnalisees
- **3 effets** : Pixelisation, Flou gaussien (double passe), Masque noir
- **Intensite reglable** (5-50)

### Suppression des metadonnees
- **Donnees GPS** : coordonnees, altitude, timestamp
- **Donnees EXIF** : appareil photo, parametres, logiciels
- **Donnees d'identification** : numeros de serie, identifiants uniques
- **Donnees XMP** : metadonnees etendues embarquees
- **Profils ICC** : profils couleur pouvant contenir des identifiants
- **Segments JPEG** : APP1, APP2, APP12, APP13, APP14, COM
- **Analyse de securite** : rapport detaille avec score de risque (0-100)

### Export
- Formats **PNG/JPEG/WebP** haute qualite
- **Suppression automatique** des metadonnees a la sauvegarde
- **Previsualisation** en temps reel

### Version mobile (Android)
- **Application autonome** ou **extension de partage** (bouton "Partager avec")
- Interface tactile adaptee aux smartphones
- Compatible **Android 5.0+** (API 21 a 34)
- **Stockage scope** : utilise l'API MediaStore sur Android 10+ pour un acces conforme
- **Sauvegarde** dans le dossier Pictures/BalMasque
- **Partage** direct de l'image traitee
- **Aucune permission internet** : 100% hors-ligne, aucune donnee transmise
- **Nettoyage securise** : les fichiers temporaires sont ecrases avec des zeros avant suppression

---

## Telecharger

### Option 1 : Telecharger l'executable (recommande)

**Aucune installation requise !**

1. Allez dans **[Releases](../../releases)**
2. Telechargez la version correspondant a votre systeme :

| Plateforme | Fichier |
|---|---|
| Windows | `BalMasque_Windows.zip` |
| Linux (Ubuntu / Linux Mint) | `BalMasque_Linux.tar.gz` |
| macOS (Intel) | `BalMasque_Mac_Intel.tar.gz` |
| macOS (Apple Silicon) | `BalMasque_Mac_AppleSilicon.tar.gz` |
| Android | `BalMasque_Android.zip` |

**Windows** : Extraire le zip et lancer `BalMasque.exe`

**Linux** :
```bash
tar xzf BalMasque_Linux.tar.gz
chmod +x BalMasque
./BalMasque
```

**macOS** :
```bash
tar xzf BalMasque_Mac_Intel.tar.gz    # ou BalMasque_Mac_AppleSilicon.tar.gz
open BalMasque.app
```

**Android** :
1. Extraire `BalMasque_Android.zip`
2. Installer `BalMasque.apk` (activer "Sources inconnues" dans Parametres > Securite)
3. Ouvrir l'application directement **ou** partager une image depuis la galerie avec le bouton "Partager avec"
4. Compatible Android 5.0 (Lollipop) et superieur

### Option 2 : Depuis le code source

```bash
# Cloner le repo
git clone https://github.com/comenottaris/BAL-MASQUE.git
cd BAL-MASQUE

# Installer les dependances
pip install -r requirements.txt

# Sur Linux (Ubuntu/Mint), installer aussi tkinter :
# sudo apt-get install python3-tk

# Lancer l'application
python bal_masque.py
```

### Option 3 : Builder vous-meme avec PyInstaller

```bash
pip install -r requirements.txt
pip install pyinstaller

# Generer l'executable
pyinstaller --onefile --windowed --name "BalMasque" --add-data "logo.png:." bal_masque.py

# L'executable sera dans dist/BalMasque
```

---

## Utilisation

### Interface

![Interface d'accueil](screenshots/Accueil.png)
![Interface de retouche](screenshots/retouches.png)

### Etapes

1. **Ouvrir** une image -- `Ctrl+O` ou bouton "Ouvrir"
2. **Analyser** les metadonnees -- Onglet "Metadonnees"
3. **Detecter** les visages -- `Ctrl+D` ou bouton "Detecter"
4. **Parametrer** l'effet et l'intensite
5. **Masquer** -- Bouton "Appliquer"
6. **Nettoyer** les metadonnees -- Bouton "Supprimer metadonnees"
7. **Enregistrer** -- `Ctrl+S` ou bouton "Sauvegarder"

### Raccourcis clavier

| Raccourci | Action |
|-----------|--------|
| `Ctrl+O` | Ouvrir une image |
| `Ctrl+S` | Sauvegarder |
| `Ctrl+D` | Detecter les visages |
| `Ctrl+Z` | Annuler |
| `Ctrl+R` | Reinitialiser |

### Mode manuel

- **Dessiner** : Clic gauche + glisser
- **Annuler derniere zone** : `Ctrl+Z`
- **Tout effacer** : Bouton "Effacer zones"

---

## Aspects juridiques

### Droit a l'image

En France (et dans de nombreux pays) :

- Toute personne a un droit sur son image
- La publication d'une photo necessite le consentement des personnes reconnaissables
- Les personnes peuvent demander le retrait ou le floutage de leur image

**Exceptions** (selon contexte) :

- Evenements publics avec foule (manifestations, concerts...)
- Personnalites publiques dans l'exercice de leurs fonctions
- Images accessoires (personne non reconnaissable/non centrale)

### Bon usage

Ce logiciel est concu pour :

- Proteger la vie privee des personnes photographiees
- Respecter le droit a l'image
- Permettre la diffusion de photos d'evenements collectifs
- Proteger les sources et les personnes vulnerables

Il **ne doit PAS** etre utilise pour :

- Cacher des informations relevant de l'interet public
- Entraver le travail journalistique legitime
- Dissimuler des actes reprehensibles

---

## Technologies

- **Python 3.8+**
- **OpenCV** - Detection de visages (classificateurs Haar)
- **Pillow** - Manipulation d'images et metadonnees EXIF
- **Tkinter** - Interface graphique (version desktop)
- **Kivy** - Interface graphique (version mobile Android)
- **NumPy** - Traitement matriciel
- **Buildozer** - Compilation APK Android
- **PyInstaller** - Generation des executables desktop

---

## Arborescence du projet

```
BAL-MASQUE/
|-- bal_masque.py              # Code principal (desktop)
|-- bal_masque_mobile.py       # Version mobile Android (Kivy)
|-- buildozer.spec             # Configuration build Android
|-- intent_filter.xml          # Filtre d'intent Android (partage)
|-- logo.png                   # Logo de l'application
|-- requirements.txt           # Dependances Python (desktop)
|-- requirements-mobile.txt    # Dependances Python (mobile)
|-- tests/
|   +-- test_bal_masque.py     # Tests unitaires
|-- docs/                      # Documentation et wiki
|-- .github/
|   +-- workflows/
|       +-- release.yml        # Build & release multi-plateforme + APK
|-- screenshots/               # Captures d'ecran
|   |-- Accueil.png
|   +-- retouches.png
|-- README.md                  # Ce fichier
+-- LICENSE                    # Licence GPL-3.0
```

---

## Contribuer

Les contributions sont bienvenues !

1. **Fork** le projet
2. Creez une branche (`git checkout -b feature/amelioration`)
3. Committez (`git commit -m 'Ajout fonctionnalite X'`)
4. Push (`git push origin feature/amelioration`)
5. Ouvrez une **Pull Request**

### Idees de contributions

- [ ] Support video (floutage frame par frame)
- [ ] Detection de plaques d'immatriculation
- [ ] Mode batch (traiter plusieurs images)
- [ ] Reconnaissance faciale pour exclure certaines personnes
- [ ] Interface en ligne de commande (CLI)
- [ ] Localisation (traductions)

---

## Licence

**GPL-3.0** - Logiciel libre et open source

Vous etes libre de :

- Utiliser ce logiciel a toute fin
- Etudier et modifier le code
- Redistribuer des copies
- Redistribuer des versions modifiees

**Conditions** :

- Le code source doit rester disponible
- Les modifications doivent etre documentees
- La meme licence doit etre appliquee aux derives

Voir [LICENSE](LICENSE) pour plus de details.

---

## Credits et Remerciements

### Projets dont Bal Masque s'inspire

Ce projet n'aurait pas vu le jour sans le travail remarquable des projets suivants :

---

#### [BlurryFaces](https://github.com/asmaamirkhan/BlurryFaces) par [Asmaa Mirkhan](https://github.com/asmaamirkhan)

Outil de floutage automatique de visages utilisant OpenCV.

Bal Masque s'est largement inspire de l'approche de detection et de floutage de BlurryFaces pour implementer la detection multi-cascade des visages (frontale, alternative et profil) ainsi que l'application d'effets de flou.

- **Repository** : <https://github.com/asmaamirkhan/BlurryFaces>
- **Auteur** : Asmaa Mirkhan ([@asmaamirkhan](https://github.com/asmaamirkhan))
- **Licence** : MIT

---

#### [Metadata-Remover](https://github.com/Anish-M-code/Metadata-Remover) par [Anish M](https://github.com/Anish-M-code)

Outil de suppression de metadonnees pour proteger la vie privee (MRT -- Metadata Removal Tool).

Le module de nettoyage des metadonnees de Bal Masque s'inspire directement du travail d'Anish sur la suppression des donnees EXIF, GPS, XMP et des segments APP JPEG. Son approche structuree nous a guide dans l'implementation du systeme de scoring de risque et de la suppression multi-couches des metadonnees.

- **Repository** : <https://github.com/Anish-M-code/Metadata-Remover>
- **Auteur** : Anish M ([@Anish-M-code](https://github.com/Anish-M-code))
- **Licence** : GPL-3.0

---

### Bibliotheques et frameworks

| Projet | Role dans Bal Masque | Lien |
|--------|---------------------|------|
| **OpenCV** | Detection de visages via classificateurs Haar | [opencv.org](https://opencv.org) |
| **Pillow** | Lecture/ecriture d'images et extraction de metadonnees EXIF | [python-pillow.org](https://python-pillow.org) |
| **Kivy** | Interface graphique de la version Android | [kivy.org](https://kivy.org) |
| **NumPy** | Manipulation matricielle pour le traitement d'images | [numpy.org](https://numpy.org) |
| **Buildozer** | Compilation de l'application Android (APK) | [github.com/kivy/buildozer](https://github.com/kivy/buildozer) |
| **PyInstaller** | Generation des executables desktop (Windows, Linux, macOS) | [pyinstaller.org](https://pyinstaller.org) |

### Ressources et documentation

- **Guide d'autodefense numerique** - [guide.boum.org](https://guide.boum.org) - Ressources sur la securite numerique

### Typographie

- **Fonte Ouvrieres** - [typotheque.genderfluid.space](https://typotheque.genderfluid.space) - Police utilisee pour le logo

---

### Organisations qui defendent nos libertes numeriques

Un immense merci aux organisations qui luttent quotidiennement pour nos droits :

| Organisation | Description | Lien |
|--------------|-------------|------|
| **La Quadrature du Net** | Defense des libertes fondamentales dans l'environnement numerique | [laquadrature.net](https://www.laquadrature.net) |
| **Technopolice** | Observatoire des technologies policieres | [technopolice.fr](https://technopolice.fr) |
| **BOUM** | Guide d'autodefense numerique | [boum.org](https://boum.org) |
| **Exodus Privacy** | Analyse des trackers dans les applications | [exodus-privacy.eu.org](https://exodus-privacy.eu.org) |
| **Framasoft** | Education populaire et logiciels libres | [framasoft.org](https://framasoft.org) |
| **Nothing2Hide** | Protection des journalistes et activistes | [nothing2hide.org](https://nothing2hide.org) |
| **EFF** | Electronic Frontier Foundation | [eff.org](https://www.eff.org) |

---

## Contact et Support

- **Issues** : [Signaler un bug](../../issues)
- **Discussions** : [Forum](../../discussions)
- **Email** : siratton@pm.me

---

## Pourquoi ce projet ?

Dans un contexte de surveillance generalisee, de reconnaissance faciale deployee sans consentement, et de collecte massive de donnees personnelles, il est essentiel de disposer d'outils simples pour proteger notre vie privee et celle des autres.

**Bal Masque** est ne de ce besoin : permettre a chacun et chacune de partager des photos sans compromettre la securite des personnes qui y apparaissent.

> *"La vie privee n'est pas une question de 'si on n'a rien a cacher'. C'est une question de pouvoir choisir ce qu'on montre et a qui."*

---

<div align="center">

**Protegez la vie privee. Respectez le droit a l'image. Utilisez des logiciels libres.**

*Fait avec du code libre*

</div>
