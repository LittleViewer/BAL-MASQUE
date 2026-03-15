#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🎭 BAL MASQUÉ — Version Mobile
Outil militant d'anonymisation des visages et métadonnées
Adapté pour smartphones Android — Fonctionne comme extension de partage
Licence GPL-3.0
"""

import os
import struct
import re
import shutil
import tempfile
import gc
from datetime import datetime
from pathlib import Path

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.slider import Slider
from kivy.uix.image import Image as KivyImage
from kivy.uix.popup import Popup
from kivy.uix.spinner import Spinner
from kivy.uix.scrollview import ScrollView
from kivy.core.window import Window
from kivy.graphics.texture import Texture
from kivy.clock import Clock
from kivy.utils import platform
from kivy.properties import (
    ObjectProperty, StringProperty, NumericProperty, BooleanProperty
)
from kivy.lang import Builder
from kivy.cache import Cache

import numpy as np
import cv2
from PIL import Image as PILImage
from PIL.ExifTags import TAGS, GPSTAGS


# ── Interface Kivy ──────────────────────────────────────────────────

KV_LAYOUT = '''
#:import dp kivy.metrics.dp
#:import sp kivy.metrics.sp

<RoundedBtn@Button>:
    size_hint_y: None
    height: dp(50)
    background_color: 0, 0, 0, 0
    background_normal: ''
    color: 1, 1, 1, 1
    font_size: sp(15)
    bold: True
    canvas.before:
        Color:
            rgba: self._bg if hasattr(self, '_bg') else (0.14, 0.14, 0.22, 1)
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [dp(12)]

<StepBtn@RoundedBtn>:
    _bg: 0.14, 0.14, 0.22, 1

<AccentBtn@RoundedBtn>:
    _bg: 1, 0.18, 0.33, 1

<GreenBtn@RoundedBtn>:
    _bg: 0, 0.75, 0.53, 1
    color: 1, 1, 1, 1

<RootLayout>:
    orientation: 'vertical'
    padding: dp(12)
    spacing: dp(8)
    canvas.before:
        Color:
            rgba: 0.05, 0.05, 0.09, 1
        Rectangle:
            pos: self.pos
            size: self.size

    # ─── Barre de titre ───
    BoxLayout:
        size_hint_y: None
        height: dp(40)
        spacing: dp(8)
        canvas.before:
            Color:
                rgba: 0.08, 0.08, 0.14, 1
            RoundedRectangle:
                pos: self.pos
                size: self.size
                radius: [dp(10)]
        Label:
            text: '  🎭  Bal Masqué'
            font_size: sp(19)
            bold: True
            color: 1, 0.18, 0.33, 1
            halign: 'left'
            text_size: self.size
            valign: 'center'
        Label:
            text: 'v2.2  '
            font_size: sp(12)
            color: 0.45, 0.45, 0.55, 1
            size_hint_x: 0.25
            halign: 'right'
            text_size: self.size
            valign: 'center'

    # ─── Zone image (occupe tout l'espace disponible) ───
    BoxLayout:
        canvas.before:
            Color:
                rgba: 0.08, 0.08, 0.14, 1
            RoundedRectangle:
                pos: self.pos
                size: self.size
                radius: [dp(14)]

        # Image ou message d'accueil
        FloatLayout:
            Image:
                id: image_display
                allow_stretch: True
                keep_ratio: True
                pos_hint: {'center_x': .5, 'center_y': .5}
                size_hint: 1, 1

            Label:
                id: welcome_label
                text: '📷  Ouvrez une image\\nou partagez-en une depuis votre galerie\\n\\n⬇  Utilisez les boutons ci-dessous'
                font_size: sp(16)
                color: 0.5, 0.5, 0.6, 1
                halign: 'center'
                valign: 'center'
                text_size: self.size
                pos_hint: {'center_x': .5, 'center_y': .5}
                size_hint: 1, 1

    # ─── Barre de statut ───
    BoxLayout:
        size_hint_y: None
        height: dp(32)
        padding: [dp(10), 0]
        canvas.before:
            Color:
                rgba: 0.08, 0.08, 0.14, 1
            RoundedRectangle:
                pos: self.pos
                size: self.size
                radius: [dp(8)]
        Label:
            id: status_label
            text: 'Prêt — Ouvrez ou partagez une image'
            font_size: sp(13)
            color: 0, 0.9, 0.63, 1
            halign: 'center'
            text_size: self.size
            valign: 'center'

    # ─── Ligne de workflow : étapes numérotées ───
    BoxLayout:
        size_hint_y: None
        height: dp(24)
        spacing: dp(4)
        Label:
            id: step1_lbl
            text: '① Ouvrir'
            font_size: sp(12)
            color: 1, 0.18, 0.33, 1
            bold: True
            halign: 'center'
            text_size: self.size
            valign: 'center'
        Label:
            text: '→'
            font_size: sp(12)
            color: 0.35, 0.35, 0.45, 1
            size_hint_x: 0.1
            halign: 'center'
            text_size: self.size
            valign: 'center'
        Label:
            id: step2_lbl
            text: '② Détecter'
            font_size: sp(12)
            color: 0.35, 0.35, 0.45, 1
            halign: 'center'
            text_size: self.size
            valign: 'center'
        Label:
            text: '→'
            font_size: sp(12)
            color: 0.35, 0.35, 0.45, 1
            size_hint_x: 0.1
            halign: 'center'
            text_size: self.size
            valign: 'center'
        Label:
            id: step3_lbl
            text: '③ Flouter'
            font_size: sp(12)
            color: 0.35, 0.35, 0.45, 1
            halign: 'center'
            text_size: self.size
            valign: 'center'
        Label:
            text: '→'
            font_size: sp(12)
            color: 0.35, 0.35, 0.45, 1
            size_hint_x: 0.1
            halign: 'center'
            text_size: self.size
            valign: 'center'
        Label:
            id: step4_lbl
            text: '④ Sauver'
            font_size: sp(12)
            color: 0.35, 0.35, 0.45, 1
            halign: 'center'
            text_size: self.size
            valign: 'center'

    # ─── Réglages : effet + intensité ───
    BoxLayout:
        size_hint_y: None
        height: dp(42)
        spacing: dp(8)
        padding: [dp(6), 0]
        canvas.before:
            Color:
                rgba: 0.08, 0.08, 0.14, 1
            RoundedRectangle:
                pos: self.pos
                size: self.size
                radius: [dp(10)]
        Label:
            text: '  Effet'
            font_size: sp(13)
            color: 0.6, 0.6, 0.7, 1
            size_hint_x: 0.18
            halign: 'left'
            text_size: self.size
            valign: 'center'
        Spinner:
            id: effect_spinner
            text: 'Pixelisation'
            values: ['Pixelisation', 'Flou gaussien', 'Masque noir']
            size_hint_x: 0.42
            font_size: sp(13)
            background_color: 0.14, 0.14, 0.22, 1
            background_normal: ''
            color: 1, 1, 1, 1
        Label:
            text: 'Force'
            font_size: sp(13)
            color: 0.6, 0.6, 0.7, 1
            size_hint_x: 0.13
            halign: 'right'
            text_size: self.size
            valign: 'center'
        Slider:
            id: intensity_slider
            min: 5
            max: 50
            value: 25
            step: 1
            size_hint_x: 0.2
            cursor_size: (dp(22), dp(22))
        Label:
            id: intensity_label
            text: '25'
            font_size: sp(13)
            color: 1, 0.18, 0.33, 1
            bold: True
            size_hint_x: 0.07

    # ─── Boutons principaux (2 rangées) ───
    BoxLayout:
        size_hint_y: None
        height: dp(52)
        spacing: dp(8)
        StepBtn:
            text: '📂  Ouvrir'
            on_release: app.open_image()
        StepBtn:
            text: '👁  Détecter'
            on_release: app.detect_faces()
        AccentBtn:
            text: '🎭  Flouter'
            on_release: app.apply_blur()

    BoxLayout:
        size_hint_y: None
        height: dp(52)
        spacing: dp(8)
        GreenBtn:
            text: '💾  Sauvegarder'
            on_release: app.save_image()
        StepBtn:
            text: '📊  Infos'
            on_release: app.show_metadata()
        StepBtn:
            text: '↩  Annuler'
            on_release: app.undo()

    # ─── Bouton sécurité (nettoyage métadonnées) ───
    BoxLayout:
        size_hint_y: None
        height: dp(42)
        spacing: dp(8)
        AccentBtn:
            height: dp(42)
            text: '🧹  Nettoyer les métadonnées'
            on_release: app.clean_metadata()
        StepBtn:
            height: dp(42)
            size_hint_x: 0.35
            text: '🔒  Purger'
            on_release: app.manual_purge()
'''


# ── Gestionnaire de métadonnées (autonome, pas d'import du module desktop) ──

class MetadataManagerMobile:
    """Gestionnaire de métadonnées pour la version mobile"""

    SENSITIVE_TAGS = {
        'GPSInfo': '🌍 Position GPS',
        'GPSLatitude': '🌍 Latitude',
        'GPSLongitude': '🌍 Longitude',
        'GPSAltitude': '🌍 Altitude',
        'GPSTimeStamp': '🌍 Heure GPS',
        'GPSDateStamp': '🌍 Date GPS',
        'DateTime': '📅 Date/Heure',
        'DateTimeOriginal': '📅 Date originale',
        'DateTimeDigitized': '📅 Date numérisation',
        'Make': '📱 Fabricant',
        'Model': '📱 Modèle appareil',
        'Software': '💻 Logiciel',
        'HostComputer': '💻 Ordinateur',
        'Artist': '👤 Artiste',
        'Copyright': '©️ Copyright',
        'ImageUniqueID': '🔢 ID unique',
        'BodySerialNumber': '🔢 N° série',
        'LensSerialNumber': '🔢 N° série objectif',
        'LensModel': '📷 Modèle objectif',
        'LensMake': '📷 Fabricant objectif',
        'CameraSerialNumber': '🔢 N° série caméra',
        'ImageDescription': '📝 Description',
        'UserComment': '📝 Commentaire',
        'XPAuthor': '👤 Auteur XP',
        'XPComment': '📝 Commentaire XP',
        'XPKeywords': '🏷️ Mots-clés XP',
    }

    @staticmethod
    def get_all_metadata(image_path):
        """Extraction complète des métadonnées"""
        result = {
            'exif': {},
            'gps': None,
            'sensibles': [],
            'all_tags': {},
            'file_info': {},
            'risk_score': 0,
            'hidden_data': []
        }

        try:
            stat = os.stat(image_path)
            result['file_info'] = {
                'Taille': f"{stat.st_size / 1024:.1f} Ko",
                'Modifié': datetime.fromtimestamp(stat.st_mtime).strftime('%d/%m/%Y %H:%M'),
                'Chemin': str(image_path)
            }

            img = PILImage.open(image_path)
            try:
                result['file_info']['Format'] = img.format
                result['file_info']['Dimensions'] = f"{img.size[0]}x{img.size[1]}"
                result['file_info']['Mode'] = img.mode

                exif_data = img._getexif()
                if exif_data:
                    for tag_id, value in exif_data.items():
                        tag_name = TAGS.get(tag_id, str(tag_id))

                        if tag_name == 'GPSInfo' and isinstance(value, dict):
                            gps_data = {}
                            for gps_tag_id, gps_value in value.items():
                                gps_tag_name = GPSTAGS.get(gps_tag_id, str(gps_tag_id))
                                gps_data[gps_tag_name] = gps_value

                            coords = MetadataManagerMobile._extract_gps_coords(gps_data)
                            if coords:
                                result['gps'] = coords
                                result['risk_score'] += 40

                        try:
                            if isinstance(value, bytes):
                                value = value.decode('utf-8', errors='replace')[:100]
                            result['all_tags'][tag_name] = str(value)[:200]
                        except Exception:
                            result['all_tags'][tag_name] = "[Binaire]"

                        if tag_name in MetadataManagerMobile.SENSITIVE_TAGS:
                            result['sensibles'].append({
                                'tag': tag_name,
                                'label': MetadataManagerMobile.SENSITIVE_TAGS[tag_name],
                                'value': str(value)[:100]
                            })
                            result['risk_score'] += 10
            finally:
                img.close()

            with open(image_path, 'rb') as f:
                binary_data = f.read()

            emails = re.findall(
                rb'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', binary_data
            )
            for email in emails[:5]:
                result['hidden_data'].append(
                    f"📧 Email: {email.decode('utf-8', errors='replace')}"
                )
                result['risk_score'] += 15

            urls = re.findall(rb'https?://[^\s<>"{}|\\^`\[\]]+', binary_data)
            for url in urls[:5]:
                result['hidden_data'].append(
                    f"🔗 URL: {url.decode('utf-8', errors='replace')[:60]}"
                )
                result['risk_score'] += 5

            if b'\xff\xd8\xff' in binary_data[20:]:
                result['hidden_data'].append("🖼️ Miniature EXIF embarquée détectée")
                result['risk_score'] += 20

            if b'<x:xmpmeta' in binary_data or b'xmlns:xmp' in binary_data:
                result['hidden_data'].append("📦 Métadonnées XMP embarquées détectées")
                result['risk_score'] += 15

            if b'ICC_PROFILE' in binary_data:
                result['hidden_data'].append("🎨 Profil ICC embarqué détecté")
                result['risk_score'] += 5

            result['risk_score'] = min(100, result['risk_score'])

        except Exception as e:
            result['error'] = str(e)

        return result

    @staticmethod
    def _extract_gps_coords(gps_data):
        try:
            def convert_to_degrees(value):
                if isinstance(value, tuple) and len(value) == 3:
                    d, m, s = float(value[0]), float(value[1]), float(value[2])
                    return d + (m / 60.0) + (s / 3600.0)
                return None

            lat = convert_to_degrees(gps_data.get('GPSLatitude'))
            lon = convert_to_degrees(gps_data.get('GPSLongitude'))

            if lat is None or lon is None:
                return None

            if gps_data.get('GPSLatitudeRef', 'N') == 'S':
                lat = -lat
            if gps_data.get('GPSLongitudeRef', 'E') == 'W':
                lon = -lon

            return {
                'lat': lat, 'lon': lon,
                'display': (
                    f"{abs(lat):.6f}°{'N' if lat >= 0 else 'S'}, "
                    f"{abs(lon):.6f}°{'E' if lon >= 0 else 'W'}"
                ),
                'osm': (
                    f"https://www.openstreetmap.org/"
                    f"?mlat={lat}&mlon={lon}&zoom=15"
                )
            }
        except Exception:
            return None

    @staticmethod
    def remove_all_metadata(image_path, output_path=None):
        try:
            if output_path is None:
                output_path = image_path

            img = PILImage.open(image_path)

            if 'icc_profile' in img.info:
                del img.info['icc_profile']

            clean_img = PILImage.new(img.mode, img.size)
            if hasattr(img, 'get_flattened_data'):
                clean_img.putdata(list(img.get_flattened_data()))
            else:
                clean_img.putdata(list(img.getdata()))

            ext = Path(output_path).suffix.lower()

            if ext in ['.jpg', '.jpeg']:
                clean_img.save(output_path, 'JPEG', quality=95, exif=b'', optimize=True)
            elif ext == '.png':
                from PIL.PngImagePlugin import PngInfo
                clean_img.save(output_path, 'PNG', pnginfo=PngInfo())
            elif ext == '.webp':
                clean_img.save(output_path, 'WEBP', quality=95, exif=b'')
            else:
                clean_img.save(output_path)

            if ext in ['.jpg', '.jpeg']:
                MetadataManagerMobile._clean_jpeg_segments(output_path)

            check = MetadataManagerMobile.get_all_metadata(output_path)

            return {
                'success': True,
                'sensibles_restants': len(check.get('sensibles', [])),
                'risk_score': check.get('risk_score', 0)
            }

        except Exception as e:
            return {'success': False, 'message': str(e)}

    @staticmethod
    def _clean_jpeg_segments(filepath):
        try:
            with open(filepath, 'rb') as f:
                data = f.read()

            markers = [
                b'\xff\xe1',  # APP1 - EXIF, XMP
                b'\xff\xe2',  # APP2 - ICC Profile
                b'\xff\xec',  # APP12 - Ducky
                b'\xff\xed',  # APP13 - Photoshop/IPTC
                b'\xff\xee',  # APP14 - Adobe
                b'\xff\xfe',  # COM - Commentaires
            ]

            for marker in markers:
                while marker in data:
                    idx = data.find(marker)
                    if idx == -1:
                        break
                    if idx + 4 > len(data):
                        break
                    length = struct.unpack('>H', data[idx + 2:idx + 4])[0]
                    data = data[:idx] + data[idx + 2 + length:]

            with open(filepath, 'wb') as f:
                f.write(data)
        except Exception:
            pass


# ── Nettoyage sécurisé ──────────────────────────────────────────────

def _secure_delete_file(filepath):
    """Supprime un fichier en l'écrasant d'abord avec des zéros"""
    try:
        if not os.path.isfile(filepath):
            return
        size = os.path.getsize(filepath)
        with open(filepath, 'wb') as f:
            f.write(b'\x00' * size)
            f.flush()
            os.fsync(f.fileno())
        os.remove(filepath)
    except Exception:
        try:
            os.remove(filepath)
        except Exception:
            pass


def _secure_delete_dir(dirpath):
    """Supprime récursivement un répertoire après écrasement des fichiers"""
    try:
        if not os.path.isdir(dirpath):
            return
        for root, dirs, files in os.walk(dirpath, topdown=False):
            for name in files:
                _secure_delete_file(os.path.join(root, name))
            for name in dirs:
                try:
                    os.rmdir(os.path.join(root, name))
                except Exception:
                    pass
        try:
            os.rmdir(dirpath)
        except Exception:
            pass
    except Exception:
        shutil.rmtree(dirpath, ignore_errors=True)


# ── Widget racine ───────────────────────────────────────────────────

class RootLayout(BoxLayout):
    pass


# ── Application principale ──────────────────────────────────────────

class BalMasqueMobile(App):
    """Application mobile Bal Masqué pour Android"""

    VERSION = "2.2"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.image_cv = None          # Image originale (numpy/cv2)
        self.image_processed = None   # Image après traitement
        self.image_path = None        # Chemin du fichier chargé
        self.detected_faces = []      # Boîtes des visages détectés
        self.manual_boxes = []        # Boîtes manuelles
        self._cascades = []           # Classificateurs Haar chargés
        self._temp_dirs = []          # Répertoires temporaires à nettoyer
        self._current_step = 0        # Étape courante du workflow

    def build(self):
        self.title = 'Bal Masqué'
        Builder.load_string(KV_LAYOUT)
        self.root_widget = RootLayout()

        slider = self.root_widget.ids.intensity_slider
        label = self.root_widget.ids.intensity_label
        slider.bind(value=lambda inst, val: setattr(label, 'text', str(int(val))))

        self._load_cascades()
        self._update_step(0)

        return self.root_widget

    def on_start(self):
        """Vérifie si l'app a été lancée par un intent Android (partage)"""
        if platform == 'android':
            from android import activity  # noqa: F811
            activity.bind(on_new_intent=self._on_new_intent)
            intent = activity.getIntent()
            self._handle_intent(intent)

    def on_pause(self):
        """Appelé quand l'app passe en arrière-plan — nettoie le cache"""
        self._purge_temp_files()
        return True

    def on_stop(self):
        """Appelé à la fermeture — nettoyage complet et sécurisé"""
        self._full_security_cleanup()

    # ── Nettoyage sécurisé (cache / mémoire) ────────────────────────

    def _full_security_cleanup(self):
        """Purge complète : fichiers temporaires, mémoire, caches Kivy"""
        # 1. Effacer les fichiers temporaires de manière sécurisée
        self._purge_temp_files()

        # 2. Écraser les données images en mémoire
        if self.image_cv is not None:
            self.image_cv[:] = 0
            self.image_cv = None
        if self.image_processed is not None:
            self.image_processed[:] = 0
            self.image_processed = None

        # 3. Effacer les références de détection
        self.detected_faces = []
        self.manual_boxes = []
        self.image_path = None

        # 4. Vider les caches Kivy (textures, images)
        try:
            Cache.remove('kv.image')
            Cache.remove('kv.texture')
        except Exception:
            pass

        # 5. Nettoyer le cache Android de l'application
        if platform == 'android':
            try:
                from jnius import autoclass
                PythonActivity = autoclass('org.kivy.android.PythonActivity')
                context = PythonActivity.mActivity
                cache_dir = context.getCacheDir().getAbsolutePath()
                _secure_delete_dir(cache_dir)
                os.makedirs(cache_dir, exist_ok=True)
            except Exception:
                pass

        # 6. Forcer le ramasse-miettes
        gc.collect()

    def _purge_temp_files(self):
        """Supprime de manière sécurisée tous les fichiers temporaires créés"""
        for tmp_dir in self._temp_dirs:
            _secure_delete_dir(tmp_dir)
        self._temp_dirs = []

        # Nettoyer aussi les dossiers balmasque_ orphelins dans le tmpdir
        try:
            tmp_root = tempfile.gettempdir()
            for entry in os.listdir(tmp_root):
                if entry.startswith('balmasque_'):
                    _secure_delete_dir(os.path.join(tmp_root, entry))
        except Exception:
            pass

    def manual_purge(self):
        """Bouton de purge manuelle : nettoie tout et réinitialise l'interface"""
        self._full_security_cleanup()

        # Réinitialiser l'affichage
        self.root_widget.ids.image_display.texture = None
        self.root_widget.ids.welcome_label.opacity = 1
        self._update_step(0)
        self._set_status('🔒 Purge complète — mémoire et cache nettoyés')

    # ── Indicateur d'étape du workflow ───────────────────────────────

    def _update_step(self, step):
        """Met à jour l'indicateur visuel de progression (étapes 0-4)"""
        self._current_step = step
        active_color = (1, 0.18, 0.33, 1)
        done_color = (0, 0.75, 0.53, 1)
        dim_color = (0.35, 0.35, 0.45, 1)

        ids = self.root_widget.ids
        labels = [ids.step1_lbl, ids.step2_lbl, ids.step3_lbl, ids.step4_lbl]

        for i, lbl in enumerate(labels):
            if i < step:
                lbl.color = done_color
            elif i == step:
                lbl.color = active_color
                lbl.bold = True
            else:
                lbl.color = dim_color
                lbl.bold = False

    # ── Intent Android (partage) ────────────────────────────────────

    def _on_new_intent(self, intent):
        """Reçoit un nouvel intent (partage depuis une autre app)"""
        self._handle_intent(intent)

    def _handle_intent(self, intent):
        """Traite un intent Android pour récupérer l'image partagée"""
        if platform != 'android':
            return

        try:
            from jnius import autoclass, cast
            Intent = autoclass('android.content.Intent')
            action = intent.getAction()

            if action == Intent.ACTION_SEND:
                mime = intent.getType()
                if mime and mime.startswith('image/'):
                    uri = intent.getParcelableExtra(Intent.EXTRA_STREAM)
                    if uri:
                        path = self._copy_uri_to_temp(uri)
                        if path:
                            Clock.schedule_once(
                                lambda dt: self._load_image_from_path(path), 0.3
                            )

            elif action == Intent.ACTION_SEND_MULTIPLE:
                mime = intent.getType()
                if mime and mime.startswith('image/'):
                    uris = intent.getParcelableArrayListExtra(Intent.EXTRA_STREAM)
                    if uris and uris.size() > 0:
                        uri = uris.get(0)
                        path = self._copy_uri_to_temp(uri)
                        if path:
                            Clock.schedule_once(
                                lambda dt: self._load_image_from_path(path), 0.3
                            )
        except Exception as e:
            self._set_status(f'Erreur intent : {e}')

    def _copy_uri_to_temp(self, uri):
        """Copie un fichier depuis un URI Android vers un fichier temporaire"""
        try:
            from jnius import autoclass
            PythonActivity = autoclass('org.kivy.android.PythonActivity')
            context = PythonActivity.mActivity
            resolver = context.getContentResolver()
            input_stream = resolver.openInputStream(uri)

            tmp_dir = tempfile.mkdtemp(prefix='balmasque_')
            self._temp_dirs.append(tmp_dir)
            tmp_path = os.path.join(tmp_dir, 'shared_image.jpg')

            FileOutputStream = autoclass('java.io.FileOutputStream')
            fos = FileOutputStream(tmp_path)

            buf = bytearray(8192)
            while True:
                n = input_stream.read(buf)
                if n == -1:
                    break
                fos.write(buf, 0, n)

            fos.close()
            input_stream.close()
            return tmp_path
        except Exception as e:
            self._set_status(f'Erreur copie : {e}')
            return None

    # ── Chargement des classificateurs ──────────────────────────────

    def _load_cascades(self):
        """Charge les classificateurs Haar pour la détection de visages"""
        cascade_names = [
            'haarcascade_frontalface_default.xml',
            'haarcascade_frontalface_alt2.xml',
            'haarcascade_profileface.xml',
        ]
        self._cascades = []

        if platform == 'android':
            cascade_dir = os.path.join(
                os.path.dirname(os.path.abspath(__file__)), 'cascades'
            )
        else:
            cascade_dir = cv2.data.haarcascades

        for name in cascade_names:
            path = os.path.join(cascade_dir, name)
            if not os.path.exists(path) and hasattr(cv2, 'data'):
                path = cv2.data.haarcascades + name
            cascade = cv2.CascadeClassifier(path)
            if not cascade.empty():
                self._cascades.append(cascade)

    # ── Ouverture d'image ───────────────────────────────────────────

    def open_image(self):
        """Ouvre un sélecteur de fichier ou la galerie Android"""
        if platform == 'android':
            self._open_android_gallery()
        else:
            self._open_desktop_filechooser()

    def _open_android_gallery(self):
        """Ouvre la galerie Android pour sélectionner une image"""
        try:
            from jnius import autoclass
            Intent = autoclass('android.content.Intent')
            PythonActivity = autoclass('org.kivy.android.PythonActivity')

            intent = Intent(Intent.ACTION_PICK)
            intent.setType('image/*')

            from android import activity
            activity.bind(on_activity_result=self._on_gallery_result)
            PythonActivity.mActivity.startActivityForResult(intent, 1)
        except Exception as e:
            self._set_status(f'Erreur galerie : {e}')

    def _on_gallery_result(self, request_code, result_code, intent):
        """Callback de la galerie Android"""
        if request_code == 1 and intent:
            uri = intent.getData()
            if uri:
                path = self._copy_uri_to_temp(uri)
                if path:
                    Clock.schedule_once(
                        lambda dt: self._load_image_from_path(path), 0.1
                    )

    def _open_desktop_filechooser(self):
        """Sélecteur de fichier pour tests sur desktop"""
        from kivy.uix.filechooser import FileChooserListView

        chooser = FileChooserListView(
            filters=['*.jpg', '*.jpeg', '*.png', '*.webp', '*.bmp'],
            path=os.path.expanduser('~')
        )
        popup = Popup(title='Ouvrir une image', content=chooser, size_hint=(0.9, 0.9))

        def on_selection(instance, selection):
            if selection:
                self._load_image_from_path(selection[0])
                popup.dismiss()

        chooser.bind(on_submit=on_selection)
        popup.open()

    def _load_image_from_path(self, path):
        """Charge une image depuis un chemin local"""
        try:
            img = cv2.imread(path)
            if img is None:
                self._set_status('⚠ Impossible de lire cette image')
                return

            self.image_path = path
            self.image_cv = img.copy()
            self.image_processed = img.copy()
            self.detected_faces = []
            self.manual_boxes = []

            # Masquer le message d'accueil
            self.root_widget.ids.welcome_label.opacity = 0
            self._display_image(img)

            meta = MetadataManagerMobile.get_all_metadata(path)
            risk = meta.get('risk_score', 0)
            nb_sens = len(meta.get('sensibles', []))

            if risk > 0:
                self._set_status(
                    f'📷 Image chargée — ⚠ Risque {risk}/100 '
                    f'({nb_sens} donnée(s) sensible(s))'
                )
            else:
                self._set_status('📷 Image chargée — Aucun risque détecté')

            self._update_step(1)

        except Exception as e:
            self._set_status(f'Erreur chargement : {e}')

    # ── Détection de visages ────────────────────────────────────────

    def detect_faces(self):
        """Détecte les visages dans l'image chargée"""
        if self.image_cv is None:
            self._set_status('⚠ Ouvrez d\'abord une image (étape ①)')
            return

        self._set_status('🔍 Détection en cours…')
        Clock.schedule_once(lambda dt: self._run_detection(), 0.1)

    def _run_detection(self):
        """Exécute la détection (déférée pour laisser l'UI se rafraîchir)"""
        gray = cv2.cvtColor(self.image_cv, cv2.COLOR_BGR2GRAY)
        all_faces = []

        for cascade in self._cascades:
            faces = cascade.detectMultiScale(
                gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30)
            )
            if len(faces) > 0:
                all_faces.extend(faces.tolist())

        # Détection profil inversé (miroir horizontal)
        flipped = cv2.flip(gray, 1)
        w = gray.shape[1]
        for cascade in self._cascades:
            faces = cascade.detectMultiScale(
                flipped, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30)
            )
            if len(faces) > 0:
                for (fx, fy, fw, fh) in faces:
                    all_faces.append([w - fx - fw, fy, fw, fh])

        # Élargir les boîtes de 25%
        h_img, w_img = self.image_cv.shape[:2]
        expanded = []
        for (x, y, bw, bh) in all_faces:
            mx = int(bw * 0.25)
            my = int(bh * 0.25)
            nx = max(0, x - mx)
            ny = max(0, y - my)
            nw = min(w_img - nx, bw + 2 * mx)
            nh = min(h_img - ny, bh + 2 * my)
            expanded.append((nx, ny, nw, nh))

        self.detected_faces = self._deduplicate_boxes(expanded)

        # Dessiner les boîtes sur l'aperçu
        preview = self.image_cv.copy()
        for (x, y, bw, bh) in self.detected_faces:
            cv2.rectangle(preview, (x, y), (x + bw, y + bh), (0, 45, 255), 3)

        self.image_processed = self.image_cv.copy()
        self._display_image(preview)

        n = len(self.detected_faces)
        if n > 0:
            self._set_status(f'👁 {n} visage(s) détecté(s) — Appuyez sur Flouter')
            self._update_step(2)
        else:
            self._set_status('Aucun visage détecté — Réessayez ou sauvegardez')
            self._update_step(2)

    @staticmethod
    def _deduplicate_boxes(boxes, overlap_thresh=0.4):
        """Supprime les boîtes qui se chevauchent trop"""
        if not boxes:
            return []

        boxes_arr = np.array(boxes, dtype=float)
        x1 = boxes_arr[:, 0]
        y1 = boxes_arr[:, 1]
        x2 = x1 + boxes_arr[:, 2]
        y2 = y1 + boxes_arr[:, 3]
        area = boxes_arr[:, 2] * boxes_arr[:, 3]

        idxs = np.argsort(area)
        picked = []

        while len(idxs) > 0:
            last = len(idxs) - 1
            i = idxs[last]
            picked.append(i)

            xx1 = np.maximum(x1[i], x1[idxs[:last]])
            yy1 = np.maximum(y1[i], y1[idxs[:last]])
            xx2 = np.minimum(x2[i], x2[idxs[:last]])
            yy2 = np.minimum(y2[i], y2[idxs[:last]])

            inter_w = np.maximum(0, xx2 - xx1)
            inter_h = np.maximum(0, yy2 - yy1)
            overlap = (inter_w * inter_h) / area[idxs[:last]]

            suppress = np.concatenate(
                ([last], np.where(overlap > overlap_thresh)[0])
            )
            idxs = np.delete(idxs, suppress)

        return [tuple(int(v) for v in boxes_arr[i]) for i in picked]

    # ── Application du floutage ─────────────────────────────────────

    def apply_blur(self):
        """Applique l'effet de floutage sur les zones détectées"""
        if self.image_cv is None:
            self._set_status('⚠ Ouvrez d\'abord une image (étape ①)')
            return

        all_boxes = self.detected_faces + self.manual_boxes
        if not all_boxes:
            self._set_status('⚠ Détectez d\'abord les visages (étape ②)')
            return

        effect = self.root_widget.ids.effect_spinner.text
        intensity = int(self.root_widget.ids.intensity_slider.value)

        result = self.image_cv.copy()
        for (x, y, w, h) in all_boxes:
            roi = result[y:y + h, x:x + w]
            if roi.size == 0:
                continue

            if effect == 'Pixelisation':
                pixel_size = max(3, intensity // 3)
                small_w = max(1, w // pixel_size)
                small_h = max(1, h // pixel_size)
                small = cv2.resize(roi, (small_w, small_h),
                                   interpolation=cv2.INTER_LINEAR)
                roi_blurred = cv2.resize(small, (w, h),
                                         interpolation=cv2.INTER_NEAREST)

            elif effect == 'Flou gaussien':
                ksize = max(3, intensity * 4 + 1)
                if ksize % 2 == 0:
                    ksize += 1
                roi_blurred = cv2.GaussianBlur(roi, (ksize, ksize), 0)
                roi_blurred = cv2.GaussianBlur(roi_blurred, (ksize, ksize), 0)

            elif effect == 'Masque noir':
                roi_blurred = np.zeros_like(roi)

            else:
                continue

            result[y:y + h, x:x + w] = roi_blurred

        self.image_processed = result
        self._display_image(result)
        self._set_status(
            f'🎭 Floutage appliqué ({len(all_boxes)} zone(s)) '
            f'— Sauvegardez ou nettoyez les métadonnées'
        )
        self._update_step(3)

    # ── Métadonnées ─────────────────────────────────────────────────

    def show_metadata(self):
        """Affiche un rapport sur les métadonnées de l'image"""
        if self.image_path is None:
            self._set_status('⚠ Ouvrez d\'abord une image')
            return

        meta = MetadataManagerMobile.get_all_metadata(self.image_path)
        risk = meta['risk_score']

        # En-tête avec indicateur visuel de risque
        if risk == 0:
            header = "✅  Score de risque : 0/100 — Aucun risque\n"
        elif risk < 30:
            header = f"⚠️  Score de risque : {risk}/100 — Risque faible\n"
        elif risk < 60:
            header = f"🟠  Score de risque : {risk}/100 — Risque moyen\n"
        else:
            header = f"🔴  Score de risque : {risk}/100 — Risque élevé !\n"

        lines = [header]

        if meta.get('gps'):
            lines.append("🌍  POSITION GPS DÉTECTÉE")
            lines.append(f"    {meta['gps']['display']}")
            lines.append(f"    Carte : {meta['gps']['osm']}\n")

        if meta.get('sensibles'):
            lines.append(f"⚠️  {len(meta['sensibles'])} DONNÉE(S) SENSIBLE(S) :")
            for s in meta['sensibles']:
                lines.append(f"    {s['label']}  {s['value']}")
            lines.append('')

        if meta.get('hidden_data'):
            lines.append(f"🔍  {len(meta['hidden_data'])} DONNÉE(S) CACHÉE(S) :")
            for d in meta['hidden_data']:
                lines.append(f"    {d}")
            lines.append('')

        if meta.get('file_info'):
            lines.append("📁  INFORMATIONS FICHIER :")
            for k, v in meta['file_info'].items():
                lines.append(f"    {k} : {v}")

        if risk > 0:
            lines.append('\n💡  Conseil : appuyez sur « 🧹 Nettoyer » pour supprimer')

        text = '\n'.join(lines)

        content = BoxLayout(orientation='vertical', padding=10, spacing=5)
        scroll = ScrollView(size_hint=(1, 1))
        lbl = Label(
            text=text, font_size='13sp', color=(1, 1, 1, 1),
            halign='left', valign='top', markup=False,
            size_hint_y=None
        )
        lbl.bind(texture_size=lbl.setter('size'))
        lbl.text_size = (Window.width * 0.85, None)
        scroll.add_widget(lbl)
        content.add_widget(scroll)

        popup = Popup(
            title='📊 Rapport de sécurité',
            content=content,
            size_hint=(0.95, 0.85)
        )
        popup.open()

    def clean_metadata(self):
        """Supprime toutes les métadonnées de l'image chargée"""
        if self.image_path is None:
            self._set_status('⚠ Ouvrez d\'abord une image')
            return

        result = MetadataManagerMobile.remove_all_metadata(self.image_path)
        if result.get('success'):
            residual = result.get('risk_score', 0)
            if residual == 0:
                self._set_status('✅ Métadonnées supprimées — Image propre')
            else:
                self._set_status(
                    f'🧹 Métadonnées nettoyées — Risque résiduel : {residual}/100'
                )
        else:
            self._set_status(
                f'❌ Erreur : {result.get("message", "inconnue")}'
            )

    # ── Sauvegarde ──────────────────────────────────────────────────

    def save_image(self):
        """Sauvegarde l'image traitée"""
        if self.image_processed is None:
            self._set_status('⚠ Aucune image à sauvegarder')
            return

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'bal_masque_{timestamp}.png'

        if platform == 'android':
            self._save_android(filename)
        else:
            self._save_desktop(filename)

        self._update_step(4)

    def _save_android(self, filename):
        """Sauvegarde sur Android (dans Pictures ou via partage)"""
        try:
            from jnius import autoclass
            Environment = autoclass('android.os.Environment')

            pictures_dir = Environment.getExternalStoragePublicDirectory(
                Environment.DIRECTORY_PICTURES
            ).getAbsolutePath()

            bal_dir = os.path.join(pictures_dir, 'BalMasque')
            os.makedirs(bal_dir, exist_ok=True)

            save_path = os.path.join(bal_dir, filename)
            cv2.imwrite(save_path, self.image_processed)

            MetadataManagerMobile.remove_all_metadata(save_path)

            # Notifier le media scanner Android
            try:
                PythonActivity = autoclass('org.kivy.android.PythonActivity')
                MediaScannerConnection = autoclass(
                    'android.media.MediaScannerConnection'
                )
                context = PythonActivity.mActivity
                MediaScannerConnection.scanFile(
                    context, [save_path], None, None
                )
            except Exception:
                pass

            self._set_status(f'✅ Sauvegardé dans Pictures/BalMasque/')
            self._offer_share(save_path)

        except Exception as e:
            self._set_status(f'Erreur sauvegarde : {e}')

    def _save_desktop(self, filename):
        """Sauvegarde sur desktop (pour tests)"""
        save_path = os.path.join(tempfile.gettempdir(), filename)
        cv2.imwrite(save_path, self.image_processed)
        MetadataManagerMobile.remove_all_metadata(save_path)
        self._set_status(f'✅ Sauvegardé : {save_path}')

    def _offer_share(self, file_path):
        """Propose de partager l'image traitée via Android share"""
        if platform != 'android':
            return

        try:
            from jnius import autoclass
            PythonActivity = autoclass('org.kivy.android.PythonActivity')
            Intent = autoclass('android.content.Intent')
            File = autoclass('java.io.File')
            FileProvider = autoclass('androidx.core.content.FileProvider')

            context = PythonActivity.mActivity
            f = File(file_path)

            uri = FileProvider.getUriForFile(
                context,
                context.getPackageName() + '.fileprovider',
                f
            )

            share_intent = Intent(Intent.ACTION_SEND)
            share_intent.setType('image/png')
            share_intent.putExtra(Intent.EXTRA_STREAM, uri)
            share_intent.addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION)

            chooser = Intent.createChooser(share_intent, 'Partager l\'image')
            context.startActivity(chooser)
        except Exception:
            pass

    # ── Annuler ─────────────────────────────────────────────────────

    def undo(self):
        """Revient à l'image originale"""
        if self.image_cv is None:
            self._set_status('⚠ Aucune image chargée')
            return
        self.image_processed = self.image_cv.copy()
        self.detected_faces = []
        self.manual_boxes = []
        self._display_image(self.image_cv)
        self._set_status('↩ Image restaurée — Vous pouvez recommencer')
        self._update_step(1)

    # ── Affichage ───────────────────────────────────────────────────

    def _display_image(self, cv_img):
        """Affiche une image OpenCV dans le widget Kivy Image"""
        try:
            img_rgb = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
            img_flip = cv2.flip(img_rgb, 0)
            h, w = img_flip.shape[:2]

            texture = Texture.create(size=(w, h), colorfmt='rgb')
            texture.blit_buffer(img_flip.tobytes(), colorfmt='rgb', bufferfmt='ubyte')

            self.root_widget.ids.image_display.texture = texture
        except Exception as e:
            self._set_status(f'Erreur affichage : {e}')

    def _set_status(self, text):
        """Met à jour le label de statut"""
        self.root_widget.ids.status_label.text = text


# ── Point d'entrée ──────────────────────────────────────────────────

if __name__ == '__main__':
    BalMasqueMobile().run()
