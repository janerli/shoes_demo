from datetime import datetime

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import *

from widgets.add_edit_product import AddEditProduct


class CatalogTab(QWidget):
    def __init__(self, user, db):
        super().__init__()
        self.user = user
        self.db = db
        self.setup_ui()
        if user['role'] in ['manager', 'admin']:
            self.load_cb()
        self.load_data()

    def setup_ui(self):
        layout = QVBoxLayout(self)


        if self.user['role'] in ('admin', 'manager'):
            filter_group = QGroupBox("Фильтры")
            filter_layout = QHBoxLayout(filter_group)
            self.search_line = QLineEdit()
            self.search_line.setPlaceholderText("Поиск...")
            self.search_line.textChanged.connect(self.load_data)
            self.supplier_cb = QComboBox()
            self.supplier_cb.currentIndexChanged.connect(self.load_data)
            self.stock_cb = QComboBox()
            self.stock_cb.addItems(["По возрастанию", "По убыванию"])
            self.stock_cb.currentIndexChanged.connect(self.load_data)
            filter_layout.addWidget(self.search_line)
            filter_layout.addWidget(self.supplier_cb)
            filter_layout.addWidget(self.stock_cb)
            layout.addWidget(filter_group)

            add_btn = QPushButton("Добавить товар")
            add_btn.clicked.connect(self.add_product)
            layout.addWidget(add_btn)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)

        self.scroll_widget = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_widget)
        self.scroll_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.scroll_area.setWidget(self.scroll_widget)

        layout.addWidget(self.scroll_area)

    def load_data(self):
        query = """
        select 
        p.product_id,
        p.article,
        p.name,
        p.description,
        p.price,
        p.stock,
        p.sale,
        p.image_path,
        c.category_name,
        m.manufacturer_name,
        s.supplier_name,
        u.unit_name
        from products p
        left join categories c on p.category_id = c.category_id
        left join manufacturers m on p.manufacturer_id = m.manufacturer_id
        left join suppliers s on p.supplier_id = s.supplier_id
        left join units u on p.unit_id = u.unit_id
        where 1=1"""
        params = []

        if self.user['role'] in ['manager', 'admin']:
            if self.search_line.text().strip():
                query += " AND (p.name like %s OR c.category_name like %s)"
                params.append(f"%{self.search_line.text()}%")
                params.append(f"%{self.search_line.text()}%")
            if self.supplier_cb.currentText() != "Все поставщики":
                query += " AND s.supplier_name = %s"
                params.append(self.supplier_cb.currentText())
            if self.stock_cb.currentIndex() == 0:
                query += " ORDER BY p.stock ASC"
            if self.stock_cb.currentIndex() == 1:
                query += " ORDER BY p.stock DESC"

        shoes = self.db.fetchall(query, params)
        self.clear_layout(self.scroll_layout)

        for shoe in shoes:
            card = self.create_card(shoe)
            self.scroll_layout.addWidget(card)

    def create_card(self, shoe):
        card = QFrame()
        card.setFrameShape(QFrame.Shape.Box)
        card.setFixedSize(1100, 230)
        card_layout = QHBoxLayout(card)
        card_layout.setContentsMargins(10, 10, 10, 10)
        card_layout.setSpacing(15)

        if shoe['stock'] == 0:
            card.setStyleSheet("background-color: lightblue;border: 3px solid black;")
        elif shoe['sale'] > 15:
            card.setStyleSheet("background-color: #2E8B57;border: 3px solid black;")
        else:
            card.setStyleSheet("background-color: white;border: 3px solid black;")

        if self.user['role'] in ['manager', 'admin']:
            card.mouseDoubleClickEvent = lambda event: self.edit_product(shoe['product_id'])

        image = QLabel("")
        image.setAlignment(Qt.AlignmentFlag.AlignCenter)
        image.setFrameShape(QFrame.Shape.Box)
        image.setStyleSheet("background-color: #e0e0e0; border: 3px solid black;")
        image.setFixedWidth(300)
        image.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding)
        if shoe['image_path']:
            pixmap = QPixmap(shoe['image_path'])
            if not pixmap.isNull():
                pixmap = pixmap.scaled(300, 200, Qt.AspectRatioMode.KeepAspectRatio)
                image.setPixmap(pixmap)
        else:
            pixmap = QPixmap("images/picture.png")
            pixmap = pixmap.scaled(300, 200, Qt.AspectRatioMode.KeepAspectRatio)
            image.setPixmap(pixmap)
        card_layout.addWidget(image)

        info_frame = QFrame()
        info_frame.setFrameShape(QFrame.Shape.Box)
        info_frame.setStyleSheet("border: 3px solid black; background-color: transparent;")
        info_frame.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        lbl_layout = QVBoxLayout(info_frame)
        lbl_layout.setSpacing(5)
        lbl_layout.setContentsMargins(8, 8, 8, 8)
        lbl_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        naming_lbl = QLabel(f"{shoe['category_name']} | {shoe['name']}")
        naming_lbl.setStyleSheet("font-weight: bold; border: none;")
        lbl_layout.addWidget(naming_lbl)

        desc_lbl = QLabel(f"Описание товара: {shoe['description']}")
        desc_lbl.setStyleSheet("border: none;")
        lbl_layout.addWidget(desc_lbl)

        manuf_lbl = QLabel(f"Производитель: {shoe['manufacturer_name']}")
        manuf_lbl.setStyleSheet("border: none;")
        lbl_layout.addWidget(manuf_lbl)

        supp_lbl = QLabel(f"Поставщик: {shoe['supplier_name']}")
        supp_lbl.setStyleSheet("border: none;")
        lbl_layout.addWidget(supp_lbl)

        price_layout = QHBoxLayout()
        price_layout.setSpacing(10)
        if shoe['sale'] > 0:
            old_price = QLabel(f"{shoe['price']:,.0f} руб.")
            old_price.setFixedWidth(150)
            old_price.setStyleSheet("text-decoration: line-through; color: red; border: none;")
            price_layout.addWidget(old_price)

            new_price = shoe['price'] * (100 - shoe['sale']) / 100
            new_price_lbl = QLabel(f"{new_price:,.0f} руб.")
            new_price_lbl.setStyleSheet("font-weight: bold; border: none;")
            price_layout.addWidget(new_price_lbl)
        else:
            price_lbl = QLabel(f"Цена: {shoe['price']:,.0f} руб.")
            price_lbl.setStyleSheet("font-weight: bold; border: none;")
            price_layout.addWidget(price_lbl)
        price_layout.addStretch()
        lbl_layout.addLayout(price_layout)

        unit_lbl = QLabel(f"Единица измерения: {shoe['unit_name']}")
        unit_lbl.setStyleSheet("border: none;")
        lbl_layout.addWidget(unit_lbl)

        stock_label = QLabel(f"Количество на складе: {shoe['stock']} шт.")
        stock_label.setStyleSheet("border: none;")
        lbl_layout.addWidget(stock_label)

        lbl_layout.addStretch()
        card_layout.addWidget(info_frame)

        right_widget = QFrame()
        right_widget.setFrameShape(QFrame.Shape.Box)
        right_widget.setFixedWidth(100)
        right_widget.setStyleSheet("border: 3px solid black; background-color: transparent;")
        right_widget.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding)
        right_layout = QVBoxLayout(right_widget)
        right_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        if shoe['sale'] > 0:
            sale_lbl = QLabel(f"Скидка\n{shoe['sale']}%")
            sale_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            sale_lbl.setStyleSheet("border: none; font-weight: bold;")
            right_layout.addWidget(sale_lbl)

        if self.user['role'] == "admin":
            del_btn = QPushButton("X")
            del_btn.setStyleSheet("border: 1px solid black;")
            del_btn.clicked.connect(lambda: self.delete_product(shoe))
            right_layout.addWidget(del_btn)

        card_layout.addWidget(right_widget)

        return card

    def delete_product(self, shoe):
        check = self.db.fetchone(
            "SELECT * FROM order_items WHERE product_id = %s",
            (shoe['product_id'],)
        )

        if check:
            QMessageBox.warning(self, "Ошибка", "Нельзя удалить товар, так как он присутствует в заказе")
            return

        reply = QMessageBox.question(self, "Удаление", "Удалить товар?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            self.db.execute("DELETE from products where product_id = %s",shoe['product_id'])
            self.load_data()
            QMessageBox.information(self, "Успех", "Товар удален")

    def clear_layout(self, layout):
        while layout.count():
            child = layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

    def add_product(self):
        dlg = AddEditProduct(self.user, self.db, self, None)
        if dlg.exec() == 1:
            self.load_data()
            QMessageBox.information(self, "Успех", "Товар успешно добавлен")

    def edit_product(self, product_id):
        product = self.db.fetchone("select * from products where product_id = %s",product_id)
        if product:
            dlg = AddEditProduct(self.user, self.db, self, product)
            if dlg.exec() == 1:
                self.load_data()

    def load_cb(self):
        self.supplier_cb.clear()
        self.supplier_cb.addItem("Все поставщики")
        query = "select supplier_name from suppliers"
        suppliers = self.db.fetchall(query)
        for supplier in suppliers:
            self.supplier_cb.addItem(supplier['supplier_name'])
