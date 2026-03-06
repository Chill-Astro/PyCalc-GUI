from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton
from PySide6.QtGui import QIcon
from PySide6.QtCore import Qt, QThread, Signal
import requests
import os
from utils import resource_path

UPDATE_VERSION_URL = "https://gist.githubusercontent.com/Chill-Astro/738d8c4978d0a71a028235c375a30d1f/raw/cc42d26ad09a37c594401d82fcbb8d2fa97f67ef/PyC_GUI_V.txt"  # Gist URL

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

class AboutWidget(QWidget):
    def __init__(self, current_version):
        super().__init__()
        self.CURRENT_VERSION = current_version
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout(self)
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
        layout.addWidget(name_label, alignment=Qt.AlignCenter)
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

    def check_for_updates_about(self):
        self.update_thread = UpdateCheckThread(self, self.CURRENT_VERSION)
        self.update_thread.update_message.connect(self.show_about_update_message)
        self.update_thread.start()

    def show_about_update_message(self, msg):
        self.about_update_status.setText(msg)
        self.about_update_status.setStyleSheet("font-size: 15px; margin-top: 8px;")
