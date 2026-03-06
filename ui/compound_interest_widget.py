from PySide6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton)
from PySide6.QtCore import Qt

class CompoundInterestWidget(QWidget):
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
        formula_label = QLabel("<b>Formula:</b> A = P(1 + R/n)^(nt)")
        formula_label.setAlignment(Qt.AlignCenter)
        formula_label.setStyleSheet("font-size: 16px; margin-bottom: 10px;")
        layout.addWidget(formula_label, alignment=Qt.AlignCenter)
        self.ci_inputs = [QLineEdit() for _ in range(4)]
        labels = ["Principal (P) :", "Rate (R%) :", "Time (t in Years):", "Compounding Frequency (n) :"]
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

    def calculate_compound_interest(self):
        try:
            p = float(self.ci_inputs[0].text())
            r = float(self.ci_inputs[1].text()) / 100
            t = float(self.ci_inputs[2].text())
            n = float(self.ci_inputs[3].text())
            amount = p * (1 + r / n) ** (n * t)
            ci = amount - p
            self.ci_output.setText(f"""Compound Interest: {ci:.2f}
Total: {amount:.2f}""")
        except Exception:
            self.ci_output.setText("Invalid input.")
