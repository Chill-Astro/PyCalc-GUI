from PySide6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton)
from PySide6.QtCore import Qt

class DiscountWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setMinimumWidth(340)
        self.setMinimumHeight(260)
        layout = QVBoxLayout(self)
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
        self.discount_output = QLabel(r"DISCOUNT OUTPUT\nFINAL PRICE")
        self.discount_output.setAlignment(Qt.AlignCenter)
        self.discount_output.setFixedHeight(35)
        self.discount_output.setStyleSheet("font-size: 15px;")
        layout.addWidget(self.discount_output, alignment=Qt.AlignCenter)

    def calculate_discount(self):
        try:
            price = float(self.discount_inputs[0].text())
            discount = float(self.discount_inputs[1].text())
            disc_amt = price * discount / 100
            final = price - disc_amt
            self.discount_output.setText(f"""Discount: {disc_amt:.2f}
Final Price: {final:.2f}""")
        except Exception:
            self.discount_output.setText("Invalid input.")
