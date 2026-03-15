# 🔒 Security / Sécurité

> **[Version française ci-dessous](#-sécurité-android-fr)**

---

## 🇬🇧 Android Security (EN)

### Privacy by design

Bal Masqué is designed as a **privacy-first tool**. The core principle is that **no data ever leaves the device**:

- ❌ No internet permission — the app cannot make network connections
- ❌ No analytics or telemetry
- ❌ No cloud services
- ✅ All processing happens locally on-device
- ✅ Temporary files are overwritten with zeros before deletion
- ✅ Image arrays are zeroed-out in memory on app pause/stop

### Permissions

| Permission | Purpose | Android version |
|-----------|---------|----------------|
| `READ_EXTERNAL_STORAGE` | Read images from gallery | Android 5–12 |
| `WRITE_EXTERNAL_STORAGE` | Save processed images | Android 5–9 |
| `READ_MEDIA_IMAGES` | Read images from gallery | Android 13+ |

**Note:** On Android 10+, the app uses the **MediaStore API** (scoped storage) for saving images, so `WRITE_EXTERNAL_STORAGE` is not used on modern devices.

### Data handling

| Data type | Handling |
|----------|---------|
| Original images | Read-only, never modified |
| Processed images | Saved to `Pictures/BalMasque/` via MediaStore |
| Temporary files | Overwritten with zeros, then deleted |
| Metadata (EXIF, GPS, XMP) | Stripped completely before saving |
| App state | Not persisted, not backed up |

### Manifest security settings

| Setting | Value | Purpose |
|---------|-------|---------|
| `android:allowBackup` | `false` | Prevents cloud backup of app data |
| `android:usesCleartextTraffic` | N/A | No INTERNET permission, not needed |
| `android:targetSdkVersion` | `34` | Android 14 compliance |
| `android:minSdkVersion` | `21` | Android 5.0 Lollipop minimum |

### Sideloading safety

The APK is safe to sideload (install from outside the Play Store):

1. **No dangerous permissions**: No access to contacts, camera, microphone, location, or internet
2. **Minimal attack surface**: Image processing only, no web views or dynamic code loading
3. **Open source**: Full source code available for audit (GPL-3.0)
4. **Signed APK**: Release builds are signed with a consistent key

### Reporting security issues

If you find a security vulnerability, please open a private issue or contact the maintainer directly.

---

## 🇫🇷 Sécurité Android (FR)

### Protection de la vie privée par conception

Bal Masqué est conçu comme un **outil axé sur la vie privée**. Le principe fondamental est qu'**aucune donnée ne quitte jamais l'appareil** :

- ❌ Aucune permission internet — l'application ne peut pas établir de connexion réseau
- ❌ Aucune analyse ni télémétrie
- ❌ Aucun service cloud
- ✅ Tout le traitement se fait localement sur l'appareil
- ✅ Les fichiers temporaires sont écrasés avec des zéros avant suppression
- ✅ Les tableaux d'images sont remis à zéro en mémoire lors de la pause/arrêt de l'application

### Permissions

| Permission | Usage | Version Android |
|-----------|-------|----------------|
| `READ_EXTERNAL_STORAGE` | Lire les images de la galerie | Android 5–12 |
| `WRITE_EXTERNAL_STORAGE` | Sauvegarder les images traitées | Android 5–9 |
| `READ_MEDIA_IMAGES` | Lire les images de la galerie | Android 13+ |

**Note :** Sur Android 10+, l'application utilise l'**API MediaStore** (stockage scopé) pour sauvegarder les images, `WRITE_EXTERNAL_STORAGE` n'est donc pas utilisé sur les appareils modernes.

### Traitement des données

| Type de données | Traitement |
|----------------|-----------|
| Images originales | Lecture seule, jamais modifiées |
| Images traitées | Sauvegardées dans `Pictures/BalMasque/` via MediaStore |
| Fichiers temporaires | Écrasés avec des zéros, puis supprimés |
| Métadonnées (EXIF, GPS, XMP) | Supprimées intégralement avant sauvegarde |
| État de l'application | Non persisté, non sauvegardé |

### Paramètres de sécurité du manifeste

| Paramètre | Valeur | Objectif |
|----------|--------|---------|
| `android:allowBackup` | `false` | Empêche la sauvegarde cloud des données de l'application |
| `android:usesCleartextTraffic` | N/A | Pas de permission INTERNET, pas nécessaire |
| `android:targetSdkVersion` | `34` | Conformité Android 14 |
| `android:minSdkVersion` | `21` | Minimum Android 5.0 Lollipop |

### Sécurité du sideloading

L'APK est sûr à installer en sideloading (hors Play Store) :

1. **Pas de permissions dangereuses** : Pas d'accès aux contacts, caméra, microphone, localisation ou internet
2. **Surface d'attaque minimale** : Traitement d'images uniquement, pas de vues web ni de chargement dynamique de code
3. **Open source** : Code source complet disponible pour audit (GPL-3.0)
4. **APK signé** : Les builds release sont signés avec une clé cohérente

### Signaler un problème de sécurité

Si vous trouvez une vulnérabilité de sécurité, veuillez ouvrir un ticket privé ou contacter le mainteneur directement.
