#!/usr/bin/env python3
import os
import sys
import math
import shutil
import requests
from PySide6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QPushButton, QLabel, QLineEdit, QSizePolicy, QStackedWidget, QFrame, QStyle)
from PySide6.QtGui import QIcon, QFont, QFontDatabase
from PySide6.QtCore import Qt, QSettings, QSize

# Helper for bundled resources (PyInstaller)
def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath(os.path.dirname(__file__)), relative_path)

UPDATE_VERSION_URL = "https://gist.githubusercontent.com/Chill-Astro/738d8c4978d0a71a028235c375a30d1f/raw/cc42d26ad09a37c594401d82fcbb8d2fa97f67ef/PyC_GUI_V.txt"  # Gist URL

class Calculator(QWidget):
    def initAboutUI(self, use_icomoon, icomoon_font):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(16)
        layout.setContentsMargins(32, 32, 32, 32)
        layout.setAlignment(Qt.AlignCenter)
        # App icon
        icon_label = QLabel()
        icon_path = resource_path("PyCalc-GUI.ico")
        if os.path.exists(icon_path):
            icon_label.setPixmap(QIcon(icon_path).pixmap(128, 128))
        icon_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(icon_label, alignment=Qt.AlignCenter)
        # App name
        name_label = QLabel(f"<b>PyCalc - GUI v{self.CURRENT_VERSION}</b>")
        name_label.setAlignment(Qt.AlignCenter)
        name_label.setStyleSheet("font-size: 22px; margin-top: 8px;")
        layout.addWidget(name_label, alignment=Qt.AlignCenter)\
        # Quote
        version_label = QLabel("<i>\"Lamina</i>" + " ✦ " + "<i>for every System!\"</i>")
        version_label.setAlignment(Qt.AlignCenter)
        version_label.setStyleSheet("font-size: 15px; color: #888;")
        layout.addWidget(version_label, alignment=Qt.AlignCenter)
        # Author
        author_label = QLabel("Developer : Chill-Astro Software")
        author_label.setAlignment(Qt.AlignCenter)
        author_label.setStyleSheet("font-size: 15px; color: #888;")
        layout.addWidget(author_label, alignment=Qt.AlignCenter)
        # Check for updates button
        update_btn = QPushButton("Check for updates")
        update_btn.setFixedHeight(36)
        update_btn.setFixedWidth(180)
        update_btn.setProperty('eq', True)
        update_btn.setStyleSheet("font-size: 15px;")
        update_btn.clicked.connect(self.check_for_updates_about)
        layout.addWidget(update_btn, alignment=Qt.AlignCenter)
        # Update status (now below the button)
        self.about_update_status = QLabel("")
        self.about_update_status.setAlignment(Qt.AlignCenter)
        self.about_update_status.setStyleSheet("font-size: 15px; margin-top: 8px;")
        layout.addWidget(self.about_update_status, alignment=Qt.AlignCenter)
        return widget
    
    def __init__(self):
        super().__init__()
        self.CURRENT_VERSION = "1.3" # About Section + Bug Fixes
        self.setWindowTitle("PyCalc - GUI")
        self.setMinimumSize(430, 540)
        # Set window icon using resource_path (bundled with exe)
        icon_path = resource_path("PyCalc-GUI.ico")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        # ...existing code...
        # Restore window geometry
        self.settings = QSettings("ChillAstro", "PyCalc-GUI")
        geometry = self.settings.value("geometry")
        if geometry:
            self.restoreGeometry(geometry)
        self.initSidebarUI()  # <-- new sidebar UI
        self.apply_theme()
        self.reset()
        # --- Theme polling for runtime changes ---
        from PySide6.QtCore import QTimer, Qt
        self._last_theme = self._detect_os_theme()
        self._theme_timer = QTimer(self)
        self._theme_timer.setTimerType(Qt.CoarseTimer)  # Use enum for less CPU
        self._theme_timer.timeout.connect(self._check_theme_change)
        self._theme_timer.start(1000)  # check every 1s

    def closeEvent(self, event):
        # Save window geometry
        self.settings.setValue("geometry", self.saveGeometry())
        super().closeEvent(event)

    def _detect_os_theme(self):
        # Returns 'dark' or 'light'. Enhanced for KDE (KWin) and GNOME on Wayland.
        try:
            if sys.platform == 'win32':
                import winreg
                with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\\Microsoft\\Windows\\CurrentVersion\\Themes\\Personalize") as key:
                    value, _ = winreg.QueryValueEx(key, "AppsUseLightTheme")
                    return 'dark' if value == 0 else 'light'
            elif sys.platform == 'darwin':
                import subprocess
                result = subprocess.run([
                    'defaults', 'read', '-g', 'AppleInterfaceStyle'
                ], capture_output=True, text=True)
                return 'dark' if 'Dark' in result.stdout else 'light'
            elif sys.platform.startswith('linux'):
                import shutil
                import subprocess
                # Wayland only: check XDG_SESSION_TYPE
                if os.environ.get('XDG_SESSION_TYPE', '').lower() == 'wayland':
                    desktop = os.environ.get('XDG_CURRENT_DESKTOP', '').lower()
                    # GNOME Wayland
                    if 'gnome' in desktop:
                        try:
                            # GNOME 42+ uses color-scheme, fallback to gtk-theme
                            result = subprocess.run([
                                'gsettings', 'get', 'org.gnome.desktop.interface', 'color-scheme'
                            ], capture_output=True, text=True)
                            if 'dark' in result.stdout.lower():
                                return 'dark'
                            elif 'light' in result.stdout.lower():
                                return 'light'
                        except Exception:
                            pass
                        # Fallback: check gtk-theme
                        try:
                            result = subprocess.run([
                                'gsettings', 'get', 'org.gnome.desktop.interface', 'gtk-theme'
                            ], capture_output=True, text=True)
                            if 'dark' in result.stdout.lower():
                                return 'dark'
                        except Exception:
                            pass
                    # KDE (KWin) Wayland
                    elif 'kde' in desktop or 'plasma' in desktop:
                        # KDE Plasma 5.24+ uses color-scheme
                        try:
                            result = subprocess.run([
                                'qdbus', 'org.kde.KWin', '/KWin', 'org.kde.KWin.supportInformation'
                            ], capture_output=True, text=True)
                            # Not strictly needed, but confirms KWin is running
                        except Exception:
                            pass
                        # Try reading kdeglobals config for color scheme
                        kdeglobals_path = os.path.expanduser('~/.config/kdeglobals')
                        if os.path.exists(kdeglobals_path):
                            try:
                                with open(kdeglobals_path, 'r', encoding='utf-8') as f:
                                    for line in f:
                                        if line.strip().startswith('ColorScheme='):  # KDE6
                                            scheme = line.strip().split('=', 1)[-1].lower()
                                            if 'dark' in scheme:
                                                return 'dark'
                                            elif 'light' in scheme:
                                                return 'light'
                                        elif line.strip().startswith('name='):  # KDE5
                                            scheme = line.strip().split('=', 1)[-1].lower()
                                            if 'dark' in scheme:
                                                return 'dark'
                                            elif 'light' in scheme:
                                                return 'light'
                            except Exception:
                                pass
                        # Fallback: check KDE_COLOR_SCHEME env
                        kde_scheme = os.environ.get('KDE_COLOR_SCHEME', '').lower()
                        if 'dark' in kde_scheme:
                            return 'dark'
                        elif 'light' in kde_scheme:
                            return 'light'
                    # Fallback for other desktops on Wayland
                    gtk_theme = os.environ.get('GTK_THEME', '').lower()
                    if 'dark' in gtk_theme:
                        return 'dark'
                    elif 'light' in gtk_theme:
                        return 'light'
                # Try darkman if available (works for both X11/Wayland)
                if shutil.which('darkman'):
                    try:
                        result = subprocess.run(['darkman', 'get'], capture_output=True, text=True)
                        if 'dark' in result.stdout.lower():
                            return 'dark'
                        elif 'light' in result.stdout.lower():
                            return 'light'
                    except Exception:
                        pass
                # Fallback: try GTK_THEME or KDE_COLOR_SCHEME
                gtk_theme = os.environ.get('GTK_THEME', '').lower()
                if 'dark' in gtk_theme:
                    return 'dark'
                elif 'light' in gtk_theme:
                    return 'light'
                kde_scheme = os.environ.get('KDE_COLOR_SCHEME', '').lower()
                if 'dark' in kde_scheme:
                    return 'dark'
                elif 'light' in kde_scheme:
                    return 'light'
                # Fallback: try XDG_CURRENT_DESKTOP for GNOME/KDE
                desktop = os.environ.get('XDG_CURRENT_DESKTOP', '').lower()
                if 'gnome' in desktop or 'kde' in desktop:
                    # Try to read gsettings (GNOME)
                    try:
                        result = subprocess.run([
                            'gsettings', 'get', 'org.gnome.desktop.interface', 'color-scheme'
                        ], capture_output=True, text=True)
                        if 'dark' in result.stdout.lower():
                            return 'dark'
                        elif 'light' in result.stdout.lower():
                            return 'light'
                    except Exception:
                        pass
                # Default to dark
                return 'dark'
        except Exception:
            return 'dark'
        return 'dark'

    def _check_theme_change(self):
        current_theme = self._detect_os_theme()
        if current_theme != self._last_theme:
            self._last_theme = current_theme
            self.refresh_theme()

    def apply_theme(self):
        is_dark = self._detect_os_theme() == 'dark'
        if is_dark:
            self.setStyleSheet(self.dark_stylesheet())
            self._current_theme = 'dark'
        else:
            self.setStyleSheet(self.light_stylesheet())
            self._current_theme = 'light'
        self.update_label_styles()

    def refresh_theme(self):
        self.apply_theme()

    def update_label_styles(self):
        # Remove inline color styles so stylesheet takes effect
        self.display.setStyleSheet("font-size: 30px; font-weight: bold; padding-right: 0.5px;")
        self.history.setStyleSheet("font-size: 12px; padding-top: 20px;")

    def dark_stylesheet(self):
        return """
            QWidget { background: #23272e; }
            QLabel { color: #e6e6e6; }
            QLabel#display { color: #e6e6e6; }
            QLabel#history { color: #888; }
            QPushButton {
                background: #31343b; color: #e6e6e6; border: none; border-radius: 5px;
                font-size: 15px; padding: 8px;
            }
            QPushButton:pressed { background: #3a3d44; }
            QPushButton[op="true"] { background: #3b4252; color: #e6e6e6; }
            QPushButton[op="true"]:pressed { background: #434c5e; }
            QPushButton[fn="true"] { background: #2e3440; color: #bfc7d5; }
            QPushButton[fn="true"]:pressed { background: #3b4252; }
            QPushButton[eq="true"] { background: #5e81ac; color: #fff; }
            QPushButton[eq="true"]:pressed { background: #4c669f; }
        """

    def light_stylesheet(self):        
        return """
            QWidget { background: #f7fafd; }
            QLabel { color: #23272e; }
            QLabel#display { color: #23272e; }
            QLabel#history { color: #7b8794; }
            QPushButton {
                background: #f0f4fa; color: #23272e; border: none; border-radius: 5px;
                font-size: 15px; padding: 8px;
                transition: background 0.2s;
            }
            QPushButton:pressed { background: #e0e7ef; }
            QPushButton[op="true"] {
                background: #e3e8f0; color: #23272e;
            }
            QPushButton[op="true"]:pressed {
                background: #bae6fd;
            }
            QPushButton[fn="true"] {
                background: #e0e7ef; color: #4b5563;
            }
            QPushButton[fn="true"]:pressed {
                background: #cbd5e1;
            }
            QPushButton[eq="true"] {
                background: #e0f2fe; color: #23272e;
            }
            QPushButton[eq="true"]:pressed {
                background: #bae6fd;
            }
        """

    def initSidebarUI(self):
        # Main layout with sidebar
        main_layout = QHBoxLayout(self)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)
        # Sidebar
        sidebar = QFrame()
        sidebar.setFixedWidth(52)  # Shrink sidebar for icons
        sidebar.setFrameShape(QFrame.StyledPanel)
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setSpacing(4)
        sidebar_layout.setContentsMargins(2, 8, 2, 8)
        # Sidebar buttons (icon only)
        self.sidebar_buttons = []
        # Try to load icomoon.ttf (bundled)
        icomoon_font_id = QFontDatabase.addApplicationFont(resource_path("icomoon.ttf"))
        icomoon_families = QFontDatabase.applicationFontFamilies(icomoon_font_id)
        use_icomoon = bool(icomoon_families)
        from PySide6.QtWidgets import QStyle
        if use_icomoon:
            icomoon_font = QFont(icomoon_families[0], 14)
            icon_codes = [
                '\ue900',  # Calculator
                '\ue901',  # Heron's Formula
                '\ue902',  # Simple Interest
                '\ue903',  # Compound Interest
                '\ue919',  # Quadratic Equation                
                '\ue915',  # Discount Price
                '🛈', # About 
            ]
        else:
            icomoon_font = None
            icon_codes = [
                'C', '△', 'SI', 'CI', 'QE', '%', '🛈'
            ]
        sidebar_btn_data = [
            ("Calculator", icon_codes[0]),
            ("Heron's Formula", icon_codes[1]),
            ("Simple Interest", icon_codes[2]),
            ("Compound Interest", icon_codes[3]),
            ("Quadratic Equation", icon_codes[4]),
            ("Discount Price", icon_codes[5]),            
            ("About", icon_codes[6]),
        ]
        for idx, (tooltip, icon_text) in enumerate(sidebar_btn_data):
            if idx == 7:
                # About/info button uses Unicode ⓘ
                btn = QPushButton('🛈')
                btn.setToolTip(tooltip)
                btn.setFixedHeight(40)
                btn.setFixedWidth(42)
                btn.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
                btn.setProperty('fn', True)
                btn.setStyleSheet("font-size: 18px; font-weight: bold; background: none; border: none;")
            else:
                btn = QPushButton(icon_text)
                btn.setToolTip(tooltip)
                btn.setFixedHeight(40)
                btn.setFixedWidth(42)
                btn.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
                btn.setProperty('fn', True)
                btn.setStyleSheet("font-size: 10px; font-weight: bold;")
                if use_icomoon and idx in (8, 9):
                    btn.setFont(icomoon_font)
            btn.clicked.connect(lambda _, i=idx: self.switch_calculator(i))
            sidebar_layout.addWidget(btn, alignment=Qt.AlignHCenter)
            self.sidebar_buttons.append(btn)
        sidebar_layout.addStretch(1)
        main_layout.addWidget(sidebar)
        # Stacked widget for calculators
        self.stack = QStackedWidget()
        # Add all calculator widgets
        self.stack.addWidget(self.initCalculatorUI())
        self.stack.addWidget(self.initHeronUI())
        self.stack.addWidget(self.initSimpleInterestUI())
        self.stack.addWidget(self.initCompoundInterestUI())
        self.stack.addWidget(self.initQuadraticUI())
        self.stack.addWidget(self.initDiscountUI())
        self.stack.addWidget(self.initAboutUI(use_icomoon, icomoon_font))
        main_layout.addWidget(self.stack)
        self.setLayout(main_layout)
        self.switch_calculator(0)

    def check_for_updates_about(self):
        from PySide6.QtCore import QThread, Signal

        class UpdateCheckThread(QThread):
            update_message = Signal(str)
            def __init__(self, parent=None, current_version=None):
                super().__init__(parent)
                self.parent = parent
                self.current_version = current_version
            def run(self):
                try:
                    response = requests.get(UPDATE_VERSION_URL, timeout=5)
                    response.raise_for_status()
                    latest_version = response.text.strip()
                    if latest_version > self.current_version:
                        msg = f"🎉 PyCalc-GUI v{latest_version} is OUT NOW!"
                    elif latest_version == self.current_version:
                        msg = "🎉 PyCalc-GUI is up to date!"
                    elif latest_version < self.current_version:
                        msg = "⚠️ WARNING! THIS IS NOT A PUBLIC RELEASE!"
                    else:
                        msg = "🎉 PyCalc-GUI is up to date!"
                except Exception:
                    msg = "⚠️ Please check your Internet Connection."
                self.update_message.emit(msg)

        self.update_thread = UpdateCheckThread(self, self.CURRENT_VERSION)
        self.update_thread.update_message.connect(self.show_about_update_message)
        self.update_thread.start()

    def show_about_update_message(self, msg):
        self.about_update_status.setText(msg)
        self.about_update_status.setStyleSheet("font-size: 15px; margin-top: 8px;")

    def switch_calculator(self, idx):
        self.stack.setCurrentIndex(idx)
        for i, btn in enumerate(self.sidebar_buttons):
            btn.setProperty('active', i == idx)
            btn.setStyleSheet(self.button_style(i == idx))

    def button_style(self, active):
        if self._detect_os_theme() == 'dark':
            if active:
                return "background: #5e81ac; color: #fff; border-radius: 5px; font-size: 18px; font-weight: bold;"
            else:
                return "background: #2e3440; color: #bfc7d5; border-radius: 5px; font-size: 18px;"
        else:
            if active:
                return "background: #2563eb; color: #fff; border-radius: 5px; font-size: 18px; font-weight: bold;"
            else:
                return "background: #e0e7ef; color: #4b5563; border-radius: 5px; font-size: 18px;"

    def initCalculatorUI(self):
        widget = QWidget()
        vbox = QVBoxLayout(widget)
        vbox.setSpacing(10)
        vbox.setContentsMargins(8, 8, 8, 8)
        self.history = QLabel("")
        self.history.setObjectName("history")
        self.history.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.history.setStyleSheet("font-size: 12px; padding-top: 20px;")
        # ...existing code...
        vbox.addWidget(self.history)
        self.display = QLabel("0")
        self.display.setObjectName("display")
        self.display.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.display.setMinimumHeight(75)
        self.display.setStyleSheet("font-size: 30px; font-weight: bold; padding-right: 0.5px;")
        # ...existing code...
        vbox.addWidget(self.display)
        grid = QGridLayout()
        grid.setSpacing(6)
        vbox.addLayout(grid)
        buttons = [
            [('xʸ', 'fn'), ('CE', 'fn'), ('C', 'fn'), ('⌫', 'fn')],
            [('x²', 'fn'), ('∛x', 'fn'), ('√x', 'fn'), ('÷', 'op')],
            [('7', ''), ('8', ''), ('9', ''), ('×', 'op')],
            [('4', ''), ('5', ''), ('6', ''), ('-', 'op')],
            [('1', ''), ('2', ''), ('3', ''), ('+', 'op')],
            [('+/-', 'fn'), ('0', ''), ('.', ''), ('=', 'eq')],
        ]
        self.button_map = {}
        for i, row in enumerate(buttons):
            for j, (text, role) in enumerate(row):
                btn = QPushButton(text)
                btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
                # ...existing code...
                if role == 'op':
                    btn.setProperty('op', True)
                elif role == 'eq':
                    btn.setProperty('eq', True)
                elif role == 'fn':
                    btn.setProperty('fn', True)
                btn.clicked.connect(lambda _, t=text: self.on_button(t))
                grid.addWidget(btn, i, j)
                self.button_map[text] = btn
        return widget

    def initHeronUI(self):
        widget = QWidget()
        outer = QVBoxLayout(widget)
        outer.setAlignment(Qt.AlignCenter)
        inner = QVBoxLayout()
        inner.setSpacing(12)
        inner.setContentsMargins(24, 24, 24, 24)
        inner.setAlignment(Qt.AlignCenter)
        self.heron_inputs = [QLineEdit() for _ in range(3)]
        labels = ["First Side [a] :", "Second Side [b] :", "Third Side [c] :"]
        for i, label in enumerate(labels):
            lbl = QLabel(f"<b>{label}</b>")
            lbl.setAlignment(Qt.AlignCenter)
            lbl.setStyleSheet("font-size: 16px;")
            inner.addWidget(lbl, alignment=Qt.AlignCenter)
            self.heron_inputs[i].setPlaceholderText("")
            self.heron_inputs[i].setFixedWidth(180)
            self.heron_inputs[i].setFixedHeight(32)
            self.heron_inputs[i].setStyleSheet("font-size: 15px;")
            inner.addWidget(self.heron_inputs[i], alignment=Qt.AlignCenter)
        btn = QPushButton("Calculate")
        btn.setFixedHeight(36)
        btn.setFixedWidth(120)
        btn.setProperty('eq', True)
        btn.setStyleSheet("font-size: 15px;")
        btn.clicked.connect(self.calculate_heron)
        inner.addWidget(btn, alignment=Qt.AlignCenter)
        self.heron_output = QLabel("OUTPUT AREA")
        self.heron_output.setAlignment(Qt.AlignCenter)
        self.heron_output.setFixedHeight(28)
        self.heron_output.setStyleSheet("font-size: 15px;")
        inner.addWidget(self.heron_output, alignment=Qt.AlignCenter)
        outer.addLayout(inner)
        return widget

    def initSimpleInterestUI(self):
        widget = QWidget()
        widget.setMinimumWidth(340)
        widget.setMinimumHeight(420)
        layout = QVBoxLayout(widget)
        layout.setSpacing(12)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setAlignment(Qt.AlignCenter)
        self.si_inputs = [QLineEdit() for _ in range(3)]
        labels = ["Principal:", "Rate [%]:", "Time [Years]:"]
        for i, label in enumerate(labels):
            lbl = QLabel(f"<b>{label}</b>")
            lbl.setAlignment(Qt.AlignCenter)
            lbl.setStyleSheet("font-size: 16px;")
            layout.addWidget(lbl, alignment=Qt.AlignCenter)
            self.si_inputs[i].setPlaceholderText("")
            self.si_inputs[i].setFixedWidth(180)
            self.si_inputs[i].setFixedHeight(32)
            self.si_inputs[i].setStyleSheet("font-size: 15px;")
            layout.addWidget(self.si_inputs[i], alignment=Qt.AlignCenter)
        btn = QPushButton("Calculate")
        btn.setFixedHeight(36)
        btn.setFixedWidth(120)
        btn.setProperty('eq', True)
        btn.setStyleSheet("font-size: 15px;")
        btn.clicked.connect(self.calculate_simple_interest)
        layout.addWidget(btn, alignment=Qt.AlignCenter)
        self.si_output = QLabel("OUTPUT AREA")
        self.si_output.setAlignment(Qt.AlignCenter)
        self.si_output.setFixedHeight(28)
        self.si_output.setStyleSheet("font-size: 15px;")
        layout.addWidget(self.si_output, alignment=Qt.AlignCenter)
        return widget

    def initCompoundInterestUI(self):
        widget = QWidget()
        widget.setMinimumWidth(340)
        widget.setMinimumHeight(420)
        layout = QVBoxLayout(widget)
        layout.setSpacing(12)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setAlignment(Qt.AlignCenter)
        self.ci_inputs = [QLineEdit() for _ in range(4)]
        labels = ["Principal :", "Rate [%] :", "Time [Years]:", "Compounding Frequency [n] :"]
        for i, label in enumerate(labels):
            lbl = QLabel(f"<b>{label}</b>")
            lbl.setAlignment(Qt.AlignCenter)
            lbl.setStyleSheet("font-size: 16px;")
            layout.addWidget(lbl, alignment=Qt.AlignCenter)
            self.ci_inputs[i].setPlaceholderText("")
            self.ci_inputs[i].setFixedWidth(180)
            self.ci_inputs[i].setFixedHeight(32)
            self.ci_inputs[i].setStyleSheet("font-size: 15px;")
            layout.addWidget(self.ci_inputs[i], alignment=Qt.AlignCenter)
        btn = QPushButton("Calculate")
        btn.setFixedHeight(36)
        btn.setFixedWidth(120)
        btn.setProperty('eq', True)
        btn.setStyleSheet("font-size: 15px;")
        btn.clicked.connect(self.calculate_compound_interest)
        layout.addWidget(btn, alignment=Qt.AlignCenter)
        self.ci_output = QLabel("OUTPUT AREA")
        self.ci_output.setAlignment(Qt.AlignCenter)
        self.ci_output.setFixedHeight(28)
        self.ci_output.setStyleSheet("font-size: 15px;")
        layout.addWidget(self.ci_output, alignment=Qt.AlignCenter)        
        return widget

    def initQuadraticUI(self):
        widget = QWidget()
        widget.setMinimumWidth(340)
        widget.setMinimumHeight(420)
        layout = QVBoxLayout(widget)
        layout.setSpacing(12)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setAlignment(Qt.AlignCenter)
        self.q_inputs = [QLineEdit() for _ in range(3)]
        labels = ["First Coeffecient [a] :", "Second Coeffecient [b] :", "Third Coeffecient [c] :"]
        for i, label in enumerate(labels):
            lbl = QLabel(f"<b>{label}</b>")
            lbl.setAlignment(Qt.AlignCenter)
            lbl.setStyleSheet("font-size: 16px;")
            layout.addWidget(lbl, alignment=Qt.AlignCenter)
            self.q_inputs[i].setPlaceholderText("")
            self.q_inputs[i].setFixedWidth(180)
            self.q_inputs[i].setFixedHeight(32)
            self.q_inputs[i].setStyleSheet("font-size: 15px;")
            layout.addWidget(self.q_inputs[i], alignment=Qt.AlignCenter)
        btn = QPushButton("Calculate")
        btn.setFixedHeight(36)
        btn.setFixedWidth(120)
        btn.setProperty('eq', True)
        btn.setStyleSheet("font-size: 15px;")
        btn.clicked.connect(self.calculate_quadratic)
        layout.addWidget(btn, alignment=Qt.AlignCenter)
        self.q_output = QLabel("OUTPUT AREA")
        self.q_output.setAlignment(Qt.AlignCenter)
        self.q_output.setFixedHeight(28)
        self.q_output.setStyleSheet("font-size: 15px;")
        layout.addWidget(self.q_output, alignment=Qt.AlignCenter)
        return widget

    def initDiscountUI(self):
        widget = QWidget()
        widget.setMinimumWidth(340)
        widget.setMinimumHeight(260)
        layout = QVBoxLayout(widget)
        layout.setSpacing(12)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setAlignment(Qt.AlignCenter)
        self.discount_inputs = [QLineEdit() for _ in range(2)]
        labels = ["Enter Original Price :", "Enter Discount [%] :"]
        for i, label in enumerate(labels):
            lbl = QLabel(f"<b>{label}</b>")
            lbl.setAlignment(Qt.AlignCenter)
            lbl.setStyleSheet("font-size: 16px;")
            layout.addWidget(lbl, alignment=Qt.AlignCenter)
            self.discount_inputs[i].setPlaceholderText("")
            self.discount_inputs[i].setFixedWidth(180)
            self.discount_inputs[i].setFixedHeight(32)
            self.discount_inputs[i].setStyleSheet("font-size: 15px;")
            layout.addWidget(self.discount_inputs[i], alignment=Qt.AlignCenter)
        btn = QPushButton("Calculate")
        btn.setFixedHeight(36)
        btn.setFixedWidth(120)
        btn.setProperty('eq', True)
        btn.setStyleSheet("font-size: 15px;")
        btn.clicked.connect(self.calculate_discount)
        layout.addWidget(btn, alignment=Qt.AlignCenter)
        self.discount_output = QLabel("DISCOUNT OUTPUT\nFINAL PRICE")
        self.discount_output.setAlignment(Qt.AlignCenter)
        self.discount_output.setFixedHeight(35)
        self.discount_output.setStyleSheet("font-size: 15px;")
        layout.addWidget(self.discount_output, alignment=Qt.AlignCenter)
        return widget

    def calculate_heron(self):
        try:
            a = float(self.heron_inputs[0].text())
            b = float(self.heron_inputs[1].text())
            c = float(self.heron_inputs[2].text())
            s = (a + b + c) / 2
            area = math.sqrt(s * (s - a) * (s - b) * (s - c))
            self.heron_output.setText(f"Area: {area:.4f}")
        except Exception:
            self.heron_output.setText("Invalid input.")

    def calculate_simple_interest(self):
        try:
            p = float(self.si_inputs[0].text())
            r = float(self.si_inputs[1].text())
            t = float(self.si_inputs[2].text())
            si = (p * r * t) / 100
            self.si_output.setText(f"Simple Interest: {si:.2f}")
        except Exception:
            self.si_output.setText("Invalid input.")

    def calculate_compound_interest(self):
        try:
            p = float(self.ci_inputs[0].text())
            r = float(self.ci_inputs[1].text()) / 100
            t = float(self.ci_inputs[2].text())
            n = float(self.ci_inputs[3].text())
            amount = p * (1 + r / n) ** (n * t)
            ci = amount - p
            self.ci_output.setText(f"Compound Interest: {ci:.2f}\nTotal: {amount:.2f}")
        except Exception:
            self.ci_output.setText("Invalid input.")

    def calculate_quadratic(self):
        try:
            a = float(self.q_inputs[0].text())
            b = float(self.q_inputs[1].text())
            c = float(self.q_inputs[2].text())
            d = b ** 2 - 4 * a * c
            if d < 0:
                self.q_output.setText("No real roots.")
            elif d == 0:
                x = -b / (2 * a)
                self.q_output.setText(f"One root: {x:.4f}")
            else:
                x1 = (-b + math.sqrt(d)) / (2 * a)
                x2 = (-b - math.sqrt(d)) / (2 * a)
                self.q_output.setText(f"Roots: {x1:.4f}, {x2:.4f}")
        except Exception:
            self.q_output.setText("Invalid input.")

    def calculate_discount(self):
        try:
            price = float(self.discount_inputs[0].text())
            discount = float(self.discount_inputs[1].text())
            disc_amt = price * discount / 100
            final = price - disc_amt
            self.discount_output.setText(f"Discount: {disc_amt:.2f}\nFinal Price: {final:.2f}")
        except Exception:
            self.discount_output.setText("Invalid input.")

    def reset(self):
        self.expression_history = ""
        self.current_input = "0"
        self.full_expression = ""
        self.result_pending = False
        self._currentNumber = 0.0
        self._previousNumber = 0.0
        self._currentOperator = ""
        self._isNewNumberInput = True
        self._hasDecimal = False
        self.update_display()

    def update_display(self):
        if isinstance(self._currentNumber, float):
            if self._currentNumber.is_integer() and not self._hasDecimal:
                display_value = str(int(self._currentNumber))
            else:
                display_value = str(self._currentNumber)
        else:
            display_value = str(self._currentNumber)
        self.display.setText(display_value)
        self.history.setText(self.expression_history)

    def clear_entry(self):
        self.current_input = "0"
        self._currentNumber = 0.0
        self._isNewNumberInput = True
        self._hasDecimal = False
        self.update_display()

    def backspace(self):
        if self.result_pending:
            return
        current_str = str(self._currentNumber)
        if '.' in current_str:
            parts = current_str.split('.')
            if len(parts[0]) > 1:
                new_str = parts[0][:-1] + ('.' + parts[1] if parts[1] else '')
            else:
                new_str = '0' + ('.' + parts[1] if parts[1] else '')
            try:
                self._currentNumber = float(new_str)
                self._hasDecimal = '.' in new_str
            except ValueError:
                self._currentNumber = 0.0
                self._hasDecimal = False
        else:
            if len(current_str) > 1:
                self._currentNumber = int(current_str[:-1])
            else:
                self._currentNumber = 0.0
            self._hasDecimal = False
        self._isNewNumberInput = False
        self.update_display()

    def input_digit(self, digit):
        if self.result_pending:
            self._currentNumber = int(digit)
            self.expression_history = ""
            self.full_expression = ""
            self.result_pending = False
            self._isNewNumberInput = False
            self._hasDecimal = False
        elif self._isNewNumberInput or self._currentNumber == 0:
            if self._hasDecimal:
                self._currentNumber = float(f"0.{digit}")
            else:
                self._currentNumber = int(digit)
            self._isNewNumberInput = False
        else:
            current_str = str(self._currentNumber)
            if self._hasDecimal:
                if '.' in current_str:
                    self._currentNumber = float(current_str + digit)
                else:
                    self._currentNumber = float(current_str + '.' + digit)
            else:
                self._currentNumber = float(current_str + digit) if '.' in current_str else int(current_str + digit)
        self.update_display()

    def input_decimal(self):
        if self.result_pending:
            self._currentNumber = 0.0
            self.expression_history = ""
            self.full_expression = ""
            self.result_pending = False
            self._isNewNumberInput = False
            self._hasDecimal = True
        if not self._hasDecimal:
            self._hasDecimal = True
            current_str = str(self._currentNumber)
            if '.' not in current_str:
                self._currentNumber = float(current_str + '.')
            self._isNewNumberInput = False
            self.update_display()

    def input_operator(self, op):
        if not self._currentNumber and op != '-':
            return
        if not self._isNewNumberInput:
            if self._currentOperator:
                self.calculate_intermediate_result()
            else:
                self._previousNumber = self._currentNumber
        visual_op = op.replace('**', '^').replace('*', '×').replace('/', '÷')
        self.expression_history = f"{self._previousNumber} {visual_op} "
        self._currentOperator = op
        self._isNewNumberInput = True
        self._hasDecimal = False
        self.update_display()

    def calculate_intermediate_result(self):
        if self._currentOperator:
            try:
                if self._currentOperator == '+':
                    result = self._previousNumber + self._currentNumber
                elif self._currentOperator == '-':
                    result = self._previousNumber - self._currentNumber
                elif self._currentOperator == '*':
                    result = self._previousNumber * self._currentNumber
                elif self._currentOperator == '/':
                    if self._currentNumber == 0:
                        self._currentNumber = "Error"
                        self.expression_history = ""
                        self._previousNumber = 0
                        self._currentOperator = ""
                        self._isNewNumberInput = True
                        self.result_pending = False
                        self._hasDecimal = False
                        self.update_display()
                        return
                    result = self._previousNumber / self._currentNumber
                if isinstance(result, float) and result.is_integer() and not self._hasDecimal:
                    self._currentNumber = int(result)
                else:
                    self._currentNumber = result
                self._previousNumber = self._currentNumber
                self._isNewNumberInput = True
                self._hasDecimal = False
                self.update_display()
            except Exception:
                self.handle_calculation_error()

    def calculate_result(self):
        if self.result_pending or not self._currentOperator:
            return
        second_number = self._currentNumber
        try:
            if self._currentOperator == '+':
                result = self._previousNumber + second_number
            elif self._currentOperator == '-':
                result = self._previousNumber - second_number
            elif self._currentOperator == '*':
                result = self._previousNumber * second_number
            elif self._currentOperator == '/':
                if second_number == 0:
                    self._currentNumber = "Error"
                    self.expression_history = ""
                    self._previousNumber = 0
                    self._currentOperator = ""
                    self._isNewNumberInput = True
                    self.result_pending = False
                    self._hasDecimal = False
                    self.update_display()
                    return
                result = self._previousNumber / second_number
            elif self._currentOperator == '**':
                result = self._previousNumber ** second_number
            if isinstance(result, float) and result.is_integer() and not self._hasDecimal:
                self._currentNumber = int(result)
            else:
                self._currentNumber = result
            self.expression_history = f"{self._previousNumber} {self.get_visual_operator(self._currentOperator)} {second_number} ="
            self.result_pending = True
            self._isNewNumberInput = True
            self._currentOperator = ""
            self._previousNumber = self._currentNumber
            self._hasDecimal = False
            self.update_display()
        except Exception:
            self.handle_calculation_error()

    def handle_calculation_error(self):
        self._currentNumber = "Error"
        self.expression_history = ""
        self._previousNumber = 0
        self._currentOperator = ""
        self._isNewNumberInput = True
        self.result_pending = False
        self._hasDecimal = False
        self.update_display()

    def get_visual_operator(self, op):
        return op.replace('**', '^').replace('*', '×').replace('/', '÷')

    def toggle_sign(self):
        try:
            self._currentNumber = -float(self._currentNumber)
            self.update_display()
        except Exception:
            self.handle_calculation_error()

    def calculate_square_root(self):
        try:
            num = float(self._currentNumber)
            if num < 0:
                self._currentNumber = "Error"
                self.expression_history = f"√({num})"
            else:
                result = math.sqrt(num)
                if result.is_integer() and not self._hasDecimal:
                    self._currentNumber = int(result)
                else:
                    self._currentNumber = result
                self.expression_history = f"√({num})"
            self.update_display()
        except (ValueError, TypeError):
            self.handle_calculation_error()

    def calculate_cube_root(self):
        try:
            num = float(self._currentNumber)
            # Cube root, handle negative numbers as real roots
            if num < 0:
                result = -(-num) ** (1/3)
            else:
                result = num ** (1/3)
            if isinstance(result, float) and result.is_integer() and not self._hasDecimal:
                self._currentNumber = int(result)
            else:
                self._currentNumber = result
            self.expression_history = f"∛({num})"
            self.update_display()
        except Exception:
            self.handle_calculation_error()

    def calculate_square(self):
        try:
            num = float(self._currentNumber)
            result = num ** 2
            if result.is_integer() and not self._hasDecimal:
                self._currentNumber = int(result)
            else:
                self._currentNumber = result
            self.expression_history = f"sqr({num})"
            self.update_display()
        except (ValueError, TypeError):
            self.handle_calculation_error()

    def on_button(self, text):
        if text in '0123456789':
            self.input_digit(text)
        elif text == '.':
            self.input_decimal()
        elif text in '+-×÷':
            # If '-' is pressed and we're starting a new number (after operator or at start), treat as negative sign
            if text == '-' and self._isNewNumberInput:
                if self._currentNumber == 0 and (not self._currentOperator or self.expression_history.endswith(('+', '-', '×', '÷', '^', '**'))):
                    self._currentNumber = 0.0
                    self._isNewNumberInput = False
                    self._hasDecimal = False
                    self.toggle_sign()
                    return
            op_map = {'+': '+', '-': '-', '×': '*', '÷': '/'}
            self.input_operator(op_map[text])
        elif text == '+/-':
            self.toggle_sign()
        elif text == 'x²':
            self.calculate_square()
        elif text == '∛x':
            self.calculate_cube_root()
        elif text == '√x':
            self.calculate_square_root()
        elif text == 'xʸ':
            self.input_operator('**')
        elif text == '=':
            self.calculate_result()
        elif text == 'C':
            self.reset()
        elif text == 'CE':
            self.clear_entry()
        elif text == '⌫':
            self.backspace()

    def keyPressEvent(self, event):
        key = event.key()
        text = event.text()
        # Numeric keys
        if text in '0123456789':
            self.on_button(text)
        # Operators
        elif text == '+':
            self.on_button('+')
        elif text == '-':
            self.on_button('-')
        elif text == '*':
            self.on_button('×')
        elif text == '/':
            self.on_button('÷')
        elif text == '.':
            self.on_button('.')
        elif text == '^':
            self.on_button('xʸ')
        elif text.lower() == 'c':
            self.on_button('C')
        elif text == '=' or key == Qt.Key_Enter or key == Qt.Key_Return:
            self.on_button('=')
        elif key == Qt.Key_Backspace:
            self.on_button('⌫')
        elif key == Qt.Key_Delete:
            self.on_button('CE')
        else:
            super().keyPressEvent(event)

    def show_update_message(self, msg):
        from PySide6.QtCore import QTimer
        def clear_message():
            if self.history.text() == msg:
                self.history.setText("")
                self.history.update()
        self.history.setText(msg)
        self.history.setStyleSheet("font-size: 12px; padding-top: 20px;")
        QTimer.singleShot(4000, clear_message)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    calc = Calculator()
    calc.show()
    sys.exit(app.exec())