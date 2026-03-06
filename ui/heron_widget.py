import math
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton)
from PySide6.QtCore import Qt

class HeronWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        outer = QVBoxLayout(self)
        outer.setAlignment(Qt.AlignCenter)
        inner = QVBoxLayout()
        inner.setSpacing(12)
        inner.setContentsMargins(24, 24, 24, 24)
        inner.setAlignment(Qt.AlignCenter)
        formula_label = QLabel("<b>Formula:</b> Area = √s(s-a)(s-b)(s-c)")
        formula_label.setAlignment(Qt.AlignCenter)
        formula_label.setStyleSheet("font-size: 16px; margin-bottom: 10px;")
        inner.addWidget(formula_label, alignment=Qt.AlignCenter)
        self.heron_inputs = [QLineEdit() for _ in range(3)]
        labels = ["First Side (a) :", "Second Side (b) :", "Third Side (c) :"]
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
