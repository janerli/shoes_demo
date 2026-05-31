import os
import shutil

from PyQt6.QtGui import QTextOption
from PyQt6.QtWidgets import *

class AddEditProduct(QDialog):
    def __init__(self, user, db, parent, product=None):
        super().__init__(parent)
        self.setModal(True)
        title = "Редактирование товара" if product else "Добавление товара"
        self.setWindowTitle(title)
        self.user = user
        self.db = db
        self.product = product
        self.setup_ui()
        self.load_data()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        form = QFormLayout()

        self.article = QLineEdit()
        form.addRow("Артикул: ", self.article)

        self.name = QLineEdit()
        form.addRow("Наименование: ", self.name)

        self.category = QComboBox()
        form.addRow("Категория: ", self.category)

        self.unit = QComboBox()
        form.addRow("Единица изме: ", self.unit)

        self.price = QDoubleSpinBox()
        self.price.setSuffix(" руб.")
        self.price.setMinimum(0.00)
        form.addRow("Цена: ", self.price)

        self.supplier = QComboBox()
        form.addRow("Поставщик: ", self.supplier)

        self.manuf = QComboBox()
        form.addRow("Производитель: ", self.manuf)

        self.sale = QSpinBox()
        self.sale.setSuffix(" %")
        self.sale.setMinimum(0)
        form.addRow("Скидка: ", self.sale)

        self.stock = QSpinBox()
        self.stock.setMinimum(0)
        form.addRow("Количество на складе: ", self.stock)

        self.description = QTextEdit()
        self.description.setWordWrapMode(QTextOption.WrapMode.WordWrap)
        form.addRow("Описание: ", self.description)

        img_layout = QHBoxLayout()
        self.image_path = QLineEdit()
        img_btn = QPushButton("Обзор")
        img_btn.clicked.connect(self.browse_img)
        img_layout.addWidget(self.image_path)
        img_layout.addWidget(img_btn)
        form.addRow("Изображение: ", img_layout)

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
        categories = self.db.fetchall("select * from categories")
        for category in categories:
            self.category.addItem(category['category_name'], category['category_id'])

        units = self.db.fetchall("select * from units")
        for unit in units:
            self.unit.addItem(unit['unit_name'], unit['unit_id'])

        suppliers = self.db.fetchall("select * from suppliers")
        for supplier in suppliers:
            self.supplier.addItem(supplier['supplier_name'], supplier['supplier_id'])

        manufacturers = self.db.fetchall("select * from manufacturers")
        for manufacturer in manufacturers:
            self.manuf.addItem(manufacturer['manufacturer_name'],manufacturer['manufacturer_id'])

        if self.product is not None:
            self.name.setText(self.product['name'])
            self.price.setValue(self.product['price'])
            self.sale.setValue(self.product['sale'])
            self.image_path.setText(self.product['image_path'])
            self.stock.setValue(self.product['stock'])
            self.article.setText(self.product['article'])
            self.description.setText(self.product['description'])

            for i in range(self.category.count()):
                if self.category.itemData(i) == self.product['category_id']:
                    self.category.setCurrentIndex(i)
                    break

            for i in range(self.unit.count()):
                if self.unit.itemData(i) == self.product['unit_id']:
                    self.unit.setCurrentIndex(i)
                    break

            for i in range(self.supplier.count()):
                if self.supplier.itemData(i) == self.product['supplier_id']:
                    self.supplier.setCurrentIndex(i)
                    break

            for i in range(self.manuf.count()):
                if self.manuf.itemData(i) == self.product['manufacturer_id']:
                    self.manuf.setCurrentIndex(i)
                    break

    def browse_img(self):
        image_path, _ = QFileDialog.getOpenFileName(self,
                                                    "Выберите фото",
                                                    "",
                                                    "All Files (*)")
        if not image_path:
            return

        os.makedirs("images", exist_ok=True)

        file_name = os.path.basename(image_path)
        new_path = os.path.join("images", file_name)

        if os.path.abspath(image_path) != os.path.abspath(new_path):
            shutil.copy(image_path, new_path)

        self.image_path.setText(image_path)

    def save(self):
        name = self.name.text().strip()
        category = self.category.currentData()
        article = self.article.text().strip()
        unit = self.unit.currentData()
        price = self.price.value()
        supplier = self.supplier.currentData()
        manufacturer = self.manuf.currentData()
        sale = self.sale.value()
        stock = self.stock.value()
        description = self.description.toPlainText().strip()
        image_path = self.image_path.text().strip()

        if self.product is not None:
            query = """
            update products
            set name=%s, category_id=%s, article=%s, unit_id=%s,
            price=%s, supplier_id=%s, manufacturer_id=%s, sale=%s,
            stock=%s, description=%s, image_path=%s
            where product_id=%s"""

            self.db.execute(query, (name, category, article, unit, price, supplier, manufacturer, sale, stock, description, image_path, self.product['product_id']))
            QMessageBox.information(self, "Успех", f"Продукт №{self.product['product_id']} успешно обновлен")
            self.accept()
        else:
            query = """insert into products(name, category_id, article, unit_id, price, supplier_id, manufacturer_id, sale, stock, description, image_path)
            values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""

            new_id = self.db.execute(query, (name, category, article, unit, price, supplier, manufacturer, sale, stock, description, image_path))
            QMessageBox.information(self, "Успех", f"Новый продукт №{new_id} был успешно добавлен")
            self.accept()