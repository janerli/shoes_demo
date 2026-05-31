from PyQt6.QtWidgets import *
from PyQt6.QtCore import QDate

class AddEditOrder(QDialog):
    def __init__(self, user, db, parent, order=None):
        super().__init__(parent)
        self.db = db
        self.user = user
        self.order = order

        self.setWindowTitle("Добавление заказа" if order is None else "Редактирование заказа")
        self.setModal(True)
        self.resize(550, 400)
        self.setup_ui()
        self.load_data()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        form = QFormLayout()

        self.status_cb = QComboBox()
        form.addRow("Статус: ", self.status_cb)

        self.pickup_cb = QComboBox()
        form.addRow("Пункт выдачи: ", self.pickup_cb)

        self.order_date = QDateEdit()
        self.order_date.setDate(QDate.currentDate())
        self.order_date.setCalendarPopup(True)
        form.addRow("Дата заказа: ", self.order_date)

        self.delivery_date = QDateEdit()
        self.delivery_date.setDate(QDate.currentDate().addDays(5))
        self.delivery_date.setCalendarPopup(True)
        form.addRow("Дата доставки: ", self.delivery_date)

        self.items_text = QTextEdit()
        self.items_text.setPlaceholderText("Пример: А112Т4, 2, F635R4, 2")
        self.items_text.setMaximumHeight(100)
        form.addRow("Артикул: ", self.items_text)

        layout.addLayout(form)

        btn_layout = QHBoxLayout()
        save_btn = QPushButton("Сохранить")
        save_btn.clicked.connect(self.save)
        cancel_btn = QPushButton("Отмена")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(save_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)

    def load_data(self):
        statuses = self.db.fetchall("select * from statuses order by status_id")
        for status in statuses:
            self.status_cb.addItem(status['status_name'], status['status_id'])

        pickups = self.db.fetchall("select * from pickup_points order by pickup_point_id")
        for pickup in pickups:
            self.pickup_cb.addItem(pickup['address'], pickup['pickup_point_id'])

        if self.order is not None:
            for i in range(self.status_cb.count()):
                if self.status_cb.itemData(i) == self.order['status_id']:
                    self.status_cb.setCurrentIndex(i)
                    break

            for i in range(self.pickup_cb.count()):
                if self.pickup_cb.itemData(i) == self.order['pickup_point_id']:
                    self.pickup_cb.setCurrentIndex(i)
                    break

            od = self.order['order_date']
            self.order_date.setDate(QDate(od.year, od.month, od.day))
            if self.order.get('delivery_date'):
                d = self.order['delivery_date']
                self.delivery_date.setDate(QDate(d.year, d.month, d.day))

            self.items_text.setText(self.order.get('items', ''))

    def save(self):
        status_id = self.status_cb.currentData()
        pickup_id = self.pickup_cb.currentData()
        order_date = self.order_date.date().toString("yyyy-MM-dd")
        delivery_date = self.delivery_date.date().toString("yyyy-MM-dd")
        items = self.items_text.toPlainText().strip()

        if not items:
            QMessageBox.warning(self, "Ошибка", "Заполните артикулы заказа")
            return

        if pickup_id is None:
            QMessageBox.warning(self, "Ошибка", "Выберите пункт выдачи")
            return

        if status_id is None:
            QMessageBox.warning(self, "Ошибка", "Выберите статус")
            return

        if self.order is None:
            order_id = self.db.execute("""insert into 
            orders(status_id, pickup_point_id, order_date, delivery_date, items, user_id)
            VALUES (%s, %s, %s, %s, %s, %s)""",(
                status_id,pickup_id,order_date,delivery_date,items,self.user['role_id']
            ))

            QMessageBox.information(self, "Успех", f"Заказ №{order_id} успешно добавлен")
        else:
            self.db.execute("""update orders
            set status_id = %s, pickup_point_id = %s, order_date = %s,
                            delivery_date = %s, items = %s
            where order_id=%s""", (
                status_id, pickup_id, order_date, delivery_date, items, self.order['order_id']
            ))

            QMessageBox.information(self, "Успех", f"Заказ №{self.order['order_id']} успешно обновлен")

            self.accept()

    def get_order_id(self):
        if self.order:
            return self.order['order_id']
        return None

