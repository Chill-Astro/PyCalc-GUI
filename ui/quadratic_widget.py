import math
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton)
from PySide6.QtCore import Qt

class QuadraticWidget(QWidget):
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
        formula_label = QLabel("<b>Formula:</b> x = [-b ± √(b²-4ac)] / 2a")
        formula_label.setAlignment(Qt.AlignCenter)
        formula_label.setStyleSheet("font-size: 16px; margin-bottom: 10px;")
        layout.addWidget(formula_label, alignment=Qt.AlignCenter)
        self.q_inputs = [QLineEdit() for _ in range(3)]
        labels = ["First Coeffecient (a) :", "Second Coeffecient (b) :", "Third Coeffecient (c) :"]
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
