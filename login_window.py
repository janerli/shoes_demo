from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import *

class LoginDialog(QDialog):
    def __init__(self, db):
        super().__init__()
        self.setWindowTitle("Авторизация")
        self.resize(400,600)
        self.db = db
        self.user = None
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        logo_lbl = QLabel()
        pixmap = QPixmap("images/icon.jpg")
        if not pixmap.isNull():
            pixmap = pixmap.scaled(400,400, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            logo_lbl.setPixmap(pixmap)
        logo_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(logo_lbl)
        form = QFormLayout()

        self.login = QLineEdit()
        self.password = QLineEdit()
        self.password.setEchoMode(QLineEdit.EchoMode.Password)

        form.addRow("Логин ", self.login)
        form.addRow("Пароль ", self.password)

        layout.addLayout(form)

        login_btn = QPushButton("Войти")
        login_btn.clicked.connect(self.log_in)
        guest_btn = QPushButton("Войти как гость")
        guest_btn.clicked.connect(self.guest_login)

        layout.addWidget(login_btn)
        layout.addWidget(guest_btn)

    def log_in(self):
        username = self.login.text().strip()
        password = self.password.text().strip()

        user = self.db.fetchone("select u.*, r.role_name from users u join roles r on r.role_id = u.role_id where username=%s and password_hash=%s",
                                (username, password))
        if user:
            self.user = {
                "username": user["username"],
                "full_name": user["full_name"],
                "role": user["role_name"],
                "role_id": user["role_id"]
            }
            self.accept()

    def guest_login(self):
        self.user = {
            "username": "guest",
            "full_name": "guest",
            "role": "guest",
            "role_id": 4
        }
        self.accept()

    def get_user(self):
        return self.user
