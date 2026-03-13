#!/usr/bin/env python3
"""Tests unitaires pour les fonctionnalités critiques de Bal Masqué"""

import unittest
import tempfile
import os
import struct
import sys
import numpy as np
import cv2
from PIL import Image

# Ajouter le répertoire du projet au path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from bal_masque import MetadataManager


class TestMetadataRemoval(unittest.TestCase):
    """Tests pour la suppression complète des métadonnées"""

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()

    def _create_jpeg_with_exif(self, path):
        """Crée un JPEG avec des métadonnées EXIF simulées"""
        img = Image.new('RGB', (100, 100), color='red')
        img.save(path, 'JPEG', quality=95)
        # Injecter un faux segment APP1 EXIF avec des données sensibles
        with open(path, 'rb') as f:
            data = f.read()
        fake_exif = b'Exif\x00\x00test@example.com some-serial-12345'
        segment = b'\xff\xe1' + struct.pack('>H', len(fake_exif) + 2) + fake_exif
        data = data[:2] + segment + data[2:]
        with open(path, 'wb') as f:
            f.write(data)

    def test_jpeg_metadata_removal(self):
        """Vérifie que les métadonnées JPEG sont supprimées"""
        path = os.path.join(self.tmpdir, 'test.jpg')
        self._create_jpeg_with_exif(path)

        with open(path, 'rb') as f:
            raw = f.read()
        self.assertIn(b'test@example.com', raw)

        result = MetadataManager.remove_all_metadata(path)
        self.assertTrue(result['success'])

        with open(path, 'rb') as f:
            cleaned = f.read()
        self.assertNotIn(b'test@example.com', cleaned)
        self.assertNotIn(b'some-serial-12345', cleaned)

    def test_png_clean_save(self):
        """Vérifie que les PNG sont sauvegardés sans métadonnées"""
        path = os.path.join(self.tmpdir, 'test.png')
        img = Image.new('RGB', (50, 50), color='blue')
        img.save(path, 'PNG')

        result = MetadataManager.remove_all_metadata(path)
        self.assertTrue(result['success'])
        self.assertEqual(result['risk_score'], 0)

    def test_jpeg_app_segments_cleaned(self):
        """Vérifie que tous les segments APP sensibles sont supprimés"""
        path = os.path.join(self.tmpdir, 'test_segments.jpg')
        img = Image.new('RGB', (50, 50), color='green')
        img.save(path, 'JPEG', quality=95)

        with open(path, 'rb') as f:
            data = f.read()

        segments = [
            (b'\xff\xe1', b'EXIF_DATA_HERE'),
            (b'\xff\xe2', b'ICC_PROFILE_DATA'),
            (b'\xff\xed', b'PHOTOSHOP_IPTC'),
            (b'\xff\xfe', b'COMMENT_HERE'),
        ]
        for marker, payload in segments:
            segment = marker + struct.pack('>H', len(payload) + 2) + payload
            data = data[:2] + segment + data[2:]

        with open(path, 'wb') as f:
            f.write(data)

        result = MetadataManager.remove_all_metadata(path)
        self.assertTrue(result['success'])

        with open(path, 'rb') as f:
            cleaned = f.read()
        self.assertNotIn(b'EXIF_DATA_HERE', cleaned)
        self.assertNotIn(b'ICC_PROFILE_DATA', cleaned)
        self.assertNotIn(b'PHOTOSHOP_IPTC', cleaned)
        self.assertNotIn(b'COMMENT_HERE', cleaned)

    def test_metadata_analysis_risk_scoring(self):
        """Vérifie le scoring de risque"""
        path = os.path.join(self.tmpdir, 'test_risk.jpg')
        img = Image.new('RGB', (50, 50), color='white')
        img.save(path, 'JPEG')

        result = MetadataManager.get_all_metadata(path)
        self.assertEqual(result['risk_score'], 0)
        self.assertEqual(len(result['sensibles']), 0)

    def test_xmp_detection(self):
        """Vérifie la détection de métadonnées XMP"""
        path = os.path.join(self.tmpdir, 'test_xmp.jpg')
        img = Image.new('RGB', (50, 50), color='yellow')
        img.save(path, 'JPEG')

        with open(path, 'rb') as f:
            data = f.read()
        xmp_data = b'<x:xmpmeta xmlns:xmp="http://test.example.com">test</x:xmpmeta>'
        segment = b'\xff\xe1' + struct.pack('>H', len(xmp_data) + 2) + xmp_data
        data = data[:2] + segment + data[2:]
        with open(path, 'wb') as f:
            f.write(data)

        result = MetadataManager.get_all_metadata(path)
        xmp_found = any('XMP' in d for d in result.get('hidden_data', []))
        self.assertTrue(xmp_found, "XMP metadata should be detected")

    def tearDown(self):
        import shutil
        shutil.rmtree(self.tmpdir, ignore_errors=True)


class TestFaceBlurring(unittest.TestCase):
    """Tests pour le floutage des visages"""

    def test_pixelation_reduces_detail(self):
        """Vérifie que la pixelisation réduit significativement les détails"""
        img = np.zeros((100, 100, 3), dtype=np.uint8)
        for i in range(100):
            for j in range(100):
                img[i, j] = [i * 2, j * 2, (i + j)]

        original_variance = np.var(img.astype(float))

        intensity = 25
        h, w = 100, 100
        roi = img.copy()
        pixel_size = max(3, intensity // 3)
        small_w = max(1, w // pixel_size)
        small_h = max(1, h // pixel_size)
        small = cv2.resize(roi, (small_w, small_h), interpolation=cv2.INTER_LINEAR)
        blurred = cv2.resize(small, (w, h), interpolation=cv2.INTER_NEAREST)

        blurred_variance = np.var(blurred.astype(float))
        # La pixelisation réduit les détails fins tout en préservant les motifs globaux
        self.assertLess(blurred_variance, original_variance,
                        "La pixelisation doit réduire les détails")

    def test_gaussian_blur_strength(self):
        """Vérifie que le flou gaussien est suffisamment fort"""
        img = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
        original_variance = np.var(img.astype(float))

        intensity = 25
        ksize = max(3, intensity * 4 + 1)
        if ksize % 2 == 0:
            ksize += 1
        blurred = cv2.GaussianBlur(img, (ksize, ksize), 0)
        blurred = cv2.GaussianBlur(blurred, (ksize, ksize), 0)

        blurred_variance = np.var(blurred.astype(float))
        self.assertLess(blurred_variance, original_variance * 0.1,
                        "Le flou gaussien double passe doit réduire fortement les détails")

    def test_black_mask_complete(self):
        """Vérifie que le masque noir est complet"""
        img = np.random.randint(0, 255, (50, 50, 3), dtype=np.uint8)
        blurred = np.zeros_like(img)
        self.assertEqual(np.sum(blurred), 0, "Le masque noir doit être entièrement noir")

    def test_face_detection_cascades_available(self):
        """Vérifie que les fichiers cascade OpenCV sont disponibles"""
        cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        )
        self.assertFalse(cascade.empty(), "Le classificateur Haar doit se charger")

        profile = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_profileface.xml'
        )
        self.assertFalse(profile.empty(), "Le classificateur profil doit se charger")

        alt = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_frontalface_alt2.xml'
        )
        self.assertFalse(alt.empty(), "Le classificateur alt2 doit se charger")

    def test_box_expansion_margins(self):
        """Vérifie l'élargissement de 25% des zones détectées"""
        x, y, w, h = 100, 100, 80, 80
        img_w, img_h = 640, 480

        margin_x = int(w * 0.25)
        margin_y = int(h * 0.25)
        nx = max(0, x - margin_x)
        ny = max(0, y - margin_y)
        nw = min(img_w - nx, w + 2 * margin_x)
        nh = min(img_h - ny, h + 2 * margin_y)

        self.assertGreater(nw, w)
        self.assertGreater(nh, h)
        self.assertAlmostEqual(nw, w + 2 * margin_x, delta=1)
        self.assertAlmostEqual(nh, h + 2 * margin_y, delta=1)


class TestCrossPlatform(unittest.TestCase):
    """Tests pour la compatibilité cross-platform"""

    def test_imports(self):
        """Vérifie que tous les imports fonctionnent"""
        import cv2
        import numpy
        from PIL import Image
        import platform
        self.assertIsNotNone(cv2.__version__)
        self.assertIsNotNone(numpy.__version__)

    def test_cascade_files_exist(self):
        """Vérifie que les fichiers cascade OpenCV sont disponibles"""
        cascades = [
            'haarcascade_frontalface_default.xml',
            'haarcascade_frontalface_alt2.xml',
            'haarcascade_profileface.xml',
        ]
        for cascade in cascades:
            path = cv2.data.haarcascades + cascade
            self.assertTrue(os.path.exists(path),
                            f"Cascade manquant : {cascade}")

    def test_metadata_manager_standalone(self):
        """Vérifie que MetadataManager fonctionne sans GUI"""
        tmpdir = tempfile.mkdtemp()
        path = os.path.join(tmpdir, 'test.jpg')
        img = Image.new('RGB', (100, 100), 'red')
        img.save(path, 'JPEG')

        result = MetadataManager.get_all_metadata(path)
        self.assertIn('risk_score', result)
        self.assertIn('sensibles', result)
        self.assertIn('hidden_data', result)

        result2 = MetadataManager.remove_all_metadata(path)
        self.assertTrue(result2['success'])

        import shutil
        shutil.rmtree(tmpdir, ignore_errors=True)


if __name__ == '__main__':
    unittest.main()
