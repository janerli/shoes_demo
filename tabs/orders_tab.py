from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import *

from widgets.add_edit_order import AddEditOrder


class OrdersTab(QWidget):
    def __init__(self, user, db):
        super().__init__()
        self.user = user
        self.db = db
        self.setup_ui()
        self.load_data()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        add_btn = QPushButton("Добавить заказ")
        add_btn.clicked.connect(self.add_order)
        layout.addWidget(add_btn)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)

        self.scroll_widget = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_widget)
        self.scroll_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.scroll_area.setWidget(self.scroll_widget)

        layout.addWidget(self.scroll_area)

    def load_data(self):
        query = ("""select 
            o.order_id,
            s.status_name,
            pp.address,
            o.order_date,
            o.delivery_date,
            o.items
                from orders o 
                 left join statuses s on o.status_id = s.status_id
                 left join pickup_points pp on pp.pickup_point_id = o.pickup_point_id""")

        orders = self.db.fetchall(query)
        self.clear_layout(self.scroll_layout)

        for order in orders:
            card = self.create_card(order)
            self.scroll_layout.addWidget(card)

    def create_card(self, order):
        card = QFrame()
        card.setFrameShape(QFrame.Shape.Box)
        card.setFixedSize(1100, 200)
        card.setStyleSheet("border: 3px solid black;")
        card_layout = QHBoxLayout(card)
        card_layout.setContentsMargins(10, 10, 10, 10)
        card_layout.setSpacing(15)

        card.mouseDoubleClickEvent = lambda event: self.edit_order(order['order_id'])

        # ЛЕВЫЙ БЛОК — данные заказа
        info_frame = QFrame()
        info_frame.setFrameShape(QFrame.Shape.Box)
        info_frame.setStyleSheet("border: 3px solid black; background-color: transparent;")
        info_frame.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        lbl_layout = QVBoxLayout(info_frame)
        lbl_layout.setContentsMargins(8, 8, 8, 8)
        lbl_layout.setSpacing(5)
        lbl_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        order_id = QLabel(f"Номер заказа: {order['order_id']}")
        order_id.setStyleSheet("font-weight: bold; border: none;")
        lbl_layout.addWidget(order_id)

        for text in [
            f"Статус заказа: {order['status_name']}",
            f"Дата заказа: {order['order_date']}",
            f"Артикул: {order['items']}"
        ]:
            lbl = QLabel(text)
            lbl.setStyleSheet("border: none;")
            lbl_layout.addWidget(lbl)

        lbl_layout.addStretch()
        card_layout.addWidget(info_frame)

        # ПРАВЫЙ БЛОК — дата доставки + кнопка удаления
        right_frame = QFrame()
        right_frame.setFrameShape(QFrame.Shape.Box)
        right_frame.setFixedWidth(200)
        right_frame.setStyleSheet("border: 3px solid black; background-color: transparent;")
        right_frame.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding)
        right_layout = QVBoxLayout(right_frame)
        right_layout.setContentsMargins(8, 8, 8, 8)
        right_layout.setSpacing(8)
        right_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        delivery_lbl = QLabel(f"Дата доставки\n{order['delivery_date']}")
        delivery_lbl.setStyleSheet("border: none;")
        delivery_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        delivery_lbl.setFixedSize(150, 100)
        right_layout.addWidget(delivery_lbl, alignment=Qt.AlignmentFlag.AlignCenter)

        del_btn = QPushButton("Удалить")
        del_btn.setFixedWidth(150)
        del_btn.setStyleSheet("border: 1px solid black;")
        del_btn.clicked.connect(lambda: self.delete_order(order['order_id']))
        right_layout.addWidget(del_btn, alignment=Qt.AlignmentFlag.AlignCenter)

        card_layout.addWidget(right_frame)
        return card

    def edit_order(self, order_id):
        order = self.db.fetchone("select * from orders where order_id = %s", (order_id,))

        if order:
            dialog = AddEditOrder(self.user, self.db, self, order)
            if dialog.exec() == 1:
                self.load_data()

    def add_order(self):
        dialog = AddEditOrder(self.user, self.db, self, order=None)
        if dialog.exec() == 1:
            self.load_data()
            QMessageBox.information(self, "Успех", "Заказ добавлен")

    def delete_order(self, order_id):
        reply = QMessageBox.question(self, "Удаление заказа", "Вы хотите удалить заказ?",
                             QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            self.db.execute("DELETE from orders where order_id = %s", (order_id,))
            QMessageBox.information(self, "Успех", f"Заказ {order_id} удален")

    def clear_layout(self, layout):
        while layout.count():
            child = layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()