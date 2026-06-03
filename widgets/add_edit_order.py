from PyQt6.QtWidgets import *
from PyQt6.QtCore import QDate, Qt

class AddEditOrder(QDialog):
    def __init__(self, user, db, parent, order=None):
        super().__init__(parent)
        self.db = db
        self.user = user
        self.order = order
        self.selected_products = []  # список выбранных товаров

        self.setWindowTitle("Добавление заказа" if order is None else "Редактирование заказа")
        self.setModal(True)
        self.resize(850, 600)
        self.setup_ui()
        self.load_data()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        # ========== Верхняя часть - информация о заказе ==========
        form_group = QGroupBox("Информация о заказе")
        form_layout = QFormLayout(form_group)

        self.status_cb = QComboBox()
        form_layout.addRow("Статус: ", self.status_cb)

        self.pickup_cb = QComboBox()
        form_layout.addRow("Пункт выдачи: ", self.pickup_cb)

        self.order_date = QDateEdit()
        self.order_date.setDate(QDate.currentDate())
        self.order_date.setCalendarPopup(True)
        form_layout.addRow("Дата заказа: ", self.order_date)

        self.delivery_date = QDateEdit()
        self.delivery_date.setDate(QDate.currentDate().addDays(5))
        self.delivery_date.setCalendarPopup(True)
        form_layout.addRow("Дата доставки: ", self.delivery_date)

        layout.addWidget(form_group)

        # ========== Таблица товаров в заказе ==========
        items_group = QGroupBox("Товары в заказе")
        items_layout = QVBoxLayout(items_group)

        # Таблица
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["Артикул", "Наименование", "Кол-во", "Цена, руб.", "Сумма, руб."])
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.horizontalHeader().setStretchLastSection(True)
        items_layout.addWidget(self.table)

        # Кнопки управления
        btn_layout = QHBoxLayout()
        self.add_btn = QPushButton("Добавить товар")
        self.add_btn.clicked.connect(self.add_product)
        self.edit_btn = QPushButton("Изменить количество")
        self.edit_btn.clicked.connect(self.change_quantity)
        self.delete_btn = QPushButton("Удалить товар")
        self.delete_btn.clicked.connect(self.remove_product)

        btn_layout.addWidget(self.add_btn)
        btn_layout.addWidget(self.edit_btn)
        btn_layout.addWidget(self.delete_btn)
        items_layout.addLayout(btn_layout)

        layout.addWidget(items_group)

        # ========== Кнопки сохранить/отмена ==========
        btn_layout2 = QHBoxLayout()
        save_btn = QPushButton("Сохранить")
        save_btn.clicked.connect(self.save)
        cancel_btn = QPushButton("Отмена")
        cancel_btn.clicked.connect(self.reject)
        btn_layout2.addWidget(save_btn)
        btn_layout2.addWidget(cancel_btn)
        layout.addLayout(btn_layout2)

    def update_table(self):
        """Обновление таблицы товаров в заказе"""
        self.table.setRowCount(0)

        total_sum = 0
        for product in self.selected_products:
            item_total = product['price'] * product['quantity']
            total_sum += item_total

            row = self.table.rowCount()
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(product['article']))
            self.table.setItem(row, 1, QTableWidgetItem(product['name']))
            self.table.setItem(row, 2, QTableWidgetItem(str(product['quantity'])))
            self.table.setItem(row, 3, QTableWidgetItem(f"{product['price']:,.0f}"))
            self.table.setItem(row, 4, QTableWidgetItem(f"{item_total:,.0f}"))

        # Добавляем итоговую строку
        if self.selected_products:
            row = self.table.rowCount()
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(""))
            self.table.setItem(row, 1, QTableWidgetItem(""))
            self.table.setItem(row, 2, QTableWidgetItem(""))
            self.table.setItem(row, 3, QTableWidgetItem("ИТОГО:"))
            self.table.setItem(row, 4, QTableWidgetItem(f"{total_sum:,.0f} руб."))

            # Делаем итоговую строку невыбираемой
            for col in range(5):
                item = self.table.item(row, col)
                if item:
                    item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsSelectable)

        self.table.resizeColumnsToContents()

    def add_product(self):
        """Добавление товара в заказ"""
        # Диалог выбора товара
        dialog = SelectProductDialog(self.db, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            product = dialog.get_selected_product()

            if product:
                # Спрашиваем количество
                max_qty = product['stock']
                quantity, ok = QInputDialog.getInt(
                    self,
                    "Количество",
                    f"Введите количество для {product['name']}\n(максимум: {max_qty}):",
                    1, 1, max_qty
                )

                if ok and quantity > 0:
                    # Проверяем, нет ли уже такого товара
                    existing = None
                    for p in self.selected_products:
                        if p['product_id'] == product['product_id']:
                            existing = p
                            break

                    if existing:
                        existing['quantity'] += quantity
                    else:
                        self.selected_products.append({
                            'product_id': product['product_id'],
                            'article': product['article'],
                            'name': product['name'],
                            'quantity': quantity,
                            'price': product['price']
                        })

                    self.update_table()

    def remove_product(self):
        """Удаление выбранного товара из заказа"""
        current = self.table.currentRow()
        if current >= 0 and current < len(self.selected_products):
            self.selected_products.pop(current)
            self.update_table()
        else:
            QMessageBox.warning(self, "Ошибка", "Выберите товар для удаления")

    def change_quantity(self):
        """Изменение количества выбранного товара"""
        current = self.table.currentRow()
        if current >= 0 and current < len(self.selected_products):
            product = self.selected_products[current]

            new_quantity, ok = QInputDialog.getInt(
                self,
                "Изменить количество",
                f"Введите новое количество для {product['name']}:",
                product['quantity'], 1, 999
            )
            if ok:
                product['quantity'] = new_quantity
                self.update_table()
        else:
            QMessageBox.warning(self, "Ошибка", "Выберите товар для изменения")

    def load_data(self):
        # Загружаем статусы
        statuses = self.db.fetchall("SELECT * FROM statuses ORDER BY status_id")
        for status in statuses:
            self.status_cb.addItem(status['status_name'], status['status_id'])

        # Загружаем пункты выдачи
        pickups = self.db.fetchall("SELECT * FROM pickup_points ORDER BY pickup_point_id")
        for pickup in pickups:
            self.pickup_cb.addItem(pickup['address'], pickup['pickup_point_id'])

        # Если редактируем заказ
        if self.order is not None:
            # Устанавливаем статус
            for i in range(self.status_cb.count()):
                if self.status_cb.itemData(i) == self.order['status_id']:
                    self.status_cb.setCurrentIndex(i)
                    break

            # Устанавливаем пункт выдачи
            for i in range(self.pickup_cb.count()):
                if self.pickup_cb.itemData(i) == self.order['pickup_point_id']:
                    self.pickup_cb.setCurrentIndex(i)
                    break

            # Устанавливаем даты
            od = self.order['order_date']
            self.order_date.setDate(QDate(od.year, od.month, od.day))
            if self.order.get('delivery_date'):
                d = self.order['delivery_date']
                self.delivery_date.setDate(QDate(d.year, d.month, d.day))

            # Загружаем товары из order_items
            items = self.db.fetchall("""
                SELECT oi.*, p.article, p.name, p.price
                FROM order_items oi
                JOIN products p ON oi.product_id = p.product_id
                WHERE oi.order_id = %s
            """, (self.order['order_id'],))

            for item in items:
                self.selected_products.append({
                    'product_id': item['product_id'],
                    'article': item['article'],
                    'name': item['name'],
                    'quantity': item['quantity'],
                    'price': item['price_at_moment']
                })
            self.update_table()

    def save(self):
        status_id = self.status_cb.currentData()
        pickup_id = self.pickup_cb.currentData()
        order_date = self.order_date.date().toString("yyyy-MM-dd")
        delivery_date = self.delivery_date.date().toString("yyyy-MM-dd")

        if not self.selected_products:
            QMessageBox.warning(self, "Ошибка", "Добавьте товары в заказ")
            return

        if pickup_id is None:
            QMessageBox.warning(self, "Ошибка", "Выберите пункт выдачи")
            return

        if status_id is None:
            QMessageBox.warning(self, "Ошибка", "Выберите статус")
            return

        if self.order is None:
            # Новый заказ
            order_id = self.db.execute("""
                INSERT INTO orders(status_id, pickup_point_id, order_date, delivery_date, user_id)
                VALUES (%s, %s, %s, %s, %s)
            """, (status_id, pickup_id, order_date, delivery_date, self.user['user_id']))

            # Добавляем товары в order_items
            for product in self.selected_products:
                self.db.execute("""
                    INSERT INTO order_items(order_id, product_id, quantity, price_at_moment)
                    VALUES (%s, %s, %s, %s)
                """, (order_id, product['product_id'], product['quantity'], product['price']))

                # Уменьшаем остаток на складе
                self.db.execute("""
                    UPDATE products SET stock = stock - %s WHERE product_id = %s
                """, (product['quantity'], product['product_id']))

            QMessageBox.information(self, "Успех", f"Заказ №{order_id} успешно добавлен")
        else:
            # Редактирование заказа
            self.db.execute("""
                UPDATE orders
                SET status_id=%s, pickup_point_id=%s, order_date=%s, delivery_date=%s
                WHERE order_id=%s
            """, (status_id, pickup_id, order_date, delivery_date, self.order['order_id']))

            # Восстанавливаем остатки старых товаров
            old_items = self.db.fetchall("SELECT product_id, quantity FROM order_items WHERE order_id=%s", (self.order['order_id'],))
            for item in old_items:
                self.db.execute("UPDATE products SET stock = stock + %s WHERE product_id = %s", (item['quantity'], item['product_id']))

            # Удаляем старые товары
            self.db.execute("DELETE FROM order_items WHERE order_id=%s", (self.order['order_id'],))

            # Добавляем новые товары
            for product in self.selected_products:
                self.db.execute("""
                    INSERT INTO order_items(order_id, product_id, quantity, price_at_moment)
                    VALUES (%s, %s, %s, %s)
                """, (self.order['order_id'], product['product_id'], product['quantity'], product['price']))

                # Уменьшаем остаток
                self.db.execute("""
                    UPDATE products SET stock = stock - %s WHERE product_id = %s
                """, (product['quantity'], product['product_id']))

            QMessageBox.information(self, "Успех", f"Заказ №{self.order['order_id']} успешно обновлён")

        self.accept()


class SelectProductDialog(QDialog):
    """Диалог выбора товара"""
    def __init__(self, db, parent=None):
        super().__init__(parent)
        self.db = db
        self.selected_product = None
        self.setWindowTitle("Выбор товара")
        self.setModal(True)
        self.resize(600, 500)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        self.search_line = QLineEdit()
        self.search_line.setPlaceholderText("Поиск по артикулу или названию...")
        self.search_line.textChanged.connect(self.load_products)
        layout.addWidget(self.search_line)

        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Артикул", "Наименование", "Цена, руб.", "Остаток"])
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.itemDoubleClicked.connect(self.select_product)
        layout.addWidget(self.table)

        btn_layout = QHBoxLayout()
        select_btn = QPushButton("Выбрать")
        select_btn.clicked.connect(self.select_current)
        cancel_btn = QPushButton("Отмена")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(select_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)

        self.load_products()

    def load_products(self):
        search_text = self.search_line.text().strip()
        query = "SELECT product_id, article, name, price, stock FROM products WHERE stock > 0"
        params = []

        if search_text:
            query += " AND (article LIKE %s OR name LIKE %s)"
            params.append(f"%{search_text}%")
            params.append(f"%{search_text}%")

        query += " ORDER BY name"

        products = self.db.fetchall(query, params)

        self.table.setRowCount(0)
        for product in products:
            row = self.table.rowCount()
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(product['article']))
            self.table.setItem(row, 1, QTableWidgetItem(product['name']))
            self.table.setItem(row, 2, QTableWidgetItem(f"{product['price']:,.0f}"))
            self.table.setItem(row, 3, QTableWidgetItem(str(product['stock'])))

            self.table.item(row, 0).setData(Qt.ItemDataRole.UserRole, product['product_id'])

        self.table.resizeColumnsToContents()

    def select_product(self, item):
        row = item.row()
        product_id = self.table.item(row, 0).data(Qt.ItemDataRole.UserRole)
        self.selected_product = self.db.fetch_one("SELECT * FROM products WHERE product_id = %s", (product_id,))
        self.accept()

    def select_current(self):
        current = self.table.currentRow()
        if current >= 0:
            product_id = self.table.item(current, 0).data(Qt.ItemDataRole.UserRole)
            self.selected_product = self.db.fetch_one("SELECT * FROM products WHERE product_id = %s", (product_id,))
            self.accept()
        else:
            QMessageBox.warning(self, "Ошибка", "Выберите товар")

    def get_selected_product(self):
        return self.selected_product