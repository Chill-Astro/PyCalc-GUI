from PySide6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton)
from PySide6.QtCore import Qt

class SimpleInterestWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setMinimumWidth(340)
        self.setMinimumHeight(420)
        layout = QVBoxLayout(self)
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

    def calculate_simple_interest(self):
        try:
            p = float(self.si_inputs[0].text())
            r = float(self.si_inputs[1].text())
            t = float(self.si_inputs[2].text())
            si = (p * r * t) / 100
            self.si_output.setText(f"Simple Interest: {si:.2f}")
        except Exception:
            self.si_output.setText("Invalid input.")
