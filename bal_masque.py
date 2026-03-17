#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🎭 BAL MASQUÉ
Outil militant d'anonymisation des visages et métadonnées
Niveau professionnel de suppression des données sensibles
Licence GPL-3.0
"""

import cv2
import tkinter as tk
from tkinter import filedialog, messagebox, font as tkfont
from PIL import Image, ImageTk
from PIL.ExifTags import TAGS, GPSTAGS
from pathlib import Path
import numpy as np
import webbrowser
import sys
import os
from datetime import datetime
import struct
import re
import shutil
import platform


def enable_high_dpi():
    if sys.platform == 'win32':
        try:
            import ctypes
            ctypes.windll.shcore.SetProcessDpiAwareness(2)
        except Exception:
            try:
                import ctypes
                ctypes.windll.user32.SetProcessDPIAware()
            except Exception:
                pass


enable_high_dpi()


class Style:
    """Styles centralisés"""
    
    BG = '#0f0f1a'
    BG_PANEL = '#1a1a2e'
    ACCENT = '#ff2d55'
    ACCENT_HOVER = '#ff5c7c'
    SECONDARY = '#00e5a0'
    SECONDARY_HOVER = '#4dffc3'
    HIGHLIGHT = '#ffe600'
    PURPLE = '#a855f7'
    PURPLE_HOVER = '#c084fc'
    ORANGE = '#ff9500'
    CYAN = '#00d4ff'
    PINK = '#ff6bcb'
    TEXT = '#ffffff'
    TEXT_DIM = '#b8b8d0'
    TEXT_MUTED = '#7878a0'
    CANVAS_BG = '#08080f'
    LINK = '#5cb8ff'
    WHITE = '#ffffff'
    BLACK = '#000000'
    SUCCESS = '#00e5a0'
    WARNING = '#ff9500'
    CRITICAL = '#ff2d55'
    
    FONT = None
    FONT_MONO = None
    
    @classmethod
    def init(cls, root):
        available = list(tkfont.families())
        
        for f in ['Inter', 'Segoe UI', 'SF Pro Display', 'Helvetica Neue', 'Arial']:
            if f in available:
                cls.FONT = f
                break
        cls.FONT = cls.FONT or 'TkDefaultFont'
        
        for f in ['JetBrains Mono', 'Fira Code', 'Consolas', 'Monaco']:
            if f in available:
                cls.FONT_MONO = f
                break
        cls.FONT_MONO = cls.FONT_MONO or 'monospace'


class MetadataManager:
    """Gestionnaire professionnel de métadonnées"""
    
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
            
            img = Image.open(image_path)
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
                            
                            coords = MetadataManager._extract_gps_coords(gps_data)
                            if coords:
                                result['gps'] = coords
                                result['risk_score'] += 40
                        
                        try:
                            if isinstance(value, bytes):
                                value = value.decode('utf-8', errors='replace')[:100]
                            result['all_tags'][tag_name] = str(value)[:200]
                        except:
                            result['all_tags'][tag_name] = "[Binaire]"
                        
                        if tag_name in MetadataManager.SENSITIVE_TAGS:
                            result['sensibles'].append({
                                'tag': tag_name,
                                'label': MetadataManager.SENSITIVE_TAGS[tag_name],
                                'value': str(value)[:100]
                            })
                            result['risk_score'] += 10
            finally:
                img.close()
            
            with open(image_path, 'rb') as f:
                binary_data = f.read()
            
            emails = re.findall(rb'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', binary_data)
            for email in emails[:5]:
                result['hidden_data'].append(f"📧 Email: {email.decode('utf-8', errors='replace')}")
                result['risk_score'] += 15
            
            urls = re.findall(rb'https?://[^\s<>"{}|\\^`\[\]]+', binary_data)
            for url in urls[:5]:
                result['hidden_data'].append(f"🔗 URL: {url.decode('utf-8', errors='replace')[:60]}")
                result['risk_score'] += 5
            
            if b'\xff\xd8\xff' in binary_data[20:]:
                result['hidden_data'].append("🖼️ Miniature EXIF embarquée détectée")
                result['risk_score'] += 20
            
            # Détecter les métadonnées XMP embarquées
            if b'<x:xmpmeta' in binary_data or b'xmlns:xmp' in binary_data:
                result['hidden_data'].append("📦 Métadonnées XMP embarquées détectées")
                result['risk_score'] += 15
            
            # Détecter les profils ICC (peuvent contenir des identifiants)
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
                'display': f"{abs(lat):.6f}°{'N' if lat >= 0 else 'S'}, {abs(lon):.6f}°{'E' if lon >= 0 else 'W'}",
                'osm': f"https://www.openstreetmap.org/?mlat={lat}&mlon={lon}&zoom=15"
            }
        except:
            return None
    
    @staticmethod
    def remove_all_metadata(image_path, output_path=None):
        try:
            if output_path is None:
                output_path = image_path
            
            img = Image.open(image_path)
            
            # Supprimer le profil ICC et toute info auxiliaire
            if 'icc_profile' in img.info:
                del img.info['icc_profile']
            
            # Créer une image propre sans aucune métadonnée
            clean_img = Image.new(img.mode, img.size)
            if hasattr(img, 'get_flattened_data'):
                clean_img.putdata(list(img.get_flattened_data()))
            else:
                clean_img.putdata(list(img.getdata()))
            
            ext = Path(output_path).suffix.lower()
            
            if ext in ['.jpg', '.jpeg']:
                clean_img.save(output_path, 'JPEG', quality=95, exif=b'', optimize=True)
            elif ext == '.png':
                # PNG: sauvegarder sans aucune métadonnée
                from PIL.PngImagePlugin import PngInfo
                clean_img.save(output_path, 'PNG', pnginfo=PngInfo())
            elif ext == '.webp':
                clean_img.save(output_path, 'WEBP', quality=95, exif=b'')
            else:
                clean_img.save(output_path)
            
            if ext in ['.jpg', '.jpeg']:
                MetadataManager._clean_jpeg_segments(output_path)
            
            check = MetadataManager.get_all_metadata(output_path)
            
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
            
            # Supprimer tous les segments APP contenant des métadonnées :
            # APP1 (EXIF/XMP), APP2 (ICC), APP12 (Ducky), APP13 (Photoshop/IPTC),
            # APP14 (Adobe), COM (commentaires)
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
                    length = struct.unpack('>H', data[idx+2:idx+4])[0]
                    data = data[:idx] + data[idx+2+length:]
            
            with open(filepath, 'wb') as f:
                f.write(data)
        except Exception:
            pass


class BalMasque:
    """Application principale"""
    
    VERSION = "2.1"
    
    def __init__(self):
        # D'abord le disclaimer
        if not self.show_disclaimer():
            return
        
        # Puis l'application principale
        self.root = tk.Tk()
        self.root.title("🎭 Bal Masqué")
        self.root.configure(bg=Style.BG)
        
        # Plein écran (cross-platform)
        if sys.platform == 'win32':
            self.root.state('zoomed')
        elif sys.platform == 'darwin':
            self.root.attributes('-fullscreen', False)
            self.root.after(100, lambda: self.root.state('zoomed') if hasattr(self.root, 'state') else None)
            try:
                self.root.wm_attributes('-zoomed', True)
            except Exception:
                sw = self.root.winfo_screenwidth()
                sh = self.root.winfo_screenheight()
                self.root.geometry(f"{sw}x{sh}+0+0")
        else:
            try:
                self.root.attributes('-zoomed', True)
            except Exception:
                sw = self.root.winfo_screenwidth()
                sh = self.root.winfo_screenheight()
                self.root.geometry(f"{sw}x{sh}+0+0")
        
        self.root.minsize(1200, 800)
        
        Style.init(self.root)
        
        # Variables
        self.image_path = None
        self.image_original = None
        self.image_processed = None
        self.image_display = None
        self.faces_detected = []
        self.manual_boxes = []
        self.mode = tk.StringVar(value="auto")
        self.effect_var = tk.StringVar(value="pixelate")
        self.intensity_var = tk.IntVar(value=25)
        self.metadata_enabled = tk.BooleanVar(value=True)
        self.metadata_info = None
        
        self.start_x = 0
        self.start_y = 0
        self.current_rect = None
        self.scale_ratio = 1.0
        self.offset_x = 0
        self.offset_y = 0
        
        self.build_ui()
        self.bind_shortcuts()
        self.root.mainloop()
    
    def load_logo(self, size=90):
        logo_paths = [
            Path(__file__).parent / "logo.png",
            Path(__file__).parent / "assets" / "logo.png",
            Path("logo.png"),
        ]
        
        for path in logo_paths:
            if path.exists():
                try:
                    img = Image.open(path)
                    img.thumbnail((size, size), Image.Resampling.LANCZOS)
                    return ImageTk.PhotoImage(img)
                except:
                    pass
        return None
    
    def center_window(self, win, w, h):
        win.update_idletasks()
        x = (win.winfo_screenwidth() - w) // 2
        y = (win.winfo_screenheight() - h) // 2
        win.geometry(f"{w}x{h}+{x}+{y}")
    
    def show_disclaimer(self):
        """Fenêtre de bienvenue"""
        enable_high_dpi()
        
        win = tk.Tk()
        win.title("Bal Masqué")
        win.configure(bg=Style.BG)
        
        Style.init(win)
        self.center_window(win, 550, 620)
        
        accepted = [False]
        
        def accept():
            accepted[0] = True
            win.quit()
            win.destroy()
        
        def on_close():
            win.quit()
            win.destroy()
        
        win.protocol("WM_DELETE_WINDOW", on_close)
        
        canvas = tk.Canvas(win, bg=Style.BG, highlightthickness=0)
        scrollbar = tk.Scrollbar(win, orient='vertical', command=canvas.yview)
        canvas.configure(yscrollcommand=scrollbar.set)
        
        scrollbar.pack(side='right', fill='y')
        canvas.pack(side='left', fill='both', expand=True)
        
        main = tk.Frame(canvas, bg=Style.BG)
        canvas.create_window((0, 0), window=main, anchor='nw')
        
        content = tk.Frame(main, bg=Style.BG)
        content.pack(expand=True, fill='both', padx=45, pady=35)
        
        # Logo
        logo = self.load_logo(90)
        if logo:
            lbl = tk.Label(content, image=logo, bg=Style.BG)
            lbl.image = logo
            lbl.pack(pady=(0, 10))
        else:
            lbl = tk.Label(content, text="🎭 Bal Masqué", font=(Style.FONT, 22, 'bold'), bg=Style.BG, fg=Style.ACCENT)
            lbl.pack(pady=(0, 10))
        
        sub = tk.Label(content, text="Floutage de visages • Hors-ligne", font=(Style.FONT, 11), bg=Style.BG, fg=Style.CYAN)
        sub.pack(pady=(0, 25))
        
        # Métaphore
        metaphor_frame = tk.Frame(content, bg=Style.PURPLE, padx=3, pady=3)
        metaphor_frame.pack(fill='x', pady=(0, 25))
        
        metaphor_inner = tk.Frame(metaphor_frame, bg=Style.BG_PANEL, padx=20, pady=18)
        metaphor_inner.pack(fill='x')
        
        metaphor_text = """Au bal masqué, chacun·e choisit ce qu'iel révèle.

Dans la rue comme au carnaval, le masque protège.
Il permet d'exister sans être fiché, de défiler sans être ciblé.

Vos images restent sur votre machine."""
        
        tk.Label(
            metaphor_inner, text=metaphor_text,
            font=(Style.FONT, 11), bg=Style.BG_PANEL, fg=Style.TEXT,
            justify='left', wraplength=420
        ).pack()
        
        # Bouton principal
        btn = tk.Button(
            content, text="Accéder au bal →",
            command=accept, padx=25, pady=12,
            font=(Style.FONT, 12, 'bold'),
            bg=Style.SECONDARY, fg=Style.BLACK,
            activebackground=Style.SECONDARY_HOVER,
            activeforeground=Style.BLACK,
            relief='flat', cursor='hand2'
        )
        btn.pack(pady=(0, 25))
        
        # Ressources dépliantes
        resources_frame = tk.Frame(content, bg=Style.BG)
        resources_frame.pack(fill='x')
        
        expanded = [False]
        resources_content = [None]
        
        def toggle_resources():
            expanded[0] = not expanded[0]
            
            if expanded[0]:
                toggle_btn.config(text="▾ Ressources", fg=Style.PINK)
                rc = tk.Frame(resources_frame, bg=Style.BG)
                rc.pack(fill='x', pady=(10, 0))
                resources_content[0] = rc
                
                resources = [
                    ("La Quadrature du Net", "https://www.laquadrature.net", "Libertés numériques"),
                    ("Technopolice", "https://technopolice.fr", "Surveillance urbaine"),
                    ("Guide Boum", "https://guide.boum.org", "Autodéfense numérique"),
                ]
                
                for name, url, desc in resources:
                    row = tk.Frame(rc, bg=Style.BG)
                    row.pack(fill='x', pady=3)
                    
                    link = tk.Label(row, text=f"★ {name}", font=(Style.FONT, 10, 'underline'), bg=Style.BG, fg=Style.LINK, cursor='hand2')
                    link.pack(side='left')
                    link.bind('<Button-1>', lambda e, u=url: webbrowser.open(u))
                    
                    tk.Label(row, text=f" — {desc}", font=(Style.FONT, 10), bg=Style.BG, fg=Style.TEXT_DIM).pack(side='left')
                
                main.update_idletasks()
                canvas.configure(scrollregion=canvas.bbox('all'))
            else:
                toggle_btn.config(text="▸ Ressources", fg=Style.TEXT_DIM)
                if resources_content[0]:
                    resources_content[0].destroy()
                main.update_idletasks()
                canvas.configure(scrollregion=canvas.bbox('all'))
        
        toggle_btn = tk.Button(
            resources_frame, text="▸ Ressources",
            command=toggle_resources,
            font=(Style.FONT, 10),
            bg=Style.BG, fg=Style.TEXT_DIM,
            activebackground=Style.BG, activeforeground=Style.PINK,
            relief='flat', cursor='hand2', bd=0
        )
        toggle_btn.pack(anchor='w')
        
        tk.Label(
            content,
            text="GPL-3.0 • github.com/comenottaris/BAL-MASQUE",
            font=(Style.FONT, 9),
            bg=Style.BG, fg=Style.TEXT_MUTED
        ).pack(pady=(25, 0))
        
        main.update_idletasks()
        canvas.configure(scrollregion=canvas.bbox('all'))
        
        canvas.bind_all('<MouseWheel>', lambda e: canvas.yview_scroll(int(-1 * (e.delta / 120)), 'units'))
        canvas.bind_all('<Button-4>', lambda e: canvas.yview_scroll(-3, 'units'))
        canvas.bind_all('<Button-5>', lambda e: canvas.yview_scroll(3, 'units'))
        
        win.mainloop()
        return accepted[0]
    
    def build_ui(self):
        """Construction de l'interface"""
        main = tk.Frame(self.root, bg=Style.BG)
        main.pack(fill='both', expand=True)
        
        # === SIDEBAR GAUCHE (contrôles) ===
        sidebar = tk.Frame(main, bg=Style.BG, width=320)
        sidebar.pack(side='left', fill='y', padx=15, pady=15)
        sidebar.pack_propagate(False)
        
        # Scrollable
        s_canvas = tk.Canvas(sidebar, bg=Style.BG, highlightthickness=0)
        s_scroll = tk.Scrollbar(sidebar, orient='vertical', command=s_canvas.yview)
        s_frame = tk.Frame(s_canvas, bg=Style.BG)
        
        s_frame.bind("<Configure>", lambda e: s_canvas.configure(scrollregion=s_canvas.bbox("all")))
        s_canvas.create_window((0, 0), window=s_frame, anchor='nw', width=300)
        s_canvas.configure(yscrollcommand=s_scroll.set)
        
        s_canvas.pack(side='left', fill='both', expand=True)
        s_scroll.pack(side='right', fill='y')
        
        content = s_frame
        
        # Logo + titre
        logo = self.load_logo(70)
        if logo:
            lbl = tk.Label(content, image=logo, bg=Style.BG)
            lbl.image = logo
            lbl.pack(pady=(0, 5))
        else:
            tk.Label(content, text="🎭", font=('Segoe UI Emoji', 32), bg=Style.BG, fg=Style.ACCENT).pack()
        
        tk.Label(content, text="Bal Masqué", font=(Style.FONT, 16, 'bold'), bg=Style.BG, fg=Style.TEXT).pack()
        tk.Label(content, text="v2.1 • Hors-ligne", font=(Style.FONT, 9), bg=Style.BG, fg=Style.TEXT_MUTED).pack(pady=(0, 15))
        
        # === SECTION IMAGE ===
        self.create_section(content, "📷 IMAGE")
        
        img_btns = tk.Frame(content, bg=Style.BG)
        img_btns.pack(fill='x', pady=5)
        
        btn_open = tk.Button(img_btns, text="📂 Ouvrir", font=(Style.FONT, 10, 'bold'),
                            bg=Style.SECONDARY, fg=Style.BLACK, relief='flat', cursor='hand2',
                            padx=15, pady=6, command=self.load_image)
        btn_open.pack(side='left', expand=True, fill='x', padx=(0, 3))
        
        btn_save = tk.Button(img_btns, text="💾 Sauver", font=(Style.FONT, 10, 'bold'),
                            bg=Style.ORANGE, fg=Style.BLACK, relief='flat', cursor='hand2',
                            padx=15, pady=6, command=self.save_image)
        btn_save.pack(side='left', expand=True, fill='x', padx=(3, 0))
        
        # === SECTION MÉTADONNÉES (dépliante) ===
        self.create_collapsible_section(content, "🔒 MÉTADONNÉES", self.build_metadata_panel)
        
        # === SECTION DÉTECTION (dépliante) ===
        self.create_collapsible_section(content, "🎯 DÉTECTION", self.build_detection_panel)
        
        # === SECTION EFFET (dépliante) ===
        self.create_collapsible_section(content, "🎨 EFFET", self.build_effect_panel)
        
        # === SECTION ACTIONS ===
        self.create_section(content, "⚡ ACTIONS")
        
        act_row1 = tk.Frame(content, bg=Style.BG)
        act_row1.pack(fill='x', pady=3)
        
        btn_detect = tk.Button(act_row1, text="🔍 Détecter", font=(Style.FONT, 10),
                              bg=Style.PURPLE, fg=Style.WHITE, relief='flat', cursor='hand2',
                              padx=10, pady=6, command=self.detect_faces)
        btn_detect.pack(side='left', expand=True, fill='x', padx=(0, 3))
        
        btn_apply = tk.Button(act_row1, text="✨ Appliquer", font=(Style.FONT, 10),
                             bg=Style.CYAN, fg=Style.BLACK, relief='flat', cursor='hand2',
                             padx=10, pady=6, command=self.apply_blur)
        btn_apply.pack(side='left', expand=True, fill='x', padx=(3, 0))
        
        act_row2 = tk.Frame(content, bg=Style.BG)
        act_row2.pack(fill='x', pady=3)
        
        btn_undo = tk.Button(act_row2, text="↩ Annuler zone", font=(Style.FONT, 10),
                            bg=Style.BG_PANEL, fg=Style.TEXT, relief='flat', cursor='hand2',
                            padx=10, pady=6, command=self.undo_last_box)
        btn_undo.pack(side='left', expand=True, fill='x', padx=(0, 3))
        
        btn_reset = tk.Button(act_row2, text="🔄 Reset", font=(Style.FONT, 10),
                             bg=Style.ACCENT, fg=Style.WHITE, relief='flat', cursor='hand2',
                             padx=10, pady=6, command=self.reset_image)
        btn_reset.pack(side='left', expand=True, fill='x', padx=(3, 0))
        
        # Compteur
        self.counter_label = tk.Label(content, text="Zones : 0", font=(Style.FONT, 12, 'bold'),
                                     fg=Style.HIGHLIGHT, bg=Style.BG)
        self.counter_label.pack(pady=15)
        
        # Indicateur métadonnées
        self.meta_indicator = tk.Label(content, text="", font=(Style.FONT, 9),
                                      fg=Style.TEXT_DIM, bg=Style.BG, wraplength=280)
        self.meta_indicator.pack(pady=5)
        
        # === ZONE CENTRALE (image) ===
        center = tk.Frame(main, bg=Style.CANVAS_BG)
        center.pack(side='left', fill='both', expand=True, padx=(0, 15), pady=15)
        
        # Barre de statut
        self.status_bar = tk.Label(center, text="Prêt — Ctrl+O pour ouvrir", font=(Style.FONT, 10),
                                  bg=Style.BG_PANEL, fg=Style.TEXT_DIM, anchor='w', padx=15, pady=8)
        self.status_bar.pack(fill='x')
        
        # Canvas
        self.canvas = tk.Canvas(center, bg=Style.CANVAS_BG, highlightthickness=0)
        self.canvas.pack(fill='both', expand=True)
        
        self.canvas.bind('<ButtonPress-1>', self.on_canvas_press)
        self.canvas.bind('<B1-Motion>', self.on_canvas_drag)
        self.canvas.bind('<ButtonRelease-1>', self.on_canvas_release)
        
        self.show_welcome()
    
    def create_section(self, parent, title):
        """Titre de section simple"""
        frame = tk.Frame(parent, bg=Style.BG)
        frame.pack(fill='x', pady=(15, 5))
        
        tk.Frame(frame, bg=Style.CYAN, height=1).pack(fill='x', pady=(0, 5))
        tk.Label(frame, text=title, font=(Style.FONT, 9, 'bold'), fg=Style.CYAN, bg=Style.BG).pack(anchor='w')
    
    def create_collapsible_section(self, parent, title, build_func):
        """Section dépliante"""
        container = tk.Frame(parent, bg=Style.BG)
        container.pack(fill='x', pady=(10, 0))
        
        expanded = [False]
        content_frame = [None]
        
        def toggle():
            expanded[0] = not expanded[0]
            if expanded[0]:
                btn.config(text=f"▾ {title}", fg=Style.PINK)
                cf = tk.Frame(container, bg=Style.BG_PANEL, padx=10, pady=10)
                cf.pack(fill='x', pady=(5, 0))
                content_frame[0] = cf
                build_func(cf)
            else:
                btn.config(text=f"▸ {title}", fg=Style.CYAN)
                if content_frame[0]:
                    content_frame[0].destroy()
        
        btn = tk.Button(container, text=f"▸ {title}", font=(Style.FONT, 10, 'bold'),
                       bg=Style.BG, fg=Style.CYAN, relief='flat', cursor='hand2', bd=0,
                       anchor='w', command=toggle)
        btn.pack(fill='x')
    
    def build_metadata_panel(self, parent):
        """Contenu du panneau métadonnées"""
        cb = tk.Checkbutton(parent, text="Supprimer à la sauvegarde", variable=self.metadata_enabled,
                           font=(Style.FONT, 10), fg=Style.TEXT, bg=Style.BG_PANEL,
                           selectcolor=Style.PURPLE, activebackground=Style.BG_PANEL)
        cb.pack(anchor='w', pady=3)
        
        btns = tk.Frame(parent, bg=Style.BG_PANEL)
        btns.pack(fill='x', pady=5)
        
        tk.Button(btns, text="🔍 Analyser", font=(Style.FONT, 9),
                 bg=Style.CYAN, fg=Style.BLACK, relief='flat', cursor='hand2',
                 padx=8, pady=4, command=self.show_metadata_report).pack(side='left', padx=(0, 5))
        
        tk.Button(btns, text="🧹 Nettoyer", font=(Style.FONT, 9),
                 bg=Style.ACCENT, fg=Style.WHITE, relief='flat', cursor='hand2',
                 padx=8, pady=4, command=self.clean_metadata_now).pack(side='left')
    
    def build_detection_panel(self, parent):
        """Contenu du panneau détection"""
        for val, txt in [("auto", "🤖 Automatique"), ("manual", "✋ Manuel (dessiner)")]:
            rb = tk.Radiobutton(parent, text=txt, variable=self.mode, value=val,
                               font=(Style.FONT, 10), fg=Style.TEXT, bg=Style.BG_PANEL,
                               selectcolor=Style.PURPLE, activebackground=Style.BG_PANEL)
            rb.pack(anchor='w', pady=2)
    
    def build_effect_panel(self, parent):
        """Contenu du panneau effet"""
        for val, txt in [("pixelate", "▦ Pixelisation"), ("blur", "◐ Flou gaussien"), ("black", "■ Noir")]:
            rb = tk.Radiobutton(parent, text=txt, variable=self.effect_var, value=val,
                               font=(Style.FONT, 10), fg=Style.TEXT, bg=Style.BG_PANEL,
                               selectcolor=Style.PURPLE, activebackground=Style.BG_PANEL)
            rb.pack(anchor='w', pady=2)
        
        tk.Label(parent, text="Intensité:", font=(Style.FONT, 9), fg=Style.TEXT_DIM, bg=Style.BG_PANEL).pack(anchor='w', pady=(10, 0))
        
        slider = tk.Scale(parent, from_=5, to=50, orient='horizontal', variable=self.intensity_var,
                         bg=Style.BG_PANEL, fg=Style.TEXT, highlightthickness=0,
                         troughcolor=Style.BG, activebackground=Style.PINK,
                         command=lambda v: self.apply_blur() if self.image_processed is not None else None)
        slider.pack(fill='x')
    
    def show_welcome(self):
        self.canvas.delete("all")
        self.canvas.update()
        cx = self.canvas.winfo_width() // 2 or 400
        cy = self.canvas.winfo_height() // 2 or 300
        
        self.canvas.create_text(cx, cy - 30, text="🎭", font=('Segoe UI Emoji', 48), fill=Style.ACCENT)
        self.canvas.create_text(cx, cy + 40, text="Glissez une image ou cliquez sur Ouvrir",
                               font=(Style.FONT, 14), fill=Style.TEXT_DIM)
        self.canvas.create_text(cx, cy + 70, text="Ctrl+O pour ouvrir • Ctrl+S pour sauver",
                               font=(Style.FONT, 11), fill=Style.TEXT_MUTED)
    
    def bind_shortcuts(self):
        self.root.bind('<Control-o>', lambda e: self.load_image())
        self.root.bind('<Control-s>', lambda e: self.save_image())
        self.root.bind('<Control-z>', lambda e: self.undo_last_box())
        self.root.bind('<Control-d>', lambda e: self.detect_faces())
    
    def update_status(self, text):
        self.status_bar.config(text=text)
    
    def update_counter(self):
        total = len(self.faces_detected) + len(self.manual_boxes)
        self.counter_label.config(text=f"Zones : {total}")
    
    def load_image(self):
        path = filedialog.askopenfilename(
            title="Ouvrir une image",
            filetypes=[("Images", "*.jpg *.jpeg *.png *.bmp *.webp"), ("Tous", "*.*")]
        )
        
        if path:
            self.image_path = path
            self.image_original = cv2.imread(path)
            
            if self.image_original is None:
                messagebox.showerror("Erreur", "Impossible de charger l'image")
                return
            
            self.image_processed = self.image_original.copy()
            self.faces_detected = []
            self.manual_boxes = []
            self.update_counter()
            self.analyze_metadata()
            self.display_image()
            self.update_status(f"Image chargée : {Path(path).name}")
    
    def analyze_metadata(self):
        if not self.image_path:
            return
        
        self.metadata_info = MetadataManager.get_all_metadata(self.image_path)
        
        if self.metadata_info:
            risk = self.metadata_info.get('risk_score', 0)
            sensibles = len(self.metadata_info.get('sensibles', []))
            gps = self.metadata_info.get('gps')
            
            if risk >= 50:
                color, icon = Style.CRITICAL, "⚠️"
            elif risk >= 25:
                color, icon = Style.WARNING, "⚡"
            else:
                color, icon = Style.SUCCESS, "✓"
            
            text = f"{icon} Risque: {risk}/100"
            if sensibles > 0:
                text += f" • {sensibles} données sensibles"
            if gps:
                text += "\n🌍 GPS DÉTECTÉ !"
            
            self.meta_indicator.config(text=text, fg=color)
    
    def show_metadata_report(self):
        """Rapport de métadonnées - fenêtre agrandie"""
        if not self.image_path:
            messagebox.showwarning("Aucune image", "Chargez d'abord une image")
            return
        
        if not self.metadata_info:
            self.analyze_metadata()
        
        report = self.metadata_info
        
        win = tk.Toplevel(self.root)
        win.title("🔍 Rapport de sécurité - Métadonnées")
        win.configure(bg=Style.BG)
        
        # Fenêtre plus grande
        win_w, win_h = 850, 700
        x = (win.winfo_screenwidth() - win_w) // 2
        y = (win.winfo_screenheight() - win_h) // 2
        win.geometry(f"{win_w}x{win_h}+{x}+{y}")
        
        # Scrollable
        canvas = tk.Canvas(win, bg=Style.BG, highlightthickness=0)
        scrollbar = tk.Scrollbar(win, orient='vertical', command=canvas.yview)
        frame = tk.Frame(canvas, bg=Style.BG, padx=35, pady=25)
        
        frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=frame, anchor='nw', width=win_w - 40)
        canvas.configure(yscrollcommand=scrollbar.set)
        
        scrollbar.pack(side='right', fill='y')
        canvas.pack(side='left', fill='both', expand=True)
        
        # Titre
        tk.Label(frame, text="🔍 RAPPORT DE SÉCURITÉ", font=(Style.FONT, 20, 'bold'),
                fg=Style.ACCENT, bg=Style.BG).pack(anchor='w', pady=(0, 20))
        
        # Score
        risk = report.get('risk_score', 0)
        if risk >= 50:
            risk_color, risk_text = Style.CRITICAL, "CRITIQUE"
        elif risk >= 25:
            risk_color, risk_text = Style.WARNING, "ÉLEVÉ"
        else:
            risk_color, risk_text = Style.SUCCESS, "FAIBLE"
        
        risk_frame = tk.Frame(frame, bg=Style.BG_PANEL, padx=25, pady=20)
        risk_frame.pack(fill='x', pady=(0, 20))
        
        tk.Label(risk_frame, text=f"Score de risque : {risk}/100 — {risk_text}",
                font=(Style.FONT, 16, 'bold'), fg=risk_color, bg=Style.BG_PANEL).pack(anchor='w')
        
        # GPS
        if report.get('gps'):
            gps = report['gps']
            gps_frame = tk.Frame(frame, bg=Style.CRITICAL, padx=3, pady=3)
            gps_frame.pack(fill='x', pady=15)
            
            gps_inner = tk.Frame(gps_frame, bg=Style.BG_PANEL, padx=20, pady=15)
            gps_inner.pack(fill='x')
            
            tk.Label(gps_inner, text="🌍 POSITION GPS DÉTECTÉE", font=(Style.FONT, 14, 'bold'),
                    fg=Style.CRITICAL, bg=Style.BG_PANEL).pack(anchor='w')
            tk.Label(gps_inner, text=gps['display'], font=(Style.FONT_MONO, 12),
                    fg=Style.TEXT, bg=Style.BG_PANEL).pack(anchor='w', pady=8)
            
            tk.Button(gps_inner, text="🗺️ Voir sur la carte", font=(Style.FONT, 11),
                     fg=Style.BLACK, bg=Style.ORANGE, relief='flat', cursor='hand2',
                     padx=15, pady=6, command=lambda: webbrowser.open(gps['osm'])).pack(anchor='w')
        
        # Données sensibles
        sensibles = report.get('sensibles', [])
        if sensibles:
            tk.Label(frame, text=f"\n⚠️ DONNÉES SENSIBLES ({len(sensibles)})",
                    font=(Style.FONT, 14, 'bold'), fg=Style.WARNING, bg=Style.BG).pack(anchor='w')
            
            for item in sensibles:
                tk.Label(frame, text=f"  {item['label']}: {item['value'][:60]}",
                        font=(Style.FONT, 11), fg=Style.TEXT_DIM, bg=Style.BG).pack(anchor='w', pady=2)
        
        # Données cachées
        hidden = report.get('hidden_data', [])
        if hidden:
            tk.Label(frame, text=f"\n🔎 DONNÉES CACHÉES ({len(hidden)})",
                    font=(Style.FONT, 14, 'bold'), fg=Style.PINK, bg=Style.BG).pack(anchor='w')
            
            for item in hidden:
                tk.Label(frame, text=f"  {item}", font=(Style.FONT, 11),
                        fg=Style.TEXT_DIM, bg=Style.BG).pack(anchor='w', pady=2)
        
        # Toutes métadonnées
        all_tags = report.get('all_tags', {})
        if all_tags:
            tk.Label(frame, text=f"\n📋 TOUTES LES MÉTADONNÉES ({len(all_tags)})",
                    font=(Style.FONT, 14, 'bold'), fg=Style.CYAN, bg=Style.BG).pack(anchor='w')
            
            tags_frame = tk.Frame(frame, bg=Style.BG_PANEL, padx=15, pady=15)
            tags_frame.pack(fill='x', pady=10)
            
            for i, (tag, value) in enumerate(list(all_tags.items())[:25]):
                tk.Label(tags_frame, text=f"{tag}: {value[:70]}", font=(Style.FONT, 10),
                        fg=Style.TEXT_DIM, bg=Style.BG_PANEL, anchor='w').pack(anchor='w', pady=1)
            
            if len(all_tags) > 25:
                tk.Label(tags_frame, text=f"... et {len(all_tags) - 25} autres",
                        font=(Style.FONT, 10), fg=Style.TEXT_MUTED, bg=Style.BG_PANEL).pack(anchor='w')
        
        # Boutons
        btn_frame = tk.Frame(frame, bg=Style.BG)
        btn_frame.pack(pady=25)
        
        tk.Button(btn_frame, text="🧹 Tout nettoyer", font=(Style.FONT, 12, 'bold'),
                 fg=Style.BLACK, bg=Style.SECONDARY, relief='flat', cursor='hand2',
                 padx=25, pady=10, command=lambda: [self.clean_metadata_now(), win.destroy()]).pack(side='left', padx=10)
        
        tk.Button(btn_frame, text="Fermer", font=(Style.FONT, 12),
                 fg=Style.TEXT, bg=Style.BG_PANEL, relief='flat', cursor='hand2',
                 padx=25, pady=10, command=win.destroy).pack(side='left', padx=10)
        
        canvas.bind_all('<MouseWheel>', lambda e: canvas.yview_scroll(int(-1 * (e.delta / 120)), 'units'))
        canvas.bind_all('<Button-4>', lambda e: canvas.yview_scroll(-3, 'units'))
        canvas.bind_all('<Button-5>', lambda e: canvas.yview_scroll(3, 'units'))
    
    def clean_metadata_now(self):
        if not self.image_path:
            messagebox.showwarning("Aucune image", "Chargez d'abord une image")
            return
        
        if messagebox.askyesno("Confirmation", "Supprimer TOUTES les métadonnées ?\n\nUne sauvegarde sera créée."):
            try:
                backup = self.image_path + ".backup"
                shutil.copy2(self.image_path, backup)
                
                result = MetadataManager.remove_all_metadata(self.image_path)
                
                if result['success']:
                    self.analyze_metadata()
                    messagebox.showinfo("Succès", f"✅ Métadonnées supprimées !\n\nSauvegarde : {Path(backup).name}")
                else:
                    messagebox.showerror("Erreur", result['message'])
            except Exception as e:
                messagebox.showerror("Erreur", str(e))
    
    def display_image(self):
        if self.image_processed is None:
            return
        
        image_rgb = cv2.cvtColor(self.image_processed, cv2.COLOR_BGR2RGB)
        
        self.canvas.update()
        canvas_w = max(self.canvas.winfo_width(), 400)
        canvas_h = max(self.canvas.winfo_height(), 300)
        
        img_h, img_w = image_rgb.shape[:2]
        ratio_w = canvas_w / img_w
        ratio_h = canvas_h / img_h
        self.scale_ratio = min(ratio_w, ratio_h, 1.0)
        
        new_w = int(img_w * self.scale_ratio)
        new_h = int(img_h * self.scale_ratio)
        
        image_resized = cv2.resize(image_rgb, (new_w, new_h), interpolation=cv2.INTER_AREA)
        image_pil = Image.fromarray(image_resized)
        self.image_display = ImageTk.PhotoImage(image_pil)
        
        self.canvas.delete("all")
        self.offset_x = (canvas_w - new_w) // 2
        self.offset_y = (canvas_h - new_h) // 2
        
        self.canvas.create_image(self.offset_x, self.offset_y, anchor=tk.NW, image=self.image_display)
        self.draw_boxes()
    
    def draw_boxes(self):
        self.canvas.delete("boxes")
        
        for (x, y, w, h) in self.faces_detected:
            x1 = int(x * self.scale_ratio) + self.offset_x
            y1 = int(y * self.scale_ratio) + self.offset_y
            x2 = int((x + w) * self.scale_ratio) + self.offset_x
            y2 = int((y + h) * self.scale_ratio) + self.offset_y
            self.canvas.create_rectangle(x1, y1, x2, y2, outline=Style.SECONDARY, width=2, tags="boxes")
        
        for (x, y, w, h) in self.manual_boxes:
            x1 = int(x * self.scale_ratio) + self.offset_x
            y1 = int(y * self.scale_ratio) + self.offset_y
            x2 = int((x + w) * self.scale_ratio) + self.offset_x
            y2 = int((y + h) * self.scale_ratio) + self.offset_y
            self.canvas.create_rectangle(x1, y1, x2, y2, outline=Style.ORANGE, width=2, tags="boxes")
    
    def on_canvas_press(self, event):
        if self.mode.get() != "manual" or self.image_original is None:
            return
        self.start_x = event.x
        self.start_y = event.y
        self.current_rect = None
    
    def on_canvas_drag(self, event):
        if self.mode.get() != "manual" or self.image_original is None:
            return
        if self.current_rect:
            self.canvas.delete(self.current_rect)
        self.current_rect = self.canvas.create_rectangle(
            self.start_x, self.start_y, event.x, event.y,
            outline=Style.ACCENT, width=2, dash=(4, 4)
        )
    
    def on_canvas_release(self, event):
        if self.mode.get() != "manual" or self.image_original is None:
            return
        if self.current_rect:
            self.canvas.delete(self.current_rect)
        
        x1 = int((min(self.start_x, event.x) - self.offset_x) / self.scale_ratio)
        y1 = int((min(self.start_y, event.y) - self.offset_y) / self.scale_ratio)
        x2 = int((max(self.start_x, event.x) - self.offset_x) / self.scale_ratio)
        y2 = int((max(self.start_y, event.y) - self.offset_y) / self.scale_ratio)
        
        if x2 - x1 > 10 and y2 - y1 > 10:
            h, w = self.image_original.shape[:2]
            x1, y1 = max(0, x1), max(0, y1)
            x2, y2 = min(w, x2), min(h, y2)
            
            self.manual_boxes.append((x1, y1, x2 - x1, y2 - y1))
            self.update_counter()
            self.apply_blur()
    
    def detect_faces(self):
        if self.image_original is None:
            messagebox.showwarning("Aucune image", "Chargez d'abord une image")
            return
        
        self.update_status("Détection en cours...")
        self.root.update()
        
        gray = cv2.cvtColor(self.image_original, cv2.COLOR_BGR2GRAY)
        gray = cv2.equalizeHist(gray)
        
        all_faces = []
        
        # Détection frontale avec plusieurs passes (sensibilité croissante)
        cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        face_cascade = cv2.CascadeClassifier(cascade_path)
        
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.05, minNeighbors=4, minSize=(20, 20))
        for f in faces:
            all_faces.append(tuple(f))
        
        # Détection frontale alt (autre modèle)
        alt_cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_alt2.xml'
        alt_cascade = cv2.CascadeClassifier(alt_cascade_path)
        alt_faces = alt_cascade.detectMultiScale(gray, scaleFactor=1.05, minNeighbors=4, minSize=(20, 20))
        for f in alt_faces:
            if not any(self._boxes_overlap(tuple(f), existing) for existing in all_faces):
                all_faces.append(tuple(f))
        
        # Détection profils gauche
        profile_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_profileface.xml')
        profiles = profile_cascade.detectMultiScale(gray, scaleFactor=1.05, minNeighbors=4, minSize=(20, 20))
        for p in profiles:
            if not any(self._boxes_overlap(tuple(p), existing) for existing in all_faces):
                all_faces.append(tuple(p))
        
        # Détection profils droite (image retournée)
        flipped = cv2.flip(gray, 1)
        profiles_r = profile_cascade.detectMultiScale(flipped, scaleFactor=1.05, minNeighbors=4, minSize=(20, 20))
        img_w = gray.shape[1]
        for (x, y, w, h) in profiles_r:
            mirrored = (img_w - x - w, y, w, h)
            if not any(self._boxes_overlap(mirrored, existing) for existing in all_faces):
                all_faces.append(mirrored)
        
        # Élargir les zones détectées de 25% pour couvrir tout le visage
        expanded = []
        img_h, img_w_full = self.image_original.shape[:2]
        for (x, y, w, h) in all_faces:
            margin_x = int(w * 0.25)
            margin_y = int(h * 0.25)
            nx = max(0, x - margin_x)
            ny = max(0, y - margin_y)
            nw = min(img_w_full - nx, w + 2 * margin_x)
            nh = min(img_h - ny, h + 2 * margin_y)
            expanded.append((nx, ny, nw, nh))
        
        # Dédupliquer les zones élargies
        self.faces_detected = []
        for box in expanded:
            if not any(self._boxes_overlap(box, existing, threshold=0.4) for existing in self.faces_detected):
                self.faces_detected.append(box)
        
        self.update_counter()
        
        if self.faces_detected:
            self.update_status(f"{len(self.faces_detected)} visage(s) détecté(s)")
            self.apply_blur()
        else:
            self.update_status("Aucun visage — Mode manuel recommandé")
            messagebox.showinfo("Détection", "Aucun visage détecté.\n\nUtilisez le mode manuel (▸ DÉTECTION)")
    
    def _boxes_overlap(self, box1, box2, threshold=0.5):
        x1, y1, w1, h1 = box1
        x2, y2, w2, h2 = box2
        
        xi1, yi1 = max(x1, x2), max(y1, y2)
        xi2, yi2 = min(x1 + w1, x2 + w2), min(y1 + h1, y2 + h2)
        
        if xi2 <= xi1 or yi2 <= yi1:
            return False
        
        inter = (xi2 - xi1) * (yi2 - yi1)
        return inter / min(w1 * h1, w2 * h2) > threshold
    
    def apply_blur(self):
        if self.image_original is None:
            return
        
        self.image_processed = self.image_original.copy()
        all_boxes = self.faces_detected + self.manual_boxes
        intensity = self.intensity_var.get()
        effect = self.effect_var.get()
        
        for (x, y, w, h) in all_boxes:
            roi = self.image_processed[y:y+h, x:x+w]
            if roi.size == 0:
                continue
            
            if effect == "pixelate":
                # Pixelisation plus agressive : blocs plus gros
                pixel_size = max(3, intensity // 3)
                small_w = max(1, w // pixel_size)
                small_h = max(1, h // pixel_size)
                small = cv2.resize(roi, (small_w, small_h), interpolation=cv2.INTER_LINEAR)
                blurred = cv2.resize(small, (w, h), interpolation=cv2.INTER_NEAREST)
            elif effect == "blur":
                # Double passe de flou gaussien pour effet plus fort
                ksize = max(3, intensity * 4 + 1)
                if ksize % 2 == 0:
                    ksize += 1
                blurred = cv2.GaussianBlur(roi, (ksize, ksize), 0)
                blurred = cv2.GaussianBlur(blurred, (ksize, ksize), 0)
            elif effect == "black":
                blurred = np.zeros_like(roi)
            else:
                blurred = roi
            
            self.image_processed[y:y+h, x:x+w] = blurred
        
        self.display_image()
    
    def undo_last_box(self):
        if self.manual_boxes:
            self.manual_boxes.pop()
        elif self.faces_detected:
            self.faces_detected.pop()
        else:
            return
        
        self.update_counter()
        self.apply_blur()
        self.update_status("Zone annulée")
    
    def reset_image(self):
        if self.image_original is not None:
            self.image_processed = self.image_original.copy()
            self.faces_detected = []
            self.manual_boxes = []
            self.update_counter()
            self.display_image()
            self.update_status("Image réinitialisée")
    
    def save_image(self):
        if self.image_processed is None:
            messagebox.showwarning("Aucune image", "Aucune image à sauvegarder")
            return
        
        default_name = f"bal_masque_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        
        path = filedialog.asksaveasfilename(
            defaultextension=".png",
            initialfile=default_name,
            filetypes=[("PNG (recommandé)", "*.png"), ("JPEG", "*.jpg"), ("WebP", "*.webp")]
        )
        
        if path:
            try:
                cv2.imwrite(path, self.image_processed)
                
                if self.metadata_enabled.get():
                    result = MetadataManager.remove_all_metadata(path)
                    if result['success']:
                        messagebox.showinfo("Succès", f"✅ Image sauvegardée :\n{path}\n\n✅ Métadonnées supprimées")
                    else:
                        messagebox.showwarning("Attention", f"Sauvegardée mais erreur métadonnées")
                else:
                    messagebox.showinfo("Succès", f"Image sauvegardée :\n{path}")
                
                self.update_status(f"Sauvegardé : {Path(path).name}")
            except Exception as e:
                messagebox.showerror("Erreur", str(e))


if __name__ == "__main__":
    BalMasque()
