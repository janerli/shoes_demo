from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import *

from tabs.catalog_tab import CatalogTab
from tabs.orders_tab import OrdersTab


class MainWindow(QMainWindow):
    def __init__(self, user, db):
        super().__init__()
        self.resize(1200, 800)
        self.user = user
        self.db = db
        self.setWindowTitle(f"Магазин обуви | {self.user['full_name']} | {self.user['role']}")
        self.setup_ui()

    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        top_layout = QHBoxLayout()
        name_lbl = QLabel(self.user['full_name'])
        name_lbl.setStyleSheet("font-size:20px; font-weight:bold;")
        name_lbl.setAlignment(Qt.AlignmentFlag.AlignRight)
        logout_btn = QPushButton("Выход")
        logout_btn.setFixedWidth(100)
        logout_btn.clicked.connect(self.close)
        top_layout.addWidget(logout_btn)
        top_layout.addWidget(name_lbl)
        layout.addLayout(top_layout)

        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)

        self.tabs.addTab(CatalogTab(self.user, self.db), "Каталог")

        if self.user['role'] in ("admin", "manager"):
            self.tabs.addTab(OrdersTab(self.user, self.db), "Заказы")


