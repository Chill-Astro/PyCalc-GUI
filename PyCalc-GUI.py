#!/usr/bin/env python3
import sys
import math
import os.path
import requests
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QPushButton, QLabel, QSizePolicy, QStackedWidget, QLineEdit, QFrame
)
from PySide6.QtCore import Qt, QSettings
from PySide6.QtGui import QIcon, QFontDatabase, QFont

# Helper for bundled resources (PyInstaller)
def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath(os.path.dirname(__file__)), relative_path)

UPDATE_VERSION_URL = "https://gist.githubusercontent.com/Chill-Astro/738d8c4978d0a71a028235c375a30d1f/raw/2e23a1b0ccb7bdbaa63c0dd128ddbfdb27ef814e/PyC_GUI_V.txt"  # Gist URL

class Calculator(QWidget):
    def __init__(self):
        super().__init__()
        self.CURRENT_VERSION = "1.2" # Self-Contained Update
        self.setWindowTitle("PyCalc - GUI")            
        self.setMinimumSize(400, 500)
        # Set window icon using resource_path (bundled with exe)
        icon_path = resource_path("PyCalc-GUI.ico")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        # Load custom font Inter.ttf (bundled)
        font_id = QFontDatabase.addApplicationFont(resource_path("Inter.ttf"))
        font_families = QFontDatabase.applicationFontFamilies(font_id)
        if font_families:
            custom_font = QFont(font_families[0], 14)
            QApplication.instance().setFont(custom_font)
            self.setFont(custom_font)
        # Restore window geometry
        self.settings = QSettings("ChillAstro", "PyCalc-GUI")
        geometry = self.settings.value("geometry")
        if geometry:
            self.restoreGeometry(geometry)
        self.initSidebarUI()  # <-- new sidebar UI
        self.apply_theme()
        self.reset()
        self.check_for_updates()
        # --- Theme polling for runtime changes ---
        from PySide6.QtCore import QTimer
        self._last_theme = self._detect_os_theme()
        self._theme_timer = QTimer(self)
        self._theme_timer.timeout.connect(self._check_theme_change)
        self._theme_timer.start(100)  # check every 0.1 seconds for more instant theme change

    def closeEvent(self, event):
        # Save window geometry
        self.settings.setValue("geometry", self.saveGeometry())
        super().closeEvent(event)

    def _detect_os_theme(self):
        # Returns 'dark' or 'light'
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
                # Try darkman if available
                import shutil
                if shutil.which('darkman'):
                    import subprocess
                    result = subprocess.run(['darkman', 'get'], capture_output=True, text=True)
                    return 'dark' if 'dark' in result.stdout.lower() else 'light'
                # Try GTK_THEME or XDG_CURRENT_DESKTOP heuristics
                gtk_theme = os.environ.get('GTK_THEME', '').lower()
                if 'dark' in gtk_theme:
                    return 'dark'
                # Try KDE color scheme
                kde_scheme = os.environ.get('KDE_COLOR_SCHEME', '').lower()
                if 'dark' in kde_scheme:
                    return 'dark'
                # Try XDG_CURRENT_DESKTOP for GNOME/KDE
                desktop = os.environ.get('XDG_CURRENT_DESKTOP', '').lower()
                if 'gnome' in desktop or 'kde' in desktop:
                    # Try to read gsettings (GNOME)
                    try:
                        import subprocess
                        result = subprocess.run([
                            'gsettings', 'get', 'org.gnome.desktop.interface', 'color-scheme'
                        ], capture_output=True, text=True)
                        if 'dark' in result.stdout.lower():
                            return 'dark'
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
            QWidget { background: #f5f6fa; }
            QLabel { color: #23272e; }
            QLabel#display { color: #23272e; }
            QLabel#history { color: #888; }
            QPushButton {
                background: #e6e9f0; color: #23272e; border: none; border-radius: 5px;
                font-size: 15px; padding: 8px;
            }
            QPushButton:pressed { background: #d1d5e0; }
            QPushButton[op="true"] { background: #dbeafe; color: #23272e; }
            QPushButton[op="true"]:pressed { background: #bcd0ee; }
            QPushButton[fn="true"] { background: #e0e7ef; color: #4b5563; }
            QPushButton[fn="true"]:pressed { background: #cfd8e3; }
            QPushButton[eq="true"] { background: #2563eb; color: #fff; }
            QPushButton[eq="true"]:pressed { background: #1d4ed8; }
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
        if use_icomoon:
            icomoon_font = QFont(icomoon_families[0], 14)
            icon_codes = [
                '\ue900',  # Calculator
                '\ue901',  # Heron's Formula
                '\ue902',  # Simple Interest
                '\ue903',  # Compound Interest
                '\ue919',  # Quadratic Equation
                '\ue904',  # Factorial
                '\ue915',  # Discount Price
                '≈',       # Approximation (always tilden)
                '\ue911',  # Prime Checker
                '\ue914',  # Right Triangle
            ]
        else:
            icomoon_font = None
            icon_codes = [
                'C', '△', 'SI', 'CI', 'QE', 'x!', '%', '≈', '2', '∆?'
            ]
        sidebar_btn_data = [
            ("Calculator", icon_codes[0]),
            ("Heron's Formula", icon_codes[1]),
            ("Simple Interest", icon_codes[2]),
            ("Compound Interest", icon_codes[3]),
            ("Quadratic Equation", icon_codes[4]),
            ("Factorial", icon_codes[5]),
            ("Discount Price", icon_codes[6]),
            ("Approximation", icon_codes[7]),
            ("Prime No. Checker", icon_codes[8]),
            ("Right Triangle Checker", icon_codes[9]),
        ]
        for idx, (tooltip, icon_text) in enumerate(sidebar_btn_data):
            btn = QPushButton(icon_text)
            btn.setToolTip(tooltip)
            btn.setFixedHeight(40)
            btn.setFixedWidth(42)
            btn.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
            btn.setProperty('fn', True)
            btn.setStyleSheet("font-size: 10px; font-weight: bold;")
            # Set font for icomoon icons only for Prime Checker and Right Triangle
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
        self.stack.addWidget(self.initFactorialUI())
        self.stack.addWidget(self.initDiscountUI())
        self.stack.addWidget(self.initApproximationUI())
        self.stack.addWidget(self.initPrimeCheckerUI())
        self.stack.addWidget(self.initRightTriangleUI())
        main_layout.addWidget(self.stack)
        self.setLayout(main_layout)
        self.switch_calculator(0)

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

    def initSpecialToolsUI(self, use_icomoon, icomoon_font):
        widget = QWidget()
        widget.setMinimumWidth(340)
        widget.setMinimumHeight(420)
        layout = QVBoxLayout(widget)
        layout.setSpacing(12)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setAlignment(Qt.AlignCenter)
        # Top toggle buttons
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(8)
        # Icons for toggles
        if use_icomoon:
            approx_icon = '\ue911'
            prime_icon = '2'
            right_icon = '\ue914'
        else:
            approx_icon = '≈'
            prime_icon = '2'
            right_icon = '∆'
        self.special_btns = []
        for idx, (name, icon) in enumerate([
            ("Approximation", approx_icon),
            ("Prime Checker", prime_icon),
            ("Right Triangle", right_icon),
        ]):
            btn = QPushButton(icon)
            btn.setToolTip(name)
            btn.setFixedHeight(32)
            btn.setFixedWidth(32)
            btn.setStyleSheet("font-size: 10px; font-weight: bold;")
            if use_icomoon and ord(icon[0]) >= 0xE000 and ord(icon[0]) <= 0xF8FF:
                btn.setFont(icomoon_font)
            btn.clicked.connect(lambda _, i=idx: self.switch_special_tool(i))
            btn_layout.addWidget(btn)
            self.special_btns.append(btn)
        layout.addLayout(btn_layout)
        # Stacked widget for the three tools
        self.special_stack = QStackedWidget()
        self.special_stack.addWidget(self.initApproximationUI())
        self.special_stack.addWidget(self.initPrimeCheckerUI())
        self.special_stack.addWidget(self.initRightTriangleUI())
        layout.addWidget(self.special_stack)
        widget.setLayout(layout)
        self.switch_special_tool(0)
        return widget

    def switch_special_tool(self, idx):
        self.special_stack.setCurrentIndex(idx)
        for i, btn in enumerate(self.special_btns):
            if i == idx:
                btn.setStyleSheet("background: #5e81ac; color: #fff; border-radius: 5px; font-size: 14px; font-weight: bold;")
            else:
                btn.setStyleSheet("background: none; color: #bfc7d5; border-radius: 5px; font-size: 14px; font-weight: bold;")

    def initApproximationUI(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(12)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setAlignment(Qt.AlignCenter)
        self.approx_input = QLineEdit()
        lbl = QLabel("<b>Enter the Number [n] :</b>")
        lbl.setAlignment(Qt.AlignCenter)
        lbl.setStyleSheet("font-size: 16px;")
        layout.addWidget(lbl, alignment=Qt.AlignCenter)
        self.approx_input.setPlaceholderText("")
        self.approx_input.setFixedWidth(180)
        self.approx_input.setFixedHeight(32)
        self.approx_input.setStyleSheet("font-size: 15px;")
        layout.addWidget(self.approx_input, alignment=Qt.AlignCenter)
        btn = QPushButton("Calculate")
        btn.setFixedHeight(36)
        btn.setFixedWidth(120)
        btn.setProperty('eq', True)
        btn.setStyleSheet("font-size: 15px;")
        btn.clicked.connect(self.calculate_approximation)
        layout.addWidget(btn, alignment=Qt.AlignCenter)
        self.approx_output = QLabel("OUTPUT AREA")
        self.approx_output.setAlignment(Qt.AlignCenter)
        self.approx_output.setFixedHeight(28)
        self.approx_output.setStyleSheet("font-size: 15px;")
        layout.addWidget(self.approx_output, alignment=Qt.AlignCenter)
        layout.addStretch(1)
        return widget

    def initPrimeCheckerUI(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(12)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setAlignment(Qt.AlignCenter)
        self.prime_input = QLineEdit()
        lbl = QLabel("<b>Enter a Number [n] :</b>")
        lbl.setAlignment(Qt.AlignCenter)
        lbl.setStyleSheet("font-size: 16px;")
        layout.addWidget(lbl, alignment=Qt.AlignCenter)
        self.prime_input.setPlaceholderText("")
        self.prime_input.setFixedWidth(180)
        self.prime_input.setFixedHeight(32)
        self.prime_input.setStyleSheet("font-size: 15px;")
        layout.addWidget(self.prime_input, alignment=Qt.AlignCenter)
        btn = QPushButton("Check Prime")
        btn.setFixedHeight(36)
        btn.setFixedWidth(120)
        btn.setProperty('eq', True)
        btn.setStyleSheet("font-size: 15px;")
        btn.clicked.connect(self.calculate_prime)
        layout.addWidget(btn, alignment=Qt.AlignCenter)
        self.prime_output = QLabel("OUTPUT AREA")
        self.prime_output.setAlignment(Qt.AlignCenter)
        self.prime_output.setFixedHeight(28)
        self.prime_output.setStyleSheet("font-size: 15px;")
        layout.addWidget(self.prime_output, alignment=Qt.AlignCenter)
        layout.addStretch(1)
        return widget

    def initRightTriangleUI(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(12)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setAlignment(Qt.AlignCenter)
        self.rt_inputs = [QLineEdit() for _ in range(3)]
        labels = ["Enter 1st Side [a] :", "Enter 2nd Side [b] :", "Enter 3rd Side [c]:"]
        for i, label in enumerate(labels):
            lbl = QLabel(f"<b>{label}</b>")
            lbl.setAlignment(Qt.AlignCenter)
            lbl.setStyleSheet("font-size: 16px;")
            layout.addWidget(lbl, alignment=Qt.AlignCenter)
            self.rt_inputs[i].setPlaceholderText("")
            self.rt_inputs[i].setFixedWidth(180)
            self.rt_inputs[i].setFixedHeight(32)
            self.rt_inputs[i].setStyleSheet("font-size: 15px;")
            layout.addWidget(self.rt_inputs[i], alignment=Qt.AlignCenter)
        btn = QPushButton("Check")
        btn.setFixedHeight(36)
        btn.setFixedWidth(120)
        btn.setProperty('eq', True)
        btn.setStyleSheet("font-size: 15px;")
        btn.clicked.connect(self.calculate_right_triangle)
        layout.addWidget(btn, alignment=Qt.AlignCenter)
        self.rt_output = QLabel("OUTPUT AREA")
        self.rt_output.setAlignment(Qt.AlignCenter)
        self.rt_output.setFixedHeight(28)
        self.rt_output.setStyleSheet("font-size: 15px;")
        layout.addWidget(self.rt_output, alignment=Qt.AlignCenter)
        layout.addStretch(1)
        return widget

    def calculate_approximation(self):
        try:
            n = float(self.approx_input.text())
            self.approx_output.setText(f"Rounded: {round(n)}")
        except Exception:
            self.approx_output.setText("Invalid input.")

    def calculate_prime(self):
        try:
            n = int(self.prime_input.text())
            if n < 2:
                self.prime_output.setText("Not Prime")
                return
            for i in range(2, int(n ** 0.5) + 1):
                if n % i == 0:
                    self.prime_output.setText("Not Prime")
                    return
            self.prime_output.setText("Prime")
        except Exception:
            self.prime_output.setText("Invalid input.")

    def calculate_right_triangle(self):
        try:
            a = float(self.rt_inputs[0].text())
            b = float(self.rt_inputs[1].text())
            c = float(self.rt_inputs[2].text())
            sides = sorted([a, b, c])
            if abs(sides[0]**2 + sides[1]**2 - sides[2]**2) < 1e-6:
                self.rt_output.setText("Right Triangle")
            else:
                self.rt_output.setText("Not Right Triangle")
        except Exception:
            self.rt_output.setText("Invalid input.")

    def initCalculatorUI(self):
        widget = QWidget()
        vbox = QVBoxLayout(widget)
        vbox.setSpacing(10)
        vbox.setContentsMargins(8, 8, 8, 8)
        self.history = QLabel("")
        self.history.setObjectName("history")
        self.history.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.history.setStyleSheet("font-size: 12px; padding-top: 20px;")
        font_id = QFontDatabase.addApplicationFont("Inter.ttf")
        font_families = QFontDatabase.applicationFontFamilies(font_id)
        if font_families:
            self.history.setFont(QFont(font_families[0], 12))
        vbox.addWidget(self.history)
        self.display = QLabel("0")
        self.display.setObjectName("display")
        self.display.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.display.setMinimumHeight(75)
        self.display.setStyleSheet("font-size: 30px; font-weight: bold; padding-right: 0.5px;")
        if font_families:
            self.display.setFont(QFont(font_families[0], 28, QFont.Bold))
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
                if font_families:
                    btn.setFont(QFont(font_families[0], 16))
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
        widget.setMinimumWidth(340)
        widget.setMinimumHeight(420)
        layout = QVBoxLayout(widget)
        layout.setSpacing(12)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setAlignment(Qt.AlignCenter)
        self.heron_inputs = [QLineEdit() for _ in range(3)]
        labels = ["First Side [a] :", "Second Side [b] :", "Third Side [c] :"]
        for i, label in enumerate(labels):
            lbl = QLabel(f"<b>{label}</b>")
            lbl.setAlignment(Qt.AlignCenter)
            lbl.setStyleSheet("font-size: 16px;")
            layout.addWidget(lbl, alignment=Qt.AlignCenter)
            self.heron_inputs[i].setPlaceholderText("")
            self.heron_inputs[i].setFixedWidth(180)
            self.heron_inputs[i].setFixedHeight(32)
            self.heron_inputs[i].setStyleSheet("font-size: 15px;")
            layout.addWidget(self.heron_inputs[i], alignment=Qt.AlignCenter)
        btn = QPushButton("Calculate")
        btn.setFixedHeight(36)
        btn.setFixedWidth(120)
        btn.setProperty('eq', True)
        btn.setStyleSheet("font-size: 15px;")
        btn.clicked.connect(self.calculate_heron)
        layout.addWidget(btn, alignment=Qt.AlignCenter)
        self.heron_output = QLabel("OUTPUT AREA")
        self.heron_output.setAlignment(Qt.AlignCenter)
        self.heron_output.setFixedHeight(28)
        self.heron_output.setStyleSheet("font-size: 15px;")
        layout.addWidget(self.heron_output, alignment=Qt.AlignCenter)
        layout.addStretch(1)
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
        layout.addStretch(1)
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
        layout.addStretch(1)
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
        layout.addStretch(1)
        return widget

    def initFactorialUI(self):
        widget = QWidget()
        widget.setMinimumWidth(340)
        widget.setMinimumHeight(260)
        layout = QVBoxLayout(widget)
        layout.setSpacing(12)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setAlignment(Qt.AlignCenter)
        self.fact_input = QLineEdit()
        lbl = QLabel("<b>Enter Number :</b>")
        lbl.setAlignment(Qt.AlignCenter)
        lbl.setStyleSheet("font-size: 16px;")
        layout.addWidget(lbl, alignment=Qt.AlignCenter)
        self.fact_input.setPlaceholderText("")
        self.fact_input.setFixedWidth(180)
        self.fact_input.setFixedHeight(32)
        self.fact_input.setStyleSheet("font-size: 15px;")
        layout.addWidget(self.fact_input, alignment=Qt.AlignCenter)
        btn = QPushButton("Calculate")
        btn.setFixedHeight(36)
        btn.setFixedWidth(120)
        btn.setProperty('eq', True)
        btn.setStyleSheet("font-size: 15px;")
        btn.clicked.connect(self.calculate_factorial)
        layout.addWidget(btn, alignment=Qt.AlignCenter)
        self.fact_output = QLabel("OUTPUT AREA")
        self.fact_output.setAlignment(Qt.AlignCenter)
        self.fact_output.setFixedHeight(28)
        self.fact_output.setStyleSheet("font-size: 15px;")
        layout.addWidget(self.fact_output, alignment=Qt.AlignCenter)
        layout.addStretch(1)
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
        self.discount_output.setFixedHeight(28)
        self.discount_output.setStyleSheet("font-size: 15px;")
        layout.addWidget(self.discount_output, alignment=Qt.AlignCenter)
        layout.addStretch(1)
        return widget

    # Calculation logic for each calculator (to be implemented)
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

    def calculate_factorial(self):
        try:
            n = int(self.fact_input.text())
            if n < 0:
                self.fact_output.setText("Invalid input.")
            else:
                self.fact_output.setText(f"{n}! = {math.factorial(n)}")
        except Exception:
            self.fact_output.setText("Invalid input.")

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

    def check_for_updates(self):
        from PySide6.QtCore import QThread, Signal

        class UpdateCheckThread(QThread):
            update_message = Signal(str)

            def __init__(self, parent=None):
                super().__init__(parent)
                self.parent = parent

            def run(self):
                try:
                    response = requests.get(UPDATE_VERSION_URL, timeout=5)
                    response.raise_for_status()
                    latest_version = response.text.strip()
                    if latest_version > self.parent.CURRENT_VERSION:
                        msg = f"🎉 PyCalc-GUI v{latest_version} is OUT NOW!"
                    elif latest_version == self.parent.CURRENT_VERSION:
                        msg = "🎉 PyCalc-GUI is up to date!"
                    elif latest_version < self.parent.CURRENT_VERSION:
                        msg = "⚠️ This is a Dev. Build of PyCalc-SE!"
                    else:
                        msg = "🎉 PyCalc-GUI is up to date!"
                except Exception:
                    msg = "⚠️ Error : Check your Internet Connection."
                self.update_message.emit(msg)

        self.update_thread = UpdateCheckThread(self)
        self.update_thread.update_message.connect(self.show_update_message)
        self.update_thread.start()

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