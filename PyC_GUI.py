#!/usr/bin/env python3
import sys
import importlib
from PySide6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QStackedWidget, QFrame, QSizePolicy)
from PySide6.QtGui import QIcon, QFont, QFontDatabase
from PySide6.QtCore import Qt, QSettings, QTimer
from utils import resource_path, detect_os_theme

class Calculator(QWidget):
    def __init__(self):
        super().__init__()
        self.CURRENT_VERSION = "3.14.1.3" # About Section + Bug Fixes + Performance Improvements
        self.setWindowTitle("PyCalc GUI")
        self.setMinimumSize(430, 540)
        icon_path = resource_path("PyC_GUI.ico")
        if icon_path and os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        self.settings = QSettings("Chill-Astro", "PyCalc-GUI")
        geometry = self.settings.value("geometry")
        if geometry:
            self.restoreGeometry(geometry)
        self.initUI()
        self.apply_theme()
        self._last_theme = self._detect_os_theme()
        self._theme_timer = QTimer(self)
        self._theme_timer.setTimerType(Qt.CoarseTimer)
        self._theme_timer.timeout.connect(self._check_theme_change)
        self._theme_timer.start(1000)

    def closeEvent(self, event):
        self.settings.setValue("geometry", self.saveGeometry())
        super().closeEvent(event)

    def _detect_os_theme(self):
        return detect_os_theme()

    def _check_theme_change(self):
        current_theme = self._detect_os_theme()
        if current_theme != self._last_theme:
            self._last_theme = current_theme
            self.refresh_theme()

    def apply_theme(self):
        is_dark = self._detect_os_theme() == 'dark'
        stylesheet = self.dark_stylesheet() if is_dark else self.light_stylesheet()
        self.setStyleSheet(stylesheet)
        self._current_theme = 'dark' if is_dark else 'light'
        self.update_widget_styles()

    def refresh_theme(self):
        self.apply_theme()

    def update_widget_styles(self):
        for i in range(self.stack.count()):
            widget = self.stack.widget(i)
            if hasattr(widget, 'update_label_styles'):
                widget.update_label_styles()

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
            QPushButton[op="true"] { background: #e3e8f0; color: #23272e; }
            QPushButton[op="true"]:pressed { background: #bae6fd; }
            QPushButton[fn="true"] { background: #e0e7ef; color: #4b5563; }
            QPushButton[fn="true"]:pressed { background: #cbd5e1; }
            QPushButton[eq="true"] { background: #e0f2fe; color: #23272e; }
            QPushButton[eq="true"]:pressed { background: #bae6fd; }
        """

    def initUI(self):
        main_layout = QHBoxLayout(self)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)
        sidebar = QFrame()
        sidebar.setFixedWidth(52)
        sidebar.setFrameShape(QFrame.StyledPanel)
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setSpacing(4)
        sidebar_layout.setContentsMargins(2, 8, 2, 8)
        self.sidebar_buttons = []
        icomoon_font_id = QFontDatabase.addApplicationFont(resource_path("icomoon.ttf"))
        icomoon_families = QFontDatabase.applicationFontFamilies(icomoon_font_id)
        use_icomoon = bool(icomoon_families)
        if use_icomoon:
            icomoon_font = QFont(icomoon_families[0], 14)
            icon_codes = ['\ue900', '\ue901', '\ue902', '\ue903', '\ue919', '\ue915', '🛈']
        else:
            icomoon_font = None
            icon_codes = ['C', '△', 'SI', 'CI', 'QE', '%', '🛈']
        self.calculators = [
            ("Calculator", icon_codes[0], "ui.calculator_widget", "CalculatorWidget"),
            ("Heron's Formula", icon_codes[1], "ui.heron_widget", "HeronWidget"),
            ("Simple Interest", icon_codes[2], "ui.simple_interest_widget", "SimpleInterestWidget"),
            ("Compound Interest", icon_codes[3], "ui.compound_interest_widget", "CompoundInterestWidget"),
            ("Quadratic Equation", icon_codes[4], "ui.quadratic_widget", "QuadraticWidget"),
            ("Discount Price", icon_codes[5], "ui.discount_widget", "DiscountWidget"),
            ("About", icon_codes[6], "ui.about_widget", "AboutWidget"),
        ]
        for idx, (tooltip, icon_text, _, _) in enumerate(self.calculators):
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
        self.stack = QStackedWidget()
        self.loaded_widgets = {}
        main_layout.addWidget(self.stack)
        self.setLayout(main_layout)
        self.switch_calculator(0)

    def switch_calculator(self, idx):
        if idx not in self.loaded_widgets:
            tooltip, icon_text, module_name, class_name = self.calculators[idx]
            try:
                module = importlib.import_module(module_name)
                WidgetClass = getattr(module, class_name)
                if class_name == "AboutWidget":
                    widget = WidgetClass(self.CURRENT_VERSION)
                else:
                    widget = WidgetClass()
                self.stack.addWidget(widget)
                self.loaded_widgets[idx] = self.stack.indexOf(widget)
            except (ImportError, AttributeError) as e:
                print(f"Error loading widget: {e}")
                return
        self.stack.setCurrentIndex(self.loaded_widgets[idx])
        for i, btn in enumerate(self.sidebar_buttons):
            btn.setProperty('active', i == idx)
            btn.setStyleSheet(self.button_style(i == idx))

    def button_style(self, active):
        theme = self._detect_os_theme()
        if theme == 'dark':
            if active:
                return "background: #5e81ac; color: #fff; border-radius: 5px; font-size: 18px; font-weight: bold;"
            else:
                return "background: #2e3440; color: #bfc7d5; border-radius: 5px; font-size: 18px;"
        else:
            if active:
                return "background: #2563eb; color: #fff; border-radius: 5px; font-size: 18px; font-weight: bold;"
            else:
                return "background: #e0e7ef; color: #4b5563; border-radius: 5px; font-size: 18px;"

if __name__ == "__main__":
    import os
    app = QApplication(sys.argv)
    
    # Load and apply the Inter font
    font_id = QFontDatabase.addApplicationFont(resource_path("Inter.ttf"))
    if font_id != -1:
        font_families = QFontDatabase.applicationFontFamilies(font_id)
        if font_families:
            inter_font = QFont(font_families[0])
            app.setFont(inter_font)

    calc = Calculator()
    calc.show()
    sys.exit(app.exec())
