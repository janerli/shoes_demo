from PyQt6.QtGui import QFont, QIcon
from PyQt6.QtWidgets import QApplication
import sys
from database import Database
from login_window import LoginDialog
from main_window import MainWindow

def main():
    app = QApplication(sys.argv)
    font = QFont("Times New Roman", 12)
    app.setFont(font)
    app.setWindowIcon(QIcon("images/Icon.ico"))
    db = Database()
    db.connect()
    dlg = LoginDialog(db)
    if dlg.exec() == 1:
        user = dlg.get_user()
        window = MainWindow(user, db)
        window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()