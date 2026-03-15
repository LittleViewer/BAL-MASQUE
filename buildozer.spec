[app]

# 🎭 Bal Masqué — Configuration Buildozer pour Android
title = Bal Masqué
package.name = balmasque
package.domain = org.comenottaris
source.dir = .
source.include_exts = py,png,jpg,kv,xml
source.exclude_dirs = tests,.github,screenshots,__pycache__,.git,venv,env,build,dist,docs
version = 2.2
requirements = python3,kivy==2.3.0,pillow,numpy,opencv,cython,pyjnius
orientation = portrait
fullscreen = 0

# Point d'entrée
entrypoint = bal_masque_mobile.py

# Icône et logo
icon.filename = logo.png
presplash.filename = logo.png

# ── Android ─────────────────────────────────────────────────────────

# Versions Android (minapi/ndk_api >= 24 requis pour numpy)
android.api = 34
android.minapi = 24
android.ndk = 25b
android.ndk_api = 24
android.accept_sdk_license = True

# Utiliser la branche develop de p4a pour les correctifs Python 3.11
# (corrige notamment l'erreur 'undeclared name: long' dans pyjnius)
p4a.branch = develop

# Architecture : arm64 + arm pour compatibilité large
android.archs = arm64-v8a, armeabi-v7a

# Permissions requises
android.permissions = READ_EXTERNAL_STORAGE, WRITE_EXTERNAL_STORAGE, READ_MEDIA_IMAGES

# Intent filter pour le bouton "Partager avec"
android.manifest.intent_filters = intent_filter.xml

# Thème Material sombre
android.theme = @android:style/Theme.Material.NoActionBar

# Inclure les fichiers cascade OpenCV pour la détection de visages
android.add_src = cascades

# Gradle dependencies pour FileProvider (partage d'images)
android.gradle_dependencies = androidx.core:core:1.12.0

# Empêcher la mise en veille pendant le traitement
android.wakelock = False

# Sécurité : désactiver la sauvegarde cloud (protection vie privée)
android.allow_backup = False

# Copier les cascades Haar dans l'APK
android.add_aars =
android.add_jars =

# ── Build ────────────────────────────────────────────────────────────

# Mode de build
build_mode = release

# Logs
log_level = 2

[buildozer]
log_level = 2
warn_on_root = 1
