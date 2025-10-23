# edit.py - با قابلیت نمایش تمام رکوردها (Show All)

import sqlite3
import random
import string
from datetime import datetime
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QHBoxLayout,
    QTableWidget, QTableWidgetItem, QMessageBox, QSpinBox, QStackedLayout
)
from PyQt5.QtCore import Qt

DB_PATH = "flash cards.db"


# ======================= Database Layer =======================
class DatabaseManager:
    """مدیریت دیتابیس"""

    def __init__(self):
        self.conn = sqlite3.connect(DB_PATH)
        self.cursor = self.conn.cursor()

    def add_word(self, word, meaning, initial_count):
        """افزودن کلمه جدید با کد منحصر به فرد"""
        code = self._generate_unique_code()
        # تاریخ شروع: تاریخ امروز
        next_review_date = (datetime.now()).strftime("%Y-%m-%d 00:00:00")
        try:
            # کلمه جدید با review_intervals=1 و count اولیه
            self.cursor.execute("""
                                INSERT INTO my_table (code, words, meaning, review_intervals, count, last_time_review)
                                VALUES (?, ?, ?, ?, ?, ?)
                                """, (code, word, meaning, 1, initial_count, next_review_date))
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False

    def _generate_unique_code(self):
        """تولید کد منحصر به‌فرد که در دیتابیس تکراری نباشد"""
        while True:
            code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
            self.cursor.execute("SELECT code FROM my_table WHERE code = ?", (code,))
            if not self.cursor.fetchone():
                return code

    def search_words(self, query):
        """جستجوی کلمه یا معنی"""
        q = f"%{query.lower()}%"
        self.cursor.execute("""
                            SELECT code, words, meaning, review_intervals, count, last_time_review
                            FROM my_table
                            WHERE LOWER(words) LIKE ?
                               OR LOWER(meaning) LIKE ?
                            """, (q, q))
        return self.cursor.fetchall()

    def get_all_words(self):
        """**تابع جدید:** دریافت تمام رکوردها از دیتابیس"""
        self.cursor.execute("""
                            SELECT code, words, meaning, review_intervals, count, last_time_review
                            FROM my_table
                            ORDER BY code
                            """)
        return self.cursor.fetchall()

    def update_word(self, code, word, meaning, interval, count, last_time):
        """به‌روزرسانی رکورد"""
        self.cursor.execute("""
                            UPDATE my_table
                            SET words            = ?,
                                meaning          = ?,
                                review_intervals = ?,
                                count            = ?,
                                last_time_review = ?
                            WHERE code = ?
                            """, (word, meaning, interval, count, last_time, code))
        self.conn.commit()

    def delete_word(self, code):
        """حذف رکورد"""
        self.cursor.execute("DELETE FROM my_table WHERE code = ?", (code,))
        self.conn.commit()

    def close(self):
        self.conn.close()


# ======================= Add Word Page (بدون تغییر) =======================
class AddWordPage(QWidget):
    """صفحه افزودن کلمه جدید"""

    def __init__(self, edit_menu_owner, main_window):
        super().__init__()
        self.owner = edit_menu_owner
        self.main_window = main_window
        self.db = DatabaseManager()

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(20)

        title = QLabel("Add New Word")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 26px; font-weight: 800; color: #ADD8E6; text-shadow: 1px 1px 3px black;")
        layout.addWidget(title)

        self.word_input = QLineEdit()
        self.word_input.setPlaceholderText("English word...")
        self.meaning_input = QLineEdit()
        self.meaning_input.setPlaceholderText("Persian meaning...")

        self.count_spin = QSpinBox()
        self.count_spin.setRange(0, 1000)

        try:
            from review import REVIEW_THRESHOLD
            self.count_spin.setValue(REVIEW_THRESHOLD)
            self.count_spin.setPrefix(f"Initial Count (Next is {REVIEW_THRESHOLD}): ")
        except ImportError:
            self.count_spin.setValue(5)
            self.count_spin.setPrefix("Initial Count: ")

        input_style = """
            QLineEdit, QSpinBox {
                background-color: rgba(40, 40, 40, 0.85);
                color: #F0F0F0;
                padding: 10px;
                border-radius: 5px;
                border: 1px solid rgba(100, 100, 100, 0.5);
                font-size: 16px;
            }
        """
        for box in [self.word_input, self.meaning_input]:
            box.setFixedWidth(350)
            box.setStyleSheet(input_style)
            layout.addWidget(box, alignment=Qt.AlignCenter)

        self.count_spin.setFixedWidth(350)
        self.count_spin.setStyleSheet(input_style)
        layout.addWidget(self.count_spin, alignment=Qt.AlignCenter)

        self.add_button = QPushButton("Add Word")
        self.add_button.setFixedSize(180, 50)
        self.add_button.setStyleSheet("""
            QPushButton {
                background-color: rgba(60, 179, 113, 0.9);
                color: white;
                font-size: 18px;
                border-radius: 15px;
                font-weight: bold;
                padding: 10px 20px;
                border: 1px solid white;
            }
            QPushButton:hover {
                background-color: rgba(46, 139, 87, 1);
            }
        """)
        layout.addWidget(self.add_button, alignment=Qt.AlignCenter)

        self.back_button = QPushButton("← Back")
        self.back_button.setFixedSize(140, 40)
        self.back_button.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #A9A9A9;
                font-size: 16px;
                border: none;
                font-weight: bold;
                padding: 5px;
            }
            QPushButton:hover {
                color: white;
                text-decoration: underline;
            }
        """)
        layout.addWidget(self.back_button, alignment=Qt.AlignCenter)

        self.add_button.clicked.connect(self.add_word)
        self.back_button.clicked.connect(self.go_back_to_menu)

    def add_word(self):
        """افزودن کلمه جدید به دیتابیس"""
        word = self.word_input.text().strip()
        meaning = self.meaning_input.text().strip()
        initial_count = self.count_spin.value()

        if not word or not meaning:
            QMessageBox.warning(self, "Warning", "Please enter both English word and Persian meaning.")
            return

        success = self.db.add_word(word, meaning, initial_count)
        if success:
            QMessageBox.information(self, "Success", "Word added successfully!")
            self.word_input.clear()
            self.meaning_input.clear()
            try:
                from review import REVIEW_THRESHOLD
                self.count_spin.setValue(REVIEW_THRESHOLD)
            except ImportError:
                self.count_spin.setValue(5)

            if hasattr(self.owner, "edit_page"):
                # ریست کردن جدول جستجو پس از افزودن (به جای حذف)
                self.owner.edit_page.table.setRowCount(0)
        else:
            QMessageBox.critical(self, "Error", "Failed to add word (possible DB issue).")

    def go_back_to_menu(self):
        """بازگشت به منوی درون EditMainMenu یا منوی اصلی"""
        if hasattr(self.owner, "stack") and hasattr(self.owner, "menu_page"):
            try:
                self.owner.stack.setCurrentWidget(self.owner.menu_page)
                return
            except Exception:
                pass
        if hasattr(self.main_window, "stack") and hasattr(self.main_window, "main_menu"):
            self.main_window.stack.setCurrentWidget(self.main_window.main_menu)


# ======================= Edit / Remove Page =======================
class EditRemovePage(QWidget):
    """صفحه جستجو، ویرایش و حذف"""

    def __init__(self, edit_menu_owner, main_window):
        super().__init__()
        self.owner = edit_menu_owner
        self.main_window = main_window
        self.db = DatabaseManager()

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignTop)
        layout.setSpacing(10)

        title = QLabel("Edit / Remove Words")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 26px; font-weight: 800; color: #ADD8E6; text-shadow: 1px 1px 3px black;")
        layout.addWidget(title)

        # ----------------- نوار جستجو و دکمه‌ها -----------------
        control_layout = QHBoxLayout()
        control_layout.setSpacing(10)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search by word or meaning...")
        self.search_input.setStyleSheet("""
            QLineEdit {
                background-color: rgba(40, 40, 40, 0.85);
                color: #F0F0F0;
                padding: 8px;
                border-radius: 5px;
                border: 1px solid rgba(100, 100, 100, 0.5);
                font-size: 16px;
            }
        """)

        self.search_button = QPushButton("Search")
        self.show_all_button = QPushButton("Show All")  # **دکمه جدید**

        button_style = """
            QPushButton {
                background-color: rgba(30, 144, 255, 0.9);
                color: white;
                font-size: 16px;
                border-radius: 5px;
                font-weight: bold;
                padding: 8px 15px;
                border: 1px solid white;
            }
            QPushButton:hover {
                background-color: rgba(70, 130, 180, 1);
            }
        """
        self.search_button.setStyleSheet(button_style)
        self.show_all_button.setStyleSheet(button_style.replace("30, 144, 255", "95, 158, 160"))  # Cadet Blue

        control_layout.addWidget(self.search_input)
        control_layout.addWidget(self.search_button)
        control_layout.addWidget(self.show_all_button)  # **اضافه شدن به نوار کنترل**
        layout.addLayout(control_layout)
        # ----------------------------------------------------

        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["Code", "Word", "Meaning", "Interval", "Count", "Last Review"])

        self.table.setStyleSheet("""
            QTableWidget {
                background-color: rgba(30, 30, 30, 0.8);
                color: #F0F0F0;
                border: 1px solid rgba(255, 255, 255, 0.2);
                gridline-color: rgba(255, 255, 255, 0.1);
                font-size: 14px;
                selection-background-color: rgba(0, 150, 255, 0.5);
                alternate-background-color: rgba(25, 25, 25, 0.8);
            }
            QHeaderView::section {
                background-color: rgba(50, 50, 50, 1);
                color: white;
                padding: 5px;
                border: 1px solid rgba(255, 255, 255, 0.3);
                font-weight: bold;
                font-size: 15px;
            }
            QTableWidget::item {
                padding: 5px;
            }
        """)
        layout.addWidget(self.table)

        btn_layout = QHBoxLayout()
        self.edit_button = QPushButton("Apply Changes")
        self.delete_button = QPushButton("Delete Selected")
        self.back_button = QPushButton("← Back")

        self.edit_button.setStyleSheet("""
            QPushButton {
                background-color: rgba(30, 144, 255, 0.9);
                color: white;
                font-size: 16px;
                border-radius: 10px;
                font-weight: bold;
                padding: 8px;
            }
            QPushButton:hover {
                background-color: rgba(70, 130, 180, 1);
            }
        """)

        self.delete_button.setStyleSheet("""
            QPushButton {
                background-color: rgba(220, 20, 60, 0.9);
                color: white;
                font-size: 16px;
                border-radius: 10px;
                font-weight: bold;
                padding: 8px;
            }
            QPushButton:hover {
                background-color: rgba(180, 0, 40, 1);
            }
        """)

        self.back_button.setStyleSheet("""
            QPushButton {
                background-color: rgba(100, 100, 100, 0.7);
                color: white;
                font-size: 16px;
                border-radius: 10px;
                font-weight: bold;
                padding: 8px;
            }
            QPushButton:hover {
                background-color: rgba(150, 150, 150, 0.9);
            }
        """)

        btn_layout.addWidget(self.edit_button)
        btn_layout.addWidget(self.delete_button)
        btn_layout.addWidget(self.back_button)
        layout.addLayout(btn_layout)

        # ----------------- اتصال سیگنال‌ها -----------------
        self.search_button.clicked.connect(self.perform_search)
        self.show_all_button.clicked.connect(self.show_all_records)  # **اتصال جدید**
        self.edit_button.clicked.connect(self.apply_changes)
        self.delete_button.clicked.connect(self.delete_selected)
        self.back_button.clicked.connect(self.go_back_to_menu)

    def populate_table(self, records):
        """تابع کمکی برای پر کردن جدول با لیست رکوردها"""
        self.table.setRowCount(len(records))
        for row_idx, row_data in enumerate(records):
            for col_idx, value in enumerate(row_data):
                item = QTableWidgetItem(str(value) if value is not None else "")
                if col_idx == 0:
                    item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
                else:
                    item.setFlags(item.flags() | Qt.ItemIsEditable)
                self.table.setItem(row_idx, col_idx, item)

        if not records:
            QMessageBox.information(self, "No Records", "No matching records found in the database.")

    def perform_search(self):
        query = self.search_input.text().strip()
        if not query:
            QMessageBox.warning(self, "Warning", "Please enter a search term.")
            return

        results = self.db.search_words(query)
        self.populate_table(results)

    def show_all_records(self):
        """نمایش تمام رکوردها در جدول"""
        self.search_input.clear()  # پاک کردن فیلد جستجو
        all_records = self.db.get_all_words()
        self.populate_table(all_records)

    def apply_changes(self):
        row_count = self.table.rowCount()
        for row in range(row_count):
            code = self.table.item(row, 0).text()
            word = self.table.item(row, 1).text()
            meaning = self.table.item(row, 2).text()
            interval = self.table.item(row, 3).text()
            count = self.table.item(row, 4).text()
            last_time = self.table.item(row, 5).text()

            try:
                self.db.update_word(code, word, meaning, interval, count, last_time)
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to update record: {e}")
                return

        QMessageBox.information(self, "Success", "All changes saved successfully!")

    def delete_selected(self):
        row = self.table.currentRow()
        if row == -1:
            QMessageBox.warning(self, "Warning", "Please select a record to delete.")
            return

        code = self.table.item(row, 0).text()
        confirm = QMessageBox.question(self, "Confirm", f"Delete word with code {code}?",
                                       QMessageBox.Yes | QMessageBox.No)
        if confirm == QMessageBox.Yes:
            try:
                self.db.delete_word(code)
                self.table.removeRow(row)
                QMessageBox.information(self, "Deleted", "Record deleted successfully.")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to delete record: {e}")

    def go_back_to_menu(self):
        if hasattr(self.owner, "stack") and hasattr(self.owner, "menu_page"):
            try:
                self.owner.stack.setCurrentWidget(self.owner.menu_page)
                return
            except Exception:
                pass
        if hasattr(self.main_window, "stack") and hasattr(self.main_window, "main_menu"):
            self.main_window.stack.setCurrentWidget(self.main_window.main_menu)


# ======================= Menu Page (Switcher) (بدون تغییر) =======================
class EditMainMenu(QWidget):
    """صفحه انتخاب Add یا Edit"""

    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window

        self.stack = QStackedLayout(self)
        self.menu_page = QWidget()
        layout = QVBoxLayout(self.menu_page)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(25)
        self.menu_page.setStyleSheet("background: transparent;")

        title = QLabel("Word Management")
        title.setStyleSheet("font-size: 24px; font-weight: 800; color: #ADD8E6; text-shadow: 1px 1px 3px black;")
        layout.addWidget(title, alignment=Qt.AlignCenter)

        self.add_btn = QPushButton("➕ Add New Word")
        self.edit_btn = QPushButton("✏️ Edit / Remove")
        self.back_btn = QPushButton("← Back to Main Menu")

        for btn in [self.add_btn, self.edit_btn]:
            btn.setFixedSize(220, 60)
            btn.setStyleSheet("""
                QPushButton {
                    font-size: 20px;
                    font-weight: bold;
                    color: #FFFFFF;
                    background-color: rgba(0, 0, 0, 180);
                    border: 2px solid #5F9EA0;
                    border-radius: 15px;
                }
                QPushButton:hover {
                    background-color: rgba(95, 158, 160, 200);
                    color: black;
                }
            """)
            layout.addWidget(btn, alignment=Qt.AlignCenter)

        self.back_btn.setFixedSize(220, 60)
        self.back_btn.setStyleSheet("""
            QPushButton {
                font-size: 18px;
                font-weight: bold;
                color: #A9A9A9;
                background-color: rgba(0, 0, 0, 140);
                border: 1px solid rgba(255, 255, 255, 0.3);
                border-radius: 12px;
            }
            QPushButton:hover {
                background-color: rgba(50, 50, 50, 160);
                color: white;
            }
        """)
        layout.addWidget(self.back_btn, alignment=Qt.AlignCenter)

        self.add_page = AddWordPage(self, self.main_window)
        self.edit_page = EditRemovePage(self, self.main_window)

        self.stack.addWidget(self.menu_page)
        self.stack.addWidget(self.add_page)
        self.stack.addWidget(self.edit_page)

        self.add_btn.clicked.connect(lambda: self.stack.setCurrentWidget(self.add_page))
        self.edit_btn.clicked.connect(lambda: self.stack.setCurrentWidget(self.edit_page))
        self.back_btn.clicked.connect(lambda: self.main_window.stack.setCurrentWidget(self.main_window.main_menu))