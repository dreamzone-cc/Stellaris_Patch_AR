#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Stellaris Patch AR v1.0
أداة تطبيق التصحيح العربي لـ Stellaris
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from pathlib import Path
import shutil
import json
import time
import threading
from datetime import datetime
from typing import Optional, List, Tuple
import pygame
import os
import sys
import tempfile


class ModernStellarPatch:
    """أداة تطبيق التصحيح العربي لـ Stellaris"""
    
    def __init__(self):
        """تهيئة التطبيق"""
        self.root = tk.Tk()
        self.stellaris_path: Optional[Path] = None
        
        # تحديد المسارات بناءً على نوع التشغيل (مطور أم مجمع)
        self._setup_paths()
        
        # متغيرات واجهة المستخدم
        self.progress_var = tk.DoubleVar()
        self.status_var = tk.StringVar(value="Ready to start")
        self.current_file_var = tk.StringVar()
        
        # متغيرات الموسيقى
        self.music_playing = False
        self.music_muted = False
        self.music_file = self._find_music_file()
        
        # تهيئة pygame للموسيقى
        try:
            pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
        except:
            pass  # إذا فشل تشغيل pygame
        
        # ألوان عصرية
        self.colors = {
            'primary': '#6366f1',        # Indigo
            'primary_light': '#a5b4fc',  # Light Indigo
            'secondary': '#10b981',      # Emerald
            'accent': '#f59e0b',         # Amber
            'error': '#ef4444',          # Red
            'surface': '#ffffff',        # White
            'background': '#f8fafc',     # Slate 50
            'card': '#ffffff',           # White
            'text_primary': '#0f172a',   # Slate 900
            'text_secondary': '#64748b', # Slate 500
            'border': '#e2e8f0',         # Slate 200
            'shadow': '#94a3b8'          # Slate 400
        }
        
        self._setup_window()
        self._create_modern_interface()
        self._update_status()
        
        # تشغيل الموسيقى تلقائياً
        self._start_background_music()
    
    def _find_music_file(self):
        """البحث عن ملف الموسيقى بصيغ مختلفة"""
        music_extensions = ['.mp3', '.wav', '.ogg']  # إزالة .m4a لأنه غير مدعوم
        for ext in music_extensions:
            if self.is_bundled:
                # البحث في الموارد المدمجة
                music_file = self._get_resource_path(f"music{ext}")
                if music_file.exists():
                    return music_file
            else:
                # البحث في المجلد المحلي
                music_file = Path(f"music{ext}")
                if music_file.exists():
                    return music_file
        return None  # لا يوجد ملف موسيقى
    
    def _setup_paths(self):
        """إعداد المسارات بناءً على نوع التشغيل (مطور أم مجمع)"""
        if getattr(sys, 'frozen', False):
            # التشغيل كملف تنفيذي مجمع
            self.is_bundled = True
            self.bundle_dir = Path(sys._MEIPASS)
            self.app_dir = Path(sys.executable).parent
            
            # إنشاء مجلد Patch Data مؤقت من الموارد المدمجة
            self.patch_data_path = self._extract_embedded_resources()
            
            # إنشاء مجلد Backup Data في نفس مكان البرنامج
            self.backup_data_path = self.app_dir / "Backup Data"
        else:
            # التشغيل في وضع التطوير
            self.is_bundled = False
            self.app_dir = Path.cwd()
            self.patch_data_path = Path("Patch Data")
            self.backup_data_path = Path("Backup Data")
    
    def _extract_embedded_resources(self):
        """استخراج موارد Patch Data من الملف المجمع"""
        try:
            # إنشاء مجلد مؤقت لـ Patch Data
            temp_patch_dir = Path(tempfile.mkdtemp(prefix="stellaris_patch_"))
            
            # البحث عن ملفات Patch Data في الموارد المدمجة
            patch_source = self.bundle_dir / "Patch Data"
            
            if patch_source.exists():
                # نسخ جميع ملفات Patch Data إلى المجلد المؤقت
                shutil.copytree(patch_source, temp_patch_dir / "Patch Data")
                return temp_patch_dir / "Patch Data"
            else:
                # في حالة عدم وجود المجلد، إنشاء مجلد فارغ
                patch_dir = temp_patch_dir / "Patch Data"
                patch_dir.mkdir(parents=True, exist_ok=True)
                return patch_dir
        except Exception as e:
            print(f"خطأ في استخراج الموارد: {e}")
            # في حالة الفشل، استخدام مجلد محلي
            patch_dir = Path("Patch Data")
            patch_dir.mkdir(exist_ok=True)
            return patch_dir
    
    def _get_resource_path(self, relative_path):
        """الحصول على مسار المورد بناءً على نوع التشغيل"""
        if self.is_bundled:
            return self.bundle_dir / relative_path
        else:
            return Path(relative_path)
    
    def _setup_window(self):
        """إعداد النافذة الرئيسية الصغيرة والظريفة"""
        self.root.title("🌟 Stellaris Patch AR")
        self.root.geometry("650x520")  # زيادة الارتفاع لاستيعاب التذكير
        self.root.resizable(False, False)  # حجم ثابت للشكل الظريف
        self.root.configure(bg=self.colors['background'])
        
        # استخدام أيقونة مخصصة
        try:
            icon_path = self._get_resource_path("1.ico")
            if icon_path.exists():
                self.root.iconbitmap(str(icon_path))
            else:
                # إذا لم توجد الأيقونة، أزل الأيقونة الافتراضية
                self.root.iconbitmap("")
        except Exception:
            pass
        
        # وضع النافذة في المنتصف
        self._center_window()
        
        # تكوين الشبكة
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        
        # تطبيق نمط عصري
        self._configure_styles()

    def _center_window(self):
        """وضع النافذة في وسط الشاشة"""
        # تحديث النافذة للحصول على الأبعاد الفعلية
        self.root.update_idletasks()
        
        # الحصول على أبعاد النافذة
        window_width = 650
        window_height = 520
        
        # الحصول على أبعاد الشاشة
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        # حساب الموضع المركزي
        center_x = int(screen_width/2 - window_width/2)
        center_y = int(screen_height/2 - window_height/2)
        
        # وضع النافذة في الموضع المحسوب
        self.root.geometry(f'{window_width}x{window_height}+{center_x}+{center_y}')

    def _apply_icon_to_window(self, window):
        """تطبيق الأيقونة المخصصة على نافذة"""
        try:
            icon_path = self._get_resource_path("1.ico")
            if icon_path.exists():
                window.iconbitmap(str(icon_path))
            else:
                window.iconbitmap("")
        except Exception:
            pass
    
    def _configure_styles(self):
        """تكوين الأنماط العصرية"""
        style = ttk.Style()
        
        # نمط الإطارات
        style.configure(
            "Modern.TFrame",
            background=self.colors['card'],
            relief="flat",
            borderwidth=0
        )
        
        style.configure(
            "Card.TFrame",
            background=self.colors['card'],
            relief="flat",
            borderwidth=1
        )
        
        # نمط الأزرار العصرية
        style.configure(
            "Primary.TButton",
            background=self.colors['primary'],
            foreground="white",
            borderwidth=0,
            focuscolor="none",
            font=("Segoe UI", 11, "bold"),
            padding=(20, 12)
        )
        
        style.map(
            "Primary.TButton",
            background=[("active", self.colors['primary_light']),
                       ("pressed", "#4f46e5")]
        )
        
        style.configure(
            "Secondary.TButton",
            background=self.colors['secondary'],
            foreground="white",
            borderwidth=0,
            focuscolor="none",
            font=("Segoe UI", 11, "bold"),
            padding=(20, 12)
        )
        
        style.map(
            "Secondary.TButton",
            background=[("active", "#34d399"),
                       ("pressed", "#059669")]
        )
        
        style.configure(
            "Outline.TButton",
            background=self.colors['surface'],
            foreground=self.colors['text_primary'],
            borderwidth=2,
            focuscolor="none",
            font=("Segoe UI", 11),
            padding=(20, 12)
        )
        
        # نمط العناوين
        style.configure(
            "Title.TLabel",
            background=self.colors['background'],
            foreground=self.colors['text_primary'],
            font=("Segoe UI", 28, "bold")
        )
        
        style.configure(
            "Subtitle.TLabel",
            background=self.colors['background'],
            foreground=self.colors['text_secondary'],
            font=("Segoe UI", 14)
        )
        
        style.configure(
            "CardTitle.TLabel",
            background=self.colors['card'],
            foreground=self.colors['text_primary'],
            font=("Segoe UI", 16, "bold")
        )
        
        style.configure(
            "CardText.TLabel",
            background=self.colors['card'],
            foreground=self.colors['text_secondary'],
            font=("Segoe UI", 11)
        )
        
        # نمط شريط التقدم العصري
        style.configure(
            "Modern.Horizontal.TProgressbar",
            background=self.colors['primary'],
            troughcolor=self.colors['border'],
            borderwidth=0,
            lightcolor=self.colors['primary'],
            darkcolor=self.colors['primary']
        )
    
    def _create_modern_interface(self):
        """إنشاء الواجهة الصغيرة والظريفة"""
        # الحاوي الرئيسي مع padding مناسب للحجم الصغير
        main_container = tk.Frame(
            self.root,
            bg=self.colors['background'],
            padx=20,
            pady=15
        )
        main_container.grid(row=0, column=0, sticky="nsew")
        main_container.grid_rowconfigure(5, weight=1)
        main_container.grid_columnconfigure(0, weight=1)
        
        # === قسم العنوان الصغير ===
        self._create_compact_header(main_container)
        
        # === بطاقات الحالة المدمجة ===
        self._create_compact_status_cards(main_container)
        
        # === بطاقة العمليات المدمجة ===
        self._create_compact_actions_card(main_container)
        
        # === تذكير مهم ===
        self._create_important_reminder(main_container)
        
        # === شريط التقدم البسيط ===
        self._create_simple_progress(main_container)
        
        # === شريط الحالة المدمج ===
        self._create_compact_status_bar(main_container)
    
    def _create_compact_header(self, parent):
        """إنشاء رأس الصفحة المدمج والظريف"""
        header_frame = tk.Frame(parent, bg=self.colors['background'])
        header_frame.grid(row=0, column=0, sticky="ew", pady=(0, 15))
        header_frame.grid_columnconfigure(0, weight=1)
        
        # العنوان المدمج
        title_container = tk.Frame(header_frame, bg=self.colors['background'])
        title_container.grid(row=0, column=0)
        
        # أيقونة صغيرة ولطيفة
        icon_label = tk.Label(
            title_container,
            text="🌟",
            font=("Segoe UI Emoji", 20),
            bg=self.colors['background'],
            fg=self.colors['primary']
        )
        icon_label.grid(row=0, column=0, padx=(0, 8))
        
        # العنوان المدمج
        title_label = tk.Label(
            title_container,
            text="Stellaris Patch AR",
            font=("Segoe UI", 18, "bold"),
            bg=self.colors['background'],
            fg=self.colors['text_primary']
        )
        title_label.grid(row=0, column=1)
        
        # النسخة الصغيرة
        version_label = tk.Label(
            title_container,
            text="v1.0",
            font=("Segoe UI", 10, "bold"),
            bg=self.colors['primary'],
            fg="white",
            padx=6,
            pady=2
        )
        version_label.grid(row=0, column=2, padx=(8, 0), sticky="s")
        
        # زر كتم الموسيقى الصغير
        self.music_btn = tk.Button(
            title_container,
            text="🎵",
            font=("Segoe UI Emoji", 12),
            bg=self.colors['background'],
            fg=self.colors['text_primary'],
            relief="flat",
            bd=0,
            width=2,
            height=1,
            cursor="hand2",
            command=self._toggle_music
        )
        self.music_btn.grid(row=0, column=3, padx=(8, 0), sticky="s")
        
        # الوصف المدمج
        desc_label = tk.Label(
            header_frame,
            text="Arabic Translation Tool ✨",
            font=("Segoe UI", 11),
            bg=self.colors['background'],
            fg=self.colors['text_secondary']
        )
        desc_label.grid(row=1, column=0, pady=(8, 0))
    
    def _create_compact_status_cards(self, parent):
        """إنشاء بطاقات الحالة المدمجة والصغيرة"""
        cards_frame = tk.Frame(parent, bg=self.colors['background'])
        cards_frame.grid(row=1, column=0, sticky="ew", pady=(0, 15))
        cards_frame.grid_columnconfigure((0, 1, 2), weight=1)
        
        # بطاقة ملفات التصحيح
        self.patch_card = self._create_compact_card(
            cards_frame, 0, "📁", "Patch Files", "Checking...", self.colors['primary']
        )
        
        # بطاقة Stellaris
        self.stellaris_card = self._create_compact_card(
            cards_frame, 1, "🎮", "Stellaris", "Not selected", self.colors['accent']
        )
        
        # بطاقة النسخ الاحتياطية
        self.backup_card = self._create_compact_card(
            cards_frame, 2, "🛡️", "Backups", "None", self.colors['secondary']
        )
    
    def _create_compact_card(self, parent, column, icon, title, subtitle, color):
        """إنشاء بطاقة معلومات مدمجة وصغيرة"""
        card_frame = tk.Frame(
            parent,
            bg=self.colors['card'],
            relief="flat",
            bd=1,
            highlightbackground=self.colors['border'],
            highlightthickness=1
        )
        card_frame.grid(row=0, column=column, sticky="ew", padx=5)
        card_frame.grid_columnconfigure(1, weight=1)
        
        # الأيقونة الصغيرة
        icon_frame = tk.Frame(card_frame, bg=color, width=35, height=35)
        icon_frame.grid(row=0, column=0, rowspan=2, padx=8, pady=8, sticky="ns")
        icon_frame.grid_propagate(False)
        
        icon_label = tk.Label(
            icon_frame,
            text=icon,
            font=("Segoe UI Emoji", 16),
            bg=color,
            fg="white"
        )
        icon_label.place(relx=0.5, rely=0.5, anchor="center")
        
        # النصوص المدمجة
        title_label = tk.Label(
            card_frame,
            text=title,
            font=("Segoe UI", 10, "bold"),
            bg=self.colors['card'],
            fg=self.colors['text_primary'],
            anchor="w"
        )
        title_label.grid(row=0, column=1, sticky="ew", padx=(0, 8), pady=(8, 2))
        
        subtitle_label = tk.Label(
            card_frame,
            text=subtitle,
            font=("Segoe UI", 9),
            bg=self.colors['card'],
            fg=self.colors['text_secondary'],
            anchor="w"
        )
        subtitle_label.grid(row=1, column=1, sticky="ew", padx=(0, 8), pady=(0, 8))
        
        return {
            'frame': card_frame,
            'title': title_label,
            'subtitle': subtitle_label
        }
    
    def _create_info_card(self, parent, column, icon, title, subtitle, color):
        """إنشاء بطاقة معلومات عصرية"""
        card_frame = tk.Frame(
            parent,
            bg=self.colors['card'],
            relief="flat",
            bd=1,
            highlightbackground=self.colors['border'],
            highlightthickness=1
        )
        card_frame.grid(row=0, column=column, sticky="ew", padx=10)
        card_frame.grid_columnconfigure(1, weight=1)
        
        # تأثير الظل (محاكاة)
        shadow_frame = tk.Frame(
            parent,
            bg=self.colors['shadow'],
            height=2
        )
        shadow_frame.grid(row=1, column=column, sticky="ew", padx=12, pady=(0, 5))
        
        # الأيقونة
        icon_frame = tk.Frame(card_frame, bg=color, width=60, height=60)
        icon_frame.grid(row=0, column=0, rowspan=2, padx=20, pady=20, sticky="ns")
        icon_frame.grid_propagate(False)
        
        icon_label = tk.Label(
            icon_frame,
            text=icon,
            font=("Segoe UI Emoji", 24),
            bg=color,
            fg="white"
        )
        icon_label.place(relx=0.5, rely=0.5, anchor="center")
        
        # النصوص
        title_label = tk.Label(
            card_frame,
            text=title,
            font=("Segoe UI", 14, "bold"),
            bg=self.colors['card'],
            fg=self.colors['text_primary'],
            anchor="w"
        )
        title_label.grid(row=0, column=1, sticky="ew", padx=(0, 20), pady=(20, 5))
        
        subtitle_label = tk.Label(
            card_frame,
            text=subtitle,
            font=("Segoe UI", 11),
            bg=self.colors['card'],
            fg=self.colors['text_secondary'],
            anchor="w"
        )
        subtitle_label.grid(row=1, column=1, sticky="ew", padx=(0, 20), pady=(0, 20))
        
        return {
            'frame': card_frame,
            'title': title_label,
            'subtitle': subtitle_label
        }
    
    def _create_compact_actions_card(self, parent):
        """إنشاء بطاقة العمليات المدمجة والصغيرة"""
        actions_frame = tk.Frame(
            parent,
            bg=self.colors['card'],
            relief="flat",
            bd=1,
            highlightbackground=self.colors['border'],
            highlightthickness=1
        )
        actions_frame.grid(row=2, column=0, sticky="ew", pady=(0, 15))
        actions_frame.grid_columnconfigure((0, 1), weight=1)
        
        # عنوان البطاقة المدمج
        card_title = tk.Label(
            actions_frame,
            text="🎯 Actions",
            font=("Segoe UI", 12, "bold"),
            bg=self.colors['card'],
            fg=self.colors['text_primary']
        )
        card_title.grid(row=0, column=0, columnspan=2, pady=(12, 8), padx=15, sticky="w")
        
        # الأزرار المدمجة
        button_config = {
            'width': 18,
            'font': ("Segoe UI", 9, "bold"),
            'relief': "flat",
            'bd': 0,
            'cursor': "hand2"
        }
        
        # الصف الأول - أزرار صغيرة
        self.browse_btn = tk.Button(
            actions_frame,
            text="📂 Select Folder",
            bg=self.colors['primary'],
            fg="white",
            command=self.browse_stellaris_folder,
            **button_config
        )
        self.browse_btn.grid(row=1, column=0, padx=(15, 8), pady=(0, 8), sticky="ew")
        
        self.backup_btn = tk.Button(
            actions_frame,
            text="🛡️ Backup",
            bg=self.colors['secondary'],
            fg="white",
            command=self.create_backup,
            state="disabled",
            **button_config
        )
        self.backup_btn.grid(row=1, column=1, padx=(8, 15), pady=(0, 8), sticky="ew")
        
        # الصف الثاني
        self.apply_btn = tk.Button(
            actions_frame,
            text="⚡ Apply Patch",
            bg=self.colors['accent'],
            fg="white",
            command=self.apply_korean_patch,
            state="disabled",
            **button_config
        )
        self.apply_btn.grid(row=2, column=0, padx=(15, 8), pady=(0, 8), sticky="ew")
        
        self.restore_btn = tk.Button(
            actions_frame,
            text="🔄 Restore",
            bg=self.colors['text_secondary'],
            fg="white",
            command=self.restore_original_files,
            state="disabled",
            **button_config
        )
        self.restore_btn.grid(row=2, column=1, padx=(8, 15), pady=(0, 8), sticky="ew")
        
        # زر إدارة النسخ مدمج
        self.manage_btn = tk.Button(
            actions_frame,
            text="📋 Manage Backups",
            bg=self.colors['text_primary'],
            fg="white",
            command=self.manage_backups,
            state="disabled",
            font=("Segoe UI", 9, "bold"),
            width=18,
            relief="flat",
            bd=0,
            cursor="hand2"
        )
        self.manage_btn.grid(row=3, column=0, padx=(15, 8), pady=(0, 8), sticky="ew")
        
        # زر حول البرنامج
        self.about_btn = tk.Button(
            actions_frame,
            text="ℹ️ About",
            bg="#8b5cf6",  # Purple
            fg="white",
            command=self.show_about,
            font=("Segoe UI", 9, "bold"),
            width=18,
            relief="flat",
            bd=0,
            cursor="hand2"
        )
        self.about_btn.grid(row=3, column=1, padx=(8, 15), pady=(0, 12), sticky="ew")
        
        # إضافة تأثيرات hover للأزرار
        self._add_compact_button_effects()
    
    def _add_button_effects(self):
        """إضافة تأثيرات hover للأزرار"""
        buttons = [
            (self.browse_btn, self.colors['primary'], "#4f46e5"),
            (self.backup_btn, self.colors['secondary'], "#059669"),
            (self.apply_btn, self.colors['accent'], "#d97706"),
            (self.restore_btn, self.colors['text_secondary'], "#475569"),
            (self.manage_btn, self.colors['text_primary'], "#334155")
        ]
        
        for btn, normal_color, hover_color in buttons:
            btn.bind("<Enter>", lambda e, color=hover_color: e.widget.config(bg=color))
            btn.bind("<Leave>", lambda e, color=normal_color: e.widget.config(bg=color))
    
    def _add_compact_button_effects(self):
        """إضافة تأثيرات hover للأزرار المدمجة"""
        buttons = [
            (self.browse_btn, self.colors['primary'], "#4f46e5"),
            (self.backup_btn, self.colors['secondary'], "#059669"),
            (self.apply_btn, self.colors['accent'], "#d97706"),
            (self.restore_btn, self.colors['text_secondary'], "#475569"),
            (self.manage_btn, self.colors['text_primary'], "#334155"),
            (self.about_btn, "#8b5cf6", "#7c3aed")  # Purple shades
            # إزالة زر الموسيقى من التأثيرات
        ]
        
        for btn, normal_color, hover_color in buttons:
            btn.bind("<Enter>", lambda e, color=hover_color: e.widget.config(bg=color))
            btn.bind("<Leave>", lambda e, color=normal_color: e.widget.config(bg=color))
    
    def _create_important_reminder(self, parent):
        """إنشاء تذكير مهم للمستخدم"""
        reminder_frame = tk.Frame(
            parent,
            bg="#fef3c7",  # Light yellow background
            relief="solid",
            bd=2
        )
        reminder_frame.grid(row=3, column=0, sticky="ew", pady=(0, 15))
        reminder_frame.grid_columnconfigure(0, weight=1)
        
        # أيقونة تحذير
        warning_container = tk.Frame(reminder_frame, bg="#fef3c7")
        warning_container.grid(row=0, column=0, pady=(8, 0))
        
        warning_icon = tk.Label(
            warning_container,
            text="⚠️",
            font=("Segoe UI Emoji", 16),
            bg="#fef3c7",
            fg="#d97706"
        )
        warning_icon.pack(side="left", padx=(0, 5))
        
        warning_title = tk.Label(
            warning_container,
            text="تذكير مهم",
            font=("Segoe UI", 12, "bold"),
            bg="#fef3c7",
            fg="#92400e"
        )
        warning_title.pack(side="left")
        
        # نص التذكير
        reminder_text = tk.Label(
            reminder_frame,
            text="يجب اختيار اللغة الكورية من لانشر بارادوكس قبل تشغيل اللعبة",
            font=("Segoe UI", 10, "bold"),
            bg="#fef3c7",
            fg="#92400e",
            wraplength=500,
            justify="center"
        )
        reminder_text.grid(row=1, column=0, pady=(5, 10), padx=15)
    
    def _create_simple_progress(self, parent):
        """إنشاء شريط التقدم البسيط والمدمج"""
        progress_frame = tk.Frame(parent, bg=self.colors['background'])
        progress_frame.grid(row=4, column=0, sticky="ew", pady=(0, 10))
        progress_frame.grid_columnconfigure(0, weight=1)
        
        # عنوان مدمج
        progress_title = tk.Label(
            progress_frame,
            text="📊 Progress",
            font=("Segoe UI", 10, "bold"),
            bg=self.colors['background'],
            fg=self.colors['text_primary']
        )
        progress_title.grid(row=0, column=0, pady=(0, 5), sticky="w")
        
        # شريط التقدم البسيط
        self.progress_bg = tk.Frame(
            progress_frame,
            bg=self.colors['border'],
            height=6
        )
        self.progress_bg.grid(row=1, column=0, sticky="ew", pady=(0, 8))
        
        self.progress_fill = tk.Frame(
            self.progress_bg,
            bg=self.colors['primary'],
            height=6
        )
        self.progress_fill.place(x=0, y=0, relheight=1, width=0)
        
        # تفاصيل مدمجة
        details_frame = tk.Frame(progress_frame, bg=self.colors['background'])
        details_frame.grid(row=2, column=0, sticky="ew")
        details_frame.grid_columnconfigure(1, weight=1)
        
        self.progress_label = tk.Label(
            details_frame,
            text="0%",
            font=("Segoe UI", 10, "bold"),
            bg=self.colors['background'],
            fg=self.colors['primary']
        )
        self.progress_label.grid(row=0, column=0, sticky="w")
        
        self.current_file_label = tk.Label(
            details_frame,
            textvariable=self.current_file_var,
            font=("Segoe UI", 8),
            bg=self.colors['background'],
            fg=self.colors['text_secondary']
        )
        self.current_file_label.grid(row=0, column=1, sticky="e")
    
    def _create_compact_status_bar(self, parent):
        """إنشاء شريط الحالة المدمج والصغير"""
        status_frame = tk.Frame(
            parent,
            bg=self.colors['primary'],
            height=35
        )
        status_frame.grid(row=5, column=0, sticky="ew")
        status_frame.grid_columnconfigure(1, weight=1)
        status_frame.grid_propagate(False)
        
        # أيقونة الحالة الصغيرة
        status_icon = tk.Label(
            status_frame,
            text="✨",
            font=("Segoe UI Emoji", 12),
            bg=self.colors['primary'],
            fg="white"
        )
        status_icon.grid(row=0, column=0, padx=(15, 8), sticky="w")
        
        # نص الحالة المدمج
        self.status_label = tk.Label(
            status_frame,
            textvariable=self.status_var,
            font=("Segoe UI", 10, "bold"),
            bg=self.colors['primary'],
            fg="white"
        )
        self.status_label.grid(row=0, column=1, sticky="w")
        
        # معلومات مدمجة
        info_label = tk.Label(
            status_frame,
            text="v1.0",
            font=("Segoe UI", 8),
            bg=self.colors['primary'],
            fg=self.colors['primary_light']
        )
        info_label.grid(row=0, column=2, padx=(0, 15), sticky="e")
        
        status_frame.grid_columnconfigure(1, weight=1)
    
    def _update_progress(self, percentage: float, message: str = "", current_file: str = ""):
        """تحديث شريط التقدم العصري"""
        # تحديث شريط التقدم المخصص
        progress_width = int((percentage / 100) * self.progress_bg.winfo_width())
        if self.progress_bg.winfo_width() > 1:  # تأكد من أن العرض محسوب
            self.progress_fill.place(width=max(progress_width, 0))
        
        # تحديث النص
        self.progress_label.config(text=f"{percentage:.1f}%")
        
        if message:
            self.status_var.set(message)
        if current_file:
            self.current_file_var.set(current_file)
        
        self.root.update_idletasks()
    
    def _update_status(self):
        """تحديث حالة البطاقات"""
        # بطاقة ملفات التصحيح
        patch_exists = self.patch_data_path.exists() and any(self.patch_data_path.rglob("*.yml"))
        if patch_exists:
            file_count = len(list(self.patch_data_path.rglob("*.yml")))
            self.patch_card['subtitle'].config(
                text=f"{file_count} files ready",
                fg=self.colors['secondary']
            )
        else:
            self.patch_card['subtitle'].config(
                text="Not found",
                fg=self.colors['error']
            )
        
        # بطاقة Stellaris
        stellaris_valid = self.stellaris_path and self.stellaris_path.exists()
        if stellaris_valid:
            self.stellaris_card['subtitle'].config(
                text=f"Selected: {self.stellaris_path.name}",
                fg=self.colors['secondary']
            )
        else:
            self.stellaris_card['subtitle'].config(
                text="Not selected",
                fg=self.colors['text_secondary']
            )
        
        # بطاقة النسخ الاحتياطية
        backup_exists = self.backup_data_path.exists() and any(self.backup_data_path.iterdir())
        if backup_exists:
            backup_count = len(list(self.backup_data_path.iterdir()))
            self.backup_card['subtitle'].config(
                text=f"{backup_count} backups",
                fg=self.colors['secondary']
            )
        else:
            self.backup_card['subtitle'].config(
                text="None",
                fg=self.colors['text_secondary']
            )
        
        # تحديث حالة الأزرار
        ready_for_backup = stellaris_valid and patch_exists
        ready_for_apply = ready_for_backup
        ready_for_restore = backup_exists
        ready_for_manage = backup_exists
        
        self._update_button_state(self.backup_btn, ready_for_backup)
        self._update_button_state(self.apply_btn, ready_for_apply)
        self._update_button_state(self.restore_btn, ready_for_restore)
        self._update_button_state(self.manage_btn, ready_for_manage)
    
    def _update_button_state(self, button, enabled):
        """تحديث حالة الأزرار مع تأثيرات بصرية"""
        if enabled:
            button.config(state="normal", cursor="hand2")
        else:
            button.config(state="disabled", cursor="arrow")
    
    # === باقي الوظائف نفسها من الإصدار السابق ===
    
    def browse_stellaris_folder(self):
        """تصفح مجلد Stellaris"""
        folder = filedialog.askdirectory(
            title="Select Stellaris Folder",
            initialdir="C:/Program Files (x86)/Steam/steamapps/common/"
        )
        
        if folder:
            self.stellaris_path = Path(folder)
            self._update_progress(50, "Verifying Stellaris folder...", "stellaris.exe")
            self.root.after(500, self._verify_stellaris_folder)
    
    def _verify_stellaris_folder(self):
        """التحقق من صحة مجلد Stellaris"""
        if self.stellaris_path and (self.stellaris_path / "stellaris.exe").exists():
            self._update_progress(100, "Stellaris folder selected successfully ✅", "")
            self.root.after(2000, lambda: self._update_progress(0, "Ready to work 🚀", ""))
        else:
            messagebox.showerror("Error", "Selected folder does not contain stellaris.exe")
            self.stellaris_path = None
            self._update_progress(0, "Failed to select Stellaris folder ❌", "")
        
        self._update_status()
    
    def create_backup(self):
        """إنشاء نسخة احتياطية"""
        if not self._validate_paths():
            return
        
        def backup_process():
            try:
                self._update_progress(5, "Starting backup process...", "")
                
                # إنشاء اسم النسخة الاحتياطية
                now = datetime.now()
                version = self._get_next_backup_version()
                backup_name = f"Backup v{version} {now.strftime('%H-%M %d-%m-%Y')}"
                backup_dir = self.backup_data_path / backup_name
                
                # إنشاء مجلد النسخة الاحتياطية
                backup_dir.mkdir(parents=True, exist_ok=True)
                
                self._update_progress(15, "Collecting files to backup...", "")
                
                # جمع الملفات للنسخ الاحتياطي
                files_to_backup = self._collect_backup_files()
                
                if not files_to_backup:
                    self._update_progress(100, "No files to backup", "")
                    messagebox.showinfo("Info", "No files to backup")
                    return
                
                self._update_progress(25, f"Backing up {len(files_to_backup)} files...", "")
                
                # نسخ الملفات
                copied_files = []
                progress_per_file = 60 / len(files_to_backup)
                current_progress = 25
                
                for source_file, relative_path in files_to_backup:
                    try:
                        dest_file = backup_dir / relative_path
                        dest_file.parent.mkdir(parents=True, exist_ok=True)
                        
                        shutil.copy2(source_file, dest_file)
                        copied_files.append(relative_path)
                        
                        current_progress += progress_per_file
                        self._update_progress(current_progress, f"Copying: {source_file.name}", relative_path)
                        time.sleep(0.05)
                        
                    except Exception as e:
                        print(f"Error copying {source_file}: {e}")
                
                # حفظ معلومات النسخة الاحتياطية
                self._update_progress(90, "Saving backup information...", "backup_info.json")
                
                backup_info = {
                    "name": backup_name,
                    "version": version,
                    "created_at": now.isoformat(),
                    "stellaris_path": str(self.stellaris_path),
                    "files_count": len(copied_files),
                    "files": copied_files
                }
                
                with open(backup_dir / "backup_info.json", "w", encoding="utf-8") as f:
                    json.dump(backup_info, f, indent=2, ensure_ascii=False)
                
                self._update_progress(100, "Backup created successfully! 🎉", "")
                
                messagebox.showinfo(
                    "Success!",
                    f"Backup created successfully!\n\n"
                    f"Name: {backup_name}\n"
                    f"Files: {len(copied_files)}\n"
                    f"Location: {backup_dir}"
                )
                
            except Exception as e:
                self._update_progress(0, f"Backup failed: {str(e)}", "")
                messagebox.showerror("Error", f"Backup error:\n{str(e)}")
            
            finally:
                self._update_status()
                self.root.after(3000, lambda: self._update_progress(0, "Ready to work 🚀", ""))
        
        threading.Thread(target=backup_process, daemon=True).start()
    
    def apply_korean_patch(self):
        """تطبيق التصحيح الكوري"""
        if not self._validate_paths():
            return
        
        # تأكيد العملية
        patch_files = list(self.patch_data_path.rglob("*.yml"))
        font_files = list(self.patch_data_path.rglob("*.ttf")) + list(self.patch_data_path.rglob("*.otf"))
        total_files = len(patch_files) + len(font_files)
        
        result = messagebox.askyesno(
            "Confirm Application",
            f"Apply Korean patch?\n\n"
            f"Will apply {total_files} files:\n"
            f"• {len(patch_files)} translation files\n"
            f"• {len(font_files)} fonts\n\n"
            "Auto backup will be created before application."
        )
        
        if not result:
            return
        
        def apply_process():
            try:
                # إنشاء نسخة احتياطية تلقائية
                self._update_progress(5, "Creating auto backup...", "")
                backup_success = self._create_auto_backup()
                
                if not backup_success:
                    raise Exception("Failed to create auto backup")
                
                # تطبيق الملفات
                self._update_progress(25, "Applying Korean patch files...", "")
                
                applied_files = []
                all_files = patch_files + font_files
                progress_per_file = 65 / len(all_files)
                current_progress = 25
                
                for patch_file in all_files:
                    try:
                        relative_path = patch_file.relative_to(self.patch_data_path)
                        
                        # تحديد المسار الوجهة
                        if str(relative_path).startswith("localisation/korean/"):
                            # تحويل korean إلى english
                            dest_path = str(relative_path).replace("localisation/korean/", "localisation/english/")
                        else:
                            # باقي الملفات تبقى كما هي
                            dest_path = str(relative_path)
                        
                        dest_file = self.stellaris_path / dest_path
                        dest_file.parent.mkdir(parents=True, exist_ok=True)
                        
                        shutil.copy2(patch_file, dest_file)
                        applied_files.append(dest_path)
                        
                        current_progress += progress_per_file
                        self._update_progress(current_progress, f"Applying: {patch_file.name}", dest_path)
                        time.sleep(0.03)
                        
                    except Exception as e:
                        print(f"Error applying {patch_file}: {e}")
                
                self._update_progress(95, "Finalizing application...", "")
                time.sleep(0.5)
                
                self._update_progress(100, "Korean patch applied successfully! 🎉", "")
                
                messagebox.showinfo(
                    "Success!",
                    f"Korean patch applied successfully!\n\n"
                    f"Applied files: {len(applied_files)}\n"
                    f"Auto backup created\n\n"
                    "You can now run Stellaris and enjoy Korean translation!"
                )
                
            except Exception as e:
                self._update_progress(0, f"Application failed: {str(e)}", "")
                messagebox.showerror("Error", f"Error applying patch:\n{str(e)}")
            
            finally:
                self._update_status()
                self.root.after(3000, lambda: self._update_progress(0, "Ready to work 🚀", ""))
        
        threading.Thread(target=apply_process, daemon=True).start()
    
    def restore_original_files(self):
        """استعادة الملفات الأصلية"""
        if not self.backup_data_path.exists():
            messagebox.showwarning("Warning", "No backups available for restoration")
            return
        
        # البحث عن أحدث نسخة احتياطية
        backups = sorted(self.backup_data_path.iterdir(), key=lambda x: x.stat().st_mtime, reverse=True)
        if not backups:
            messagebox.showwarning("Warning", "No backups available for restoration")
            return
        
        latest_backup = backups[0]
        
        result = messagebox.askyesno(
            "Confirm Restoration",
            f"Restore original files?\n\n"
            f"Will use backup:\n{latest_backup.name}\n\n"
            "All Korean patch files will be replaced with original files."
        )
        
        if not result:
            return
        
        def restore_process():
            try:
                self._update_progress(10, "Starting restoration process...", "")
                
                # قراءة معلومات النسخة الاحتياطية
                info_file = latest_backup / "backup_info.json"
                if info_file.exists():
                    with open(info_file, "r", encoding="utf-8") as f:
                        backup_info = json.load(f)
                    files_to_restore = backup_info.get("files", [])
                else:
                    # إذا لم توجد معلومات، استخدم جميع الملفات
                    files_to_restore = [str(f.relative_to(latest_backup)) for f in latest_backup.rglob("*") if f.is_file() and f.name != "backup_info.json"]
                
                self._update_progress(25, f"Restoring {len(files_to_restore)} files...", "")
                
                # استعادة الملفات
                restored_count = 0
                progress_per_file = 65 / len(files_to_restore) if files_to_restore else 65
                current_progress = 25
                
                for relative_path in files_to_restore:
                    try:
                        backup_file = latest_backup / relative_path
                        dest_file = self.stellaris_path / relative_path
                        
                        if backup_file.exists():
                            dest_file.parent.mkdir(parents=True, exist_ok=True)
                            shutil.copy2(backup_file, dest_file)
                            restored_count += 1
                            
                            current_progress += progress_per_file
                            self._update_progress(current_progress, f"Restoring: {backup_file.name}", relative_path)
                            time.sleep(0.03)
                    
                    except Exception as e:
                        print(f"Error restoring {relative_path}: {e}")
                
                self._update_progress(95, "Finalizing restoration...", "")
                time.sleep(0.5)
                
                self._update_progress(100, "Original files restored successfully! 🎉", "")
                
                messagebox.showinfo(
                    "Success!",
                    f"Original files restored successfully!\n\n"
                    f"Restored files: {restored_count}\n"
                    f"From backup: {latest_backup.name}"
                )
                
            except Exception as e:
                self._update_progress(0, f"Restoration failed: {str(e)}", "")
                messagebox.showerror("Error", f"Error restoring files:\n{str(e)}")
            
            finally:
                self._update_status()
                self.root.after(3000, lambda: self._update_progress(0, "Ready to work 🚀", ""))
        
        threading.Thread(target=restore_process, daemon=True).start()
    
    def manage_backups(self):
        """إدارة النسخ الاحتياطية"""
        if not self.backup_data_path.exists():
            messagebox.showinfo("Info", "No backups to manage")
            return
        
        # إنشاء نافذة الإدارة المدمجة
        manage_window = tk.Toplevel(self.root)
        manage_window.title("🗂️ Manage Backups")
        manage_window.geometry("600x400")
        manage_window.resizable(False, False)
        manage_window.configure(bg=self.colors['background'])
        
        # تطبيق الأيقونة المخصصة
        self._apply_icon_to_window(manage_window)
        
        # وضع النافذة في المنتصف
        manage_window.transient(self.root)
        manage_window.grab_set()
        
        # الحاوي الرئيسي المدمج
        main_frame = tk.Frame(manage_window, bg=self.colors['background'], padx=20, pady=20)
        main_frame.pack(fill="both", expand=True)
        
        # العنوان المدمج
        title_label = tk.Label(
            main_frame,
            text="📋 Manage Backups",
            font=("Segoe UI", 14, "bold"),
            bg=self.colors['background'],
            fg=self.colors['text_primary']
        )
        title_label.pack(pady=(0, 15))
        
        # قائمة النسخ الاحتياطية المدمجة
        list_frame = tk.Frame(main_frame, bg=self.colors['card'])
        list_frame.pack(fill="both", expand=True, pady=(0, 15))
        
        # إنشاء Treeview مدمج
        columns = ("name", "date", "files", "size")
        tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=10)
        
        # تكوين الأعمدة
        tree.heading("name", text="Backup Name", anchor="center")
        tree.heading("date", text="Date", anchor="center")
        tree.heading("files", text="Files", anchor="center")
        tree.heading("size", text="Size", anchor="center")
        
        tree.column("name", width=300, anchor="center")
        tree.column("date", width=150, anchor="center")
        tree.column("files", width=100, anchor="center")
        tree.column("size", width=100, anchor="center")
        
        # شريط التمرير
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        
        tree.pack(side="left", fill="both", expand=True, padx=20, pady=20)
        scrollbar.pack(side="right", fill="y", pady=20)
        
        # تحميل النسخ الاحتياطية
        def load_backups():
            for item in tree.get_children():
                tree.delete(item)
            
            for backup_dir in sorted(self.backup_data_path.iterdir(), key=lambda x: x.stat().st_mtime, reverse=True):
                if backup_dir.is_dir():
                    try:
                        # قراءة معلومات النسخة الاحتياطية
                        info_file = backup_dir / "backup_info.json"
                        if info_file.exists():
                            with open(info_file, "r", encoding="utf-8") as f:
                                backup_info = json.load(f)
                            
                            name = backup_info.get("name", backup_dir.name)
                            date = backup_info.get("created_at", "Unknown")
                            if "T" in date:
                                date = datetime.fromisoformat(date).strftime("%Y-%m-%d %H-%M")
                            files_count = backup_info.get("files_count", 0)
                        else:
                            name = backup_dir.name
                            date = datetime.fromtimestamp(backup_dir.stat().st_mtime).strftime("%Y-%m-%d %H-%M")
                            files_count = len(list(backup_dir.rglob("*")))
                        
                        # حساب الحجم
                        total_size = sum(f.stat().st_size for f in backup_dir.rglob("*") if f.is_file())
                        size_mb = total_size / (1024 * 1024)
                        size_str = f"{size_mb:.1f} MB"
                        
                        tree.insert("", "end", values=(name, date, files_count, size_str))
                    
                    except Exception as e:
                        print(f"Error reading backup info {backup_dir.name}: {e}")
        
        load_backups()
        
        # أزرار الإدارة العصرية
        buttons_frame = tk.Frame(main_frame, bg=self.colors['background'])
        buttons_frame.pack(fill="x")
        
        def delete_backup():
            selected = tree.selection()
            if not selected:
                messagebox.showwarning("Warning", "Please select a backup to delete")
                return
            
            backup_name = tree.item(selected[0])["values"][0]
            
            result = messagebox.askyesno(
                "Confirm Deletion",
                f"Delete backup:\n{backup_name}?\n\n"
                "This action cannot be undone!"
            )
            
            if result:
                try:
                    backup_path = self.backup_data_path / backup_name
                    if backup_path.exists():
                        shutil.rmtree(backup_path)
                        messagebox.showinfo("Success", f"Backup deleted: {backup_name}")
                        load_backups()
                        self._update_status()
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to delete backup:\n{str(e)}")
        
        def close_window():
            manage_window.destroy()
        
        # ترتيب الأزرار العصرية
        close_btn = tk.Button(
            buttons_frame,
            text="Close",
            bg=self.colors['text_secondary'],
            fg="white",
            relief="flat",
            bd=0,
            font=("Segoe UI", 11, "bold"),
            padx=20,
            pady=10,
            command=close_window,
            cursor="hand2"
        )
        close_btn.pack(side="left")
        
        refresh_btn = tk.Button(
            buttons_frame,
            text="Refresh",
            bg=self.colors['primary'],
            fg="white",
            relief="flat",
            bd=0,
            font=("Segoe UI", 11, "bold"),
            padx=20,
            pady=10,
            command=load_backups,
            cursor="hand2"
        )
        refresh_btn.pack(side="left", padx=(10, 0))
        
        delete_btn = tk.Button(
            buttons_frame,
            text="Delete",
            bg=self.colors['error'],
            fg="white",
            relief="flat",
            bd=0,
            font=("Segoe UI", 11, "bold"),
            padx=20,
            pady=10,
            command=delete_backup,
            cursor="hand2"
        )
        delete_btn.pack(side="right")
    
    def show_about(self):
        """عرض معلومات حول البرنامج والترجمة العربية"""
        about_window = tk.Toplevel(self.root)
        about_window.title("ℹ️ About - Stellaris Patch AR")
        about_window.geometry("520x450")
        about_window.resizable(False, False)
        about_window.configure(bg=self.colors['background'])
        
        # تطبيق الأيقونة المخصصة
        self._apply_icon_to_window(about_window)
        
        # وضع النافذة في المنتصف
        about_window.transient(self.root)
        about_window.grab_set()
        
        # إنشاء إطار رئيسي مع شريط التمرير
        main_container = tk.Frame(about_window, bg=self.colors['background'])
        main_container.pack(fill="both", expand=True, padx=10, pady=10)
        
        # إنشاء Canvas وشريط التمرير
        canvas = tk.Canvas(
            main_container,
            bg=self.colors['background'],
            highlightthickness=0
        )
        scrollbar = tk.Scrollbar(main_container, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=self.colors['background'])
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # ترتيب العناصر
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # الحاوي للمحتوى
        main_frame = tk.Frame(scrollable_frame, bg=self.colors['background'], padx=20, pady=15)
        main_frame.pack(fill="both", expand=True)
        
        # العنوان
        title_label = tk.Label(
            main_frame,
            text="🌟 Stellaris Patch AR v1.0",
            font=("Segoe UI", 16, "bold"),
            bg=self.colors['background'],
            fg=self.colors['primary']
        )
        title_label.pack(pady=(0, 20))
        
        # معلومات البرنامج
        info_text = """
🔤 Arabic Translation Tool for Stellaris

📖 What this tool does:
• Replaces Korean localization files with Arabic translations
• Installs Arabic fonts that work with Korean character system
• Provides seamless Arabic gaming experience

🎮 How it works:
• The game thinks it's displaying Korean text
• But actually shows Arabic translations
• Arabic fonts render properly in Korean text slots

⚠️ IMPORTANT NOTICE:
You MUST select Korean language in Paradox Launcher
before starting the game for this to work properly!

🛡️ Features:
• Automatic backup system
• Safe file replacement
• Easy restoration
• Comprehensive file management

💡 This tool makes Stellaris fully playable in Arabic
while maintaining game compatibility and performance.
        """
        
        info_label = tk.Label(
            main_frame,
            text=info_text.strip(),
            font=("Segoe UI", 9),
            bg=self.colors['background'],
            fg=self.colors['text_primary'],
            justify="left",
            wraplength=450
        )
        info_label.pack(pady=(0, 15))
        
        # معلومات المترجمين
        translators_frame = tk.Frame(
            main_frame,
            bg=self.colors['card'],
            relief="solid",
            bd=1
        )
        translators_frame.pack(fill="x", pady=(0, 15))
        
        translators_title = tk.Label(
            translators_frame,
            text="👥 Arabic Translators Contact",
            font=("Segoe UI", 12, "bold"),
            bg=self.colors['card'],
            fg=self.colors['primary'],
            pady=10
        )
        translators_title.pack()
        
        discord_label = tk.Label(
            translators_frame,
            text="💬 Discord:",
            font=("Segoe UI", 10, "bold"),
            bg=self.colors['card'],
            fg=self.colors['text_primary']
        )
        discord_label.pack(pady=(0, 5))
        
        # معلومات المترجم الأول
        def copy_yuuyu_id():
            try:
                about_window.clipboard_clear()
                about_window.clipboard_append("yuuyu_gg")
                about_window.update()
                # تغيير النص مؤقتاً للإشارة إلى النسخ
                yuuyu_btn.config(text="✅ Copied!")
                about_window.after(1500, lambda: yuuyu_btn.config(text="📋 Yuuyu: yuuyu_gg"))
            except:
                pass
        
        yuuyu_btn = tk.Button(
            translators_frame,
            text="📋 Yuuyu: yuuyu_gg",
            font=("Segoe UI", 10),
            bg="#5865f2",  # Discord blue
            fg="white",
            relief="flat",
            bd=0,
            cursor="hand2",
            command=copy_yuuyu_id,
            padx=20,
            pady=5
        )
        yuuyu_btn.pack(pady=2)
        
        # معلومات المترجم الثاني
        def copy_drikon_id():
            try:
                about_window.clipboard_clear()
                about_window.clipboard_append("drikonium")
                about_window.update()
                # تغيير النص مؤقتاً للإشارة إلى النسخ
                drikon_btn.config(text="✅ Copied!")
                about_window.after(1500, lambda: drikon_btn.config(text="📋 Drikon: drikonium"))
            except:
                pass
        
        drikon_btn = tk.Button(
            translators_frame,
            text="📋 Drikon: drikonium",
            font=("Segoe UI", 10),
            bg="#5865f2",  # Discord blue
            fg="white",
            relief="flat",
            bd=0,
            cursor="hand2",
            command=copy_drikon_id,
            padx=20,
            pady=5
        )
        drikon_btn.pack(pady=(2, 10))
        
        # تنويه مهم
        warning_frame = tk.Frame(
            main_frame,
            bg="#fef3c7",  # Light yellow
            relief="solid",
            bd=1
        )
        warning_frame.pack(fill="x", pady=(0, 15))
        
        warning_label = tk.Label(
            warning_frame,
            text="⚠️ تذكير: يجب اختيار اللغة الكورية من لانشر بارادوكس",
            font=("Segoe UI", 10, "bold"),
            bg="#fef3c7",
            fg="#92400e",  # Dark yellow
            pady=10
        )
        warning_label.pack()
        
        # زر الإغلاق
        close_btn = tk.Button(
            main_frame,
            text="✅ Close",
            bg=self.colors['primary'],
            fg="white",
            relief="flat",
            bd=0,
            font=("Segoe UI", 11, "bold"),
            padx=30,
            pady=10,
            command=about_window.destroy,
            cursor="hand2"
        )
        close_btn.pack(pady=(0, 20))
        
        # ربط عجلة الفأرة بالتمرير
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        # ربط الأحداث
        about_window.bind_all("<MouseWheel>", _on_mousewheel)
        
        # تحديث حجم التمرير
        about_window.update_idletasks()
        canvas.configure(scrollregion=canvas.bbox("all"))
    
    def _validate_paths(self) -> bool:
        """التحقق من صحة المسارات"""
        if not self.patch_data_path.exists():
            messagebox.showerror("Error", "Patch files folder not found!")
            return False
        
        if not self.stellaris_path or not self.stellaris_path.exists():
            messagebox.showerror("Error", "Stellaris folder not selected or not found!")
            return False
        
        return True
    
    def _collect_backup_files(self) -> List[Tuple[Path, str]]:
        """جمع الملفات للنسخ الاحتياطي"""
        files_to_backup = []
        
        # البحث في جميع ملفات Patch Data
        for patch_file in self.patch_data_path.rglob("*"):
            if patch_file.is_file():
                relative_path = patch_file.relative_to(self.patch_data_path)
                
                # تحديد المسار المقابل في Stellaris
                if str(relative_path).startswith("localisation/korean/"):
                    # تحويل korean إلى english للبحث
                    stellaris_path = str(relative_path).replace("localisation/korean/", "localisation/english/")
                else:
                    stellaris_path = str(relative_path)
                
                stellaris_file = self.stellaris_path / stellaris_path
                
                # إضافة للقائمة إذا كان الملف موجود في Stellaris
                if stellaris_file.exists():
                    files_to_backup.append((stellaris_file, stellaris_path))
        
        return files_to_backup
    
    def _get_next_backup_version(self) -> int:
        """الحصول على رقم الإصدار التالي للنسخة الاحتياطية"""
        if not self.backup_data_path.exists():
            return 1
        
        versions = []
        for backup_dir in self.backup_data_path.iterdir():
            if backup_dir.is_dir() and "Backup v" in backup_dir.name:
                try:
                    version_str = backup_dir.name.split("v")[1].split(" ")[0]
                    versions.append(int(version_str))
                except:
                    continue
        
        return max(versions) + 1 if versions else 1
    
    def _create_auto_backup(self) -> bool:
        """إنشاء نسخة احتياطية تلقائية"""
        try:
            now = datetime.now()
            version = self._get_next_backup_version()
            backup_name = f"Auto Backup v{version} {now.strftime('%H-%M %d-%m-%Y')}"
            backup_dir = self.backup_data_path / backup_name
            
            backup_dir.mkdir(parents=True, exist_ok=True)
            
            files_to_backup = self._collect_backup_files()
            
            copied_files = []
            for source_file, relative_path in files_to_backup:
                try:
                    dest_file = backup_dir / relative_path
                    dest_file.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(source_file, dest_file)
                    copied_files.append(relative_path)
                except Exception as e:
                    print(f"Error in auto backup {source_file}: {e}")
            
            # حفظ معلومات النسخة الاحتياطية
            backup_info = {
                "name": backup_name,
                "version": version,
                "created_at": now.isoformat(),
                "stellaris_path": str(self.stellaris_path),
                "files_count": len(copied_files),
                "files": copied_files,
                "auto_backup": True
            }
            
            with open(backup_dir / "backup_info.json", "w", encoding="utf-8") as f:
                json.dump(backup_info, f, indent=2, ensure_ascii=False)
            
            return True
        
        except Exception as e:
            print(f"Auto backup error: {e}")
            return False
    
    def _start_background_music(self):
        """تشغيل الموسيقى في الخلفية"""
        try:
            if self.music_file and self.music_file.exists():
                pygame.mixer.music.load(str(self.music_file))
                pygame.mixer.music.set_volume(0.3)  # صوت منخفض
                pygame.mixer.music.play(-1)  # تكرار لانهائي
                self.music_playing = True
                self.music_muted = False
                self._update_music_button()
                print(f"Music started: {self.music_file}")
            else:
                # إنشاء ملف موسيقى صامت إذا لم يوجد
                print("No music file found - running without music")
                self.music_playing = False
                self._update_music_button()
        except Exception as e:
            print(f"Error starting music: {e}")
            self.music_playing = False
            self._update_music_button()
    
    def _toggle_music(self):
        """تبديل كتم الموسيقى"""
        try:
            if not self.music_file:
                # لا يوجد ملف موسيقى - عرض رسالة
                messagebox.showinfo(
                    "No Music File", 
                    "No music file found!\n\n"
                    "Supported formats: MP3, WAV, OGG\n"
                    "Place a file named 'music.mp3' in the program folder."
                )
                return
                
            if self.music_playing:
                if self.music_muted:
                    # إلغاء الكتم
                    pygame.mixer.music.set_volume(0.3)
                    self.music_muted = False
                else:
                    # كتم الصوت
                    pygame.mixer.music.set_volume(0.0)
                    self.music_muted = True
                
                self._update_music_button()
        except Exception as e:
            print(f"Error toggling music: {e}")
    
    def _update_music_button(self):
        """تحديث أيقونة زر الموسيقى"""
        if not self.music_file:
            # لا يوجد ملف موسيقى
            self.music_btn.config(text="🎼", bg=self.colors['background'], fg=self.colors['text_secondary'])
        elif self.music_playing and not self.music_muted:
            # الموسيقى تعمل
            self.music_btn.config(text="🎵", bg=self.colors['background'], fg=self.colors['secondary'])
        else:
            # الموسيقى مكتومة أو متوقفة
            self.music_btn.config(text="🔇", bg=self.colors['background'], fg=self.colors['text_secondary'])

    def run(self):
        """تشغيل التطبيق"""
        # تحديث الحالة الأولية
        self._update_status()
        
        # إعداد شريط التقدم بعد عرض النافذة
        self.root.after(100, self._setup_progress_bar)
        
        # تشغيل الحلقة الرئيسية
        self.root.mainloop()
    
    def _setup_progress_bar(self):
        """إعداد شريط التقدم بعد عرض النافذة"""
        self.progress_bg.update_idletasks()


def main():
    """نقطة الدخول الرئيسية"""
    app = ModernStellarPatch()
    app.run()


if __name__ == "__main__":
    main()