# review.py (با استایل‌های جذاب و منطق Count-DOWN SRS)

import sqlite3
import random
from datetime import datetime, timedelta
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QFormLayout, QLabel, QSpinBox,
    QComboBox, QHBoxLayout, QPushButton, QGraphicsDropShadowEffect, QStackedLayout,
    QGraphicsOpacityEffect, QShortcut, QMessageBox
)
from PyQt5.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, pyqtSlot
from PyQt5.QtGui import QColor, QFont, QKeySequence

import os
import sys

# ... بقیه ایمپورت‌ها را دست نزنید

# این قسمت مسیر دیتابیس را برای حالت عادی و حالت PyInstaller تعریف می‌کند
if getattr(sys, 'frozen', False):
    # اگر برنامه در حالت EXE اجرا می‌شود، مسیر را از پوشه موقت PyInstaller بگیرید
    base_path = sys._MEIPASS
else:
    # اگر برنامه به صورت عادی اجرا می‌شود، مسیر فعلی فایل را بگیرید
    base_path = os.path.abspath(os.path.dirname(__file__))

DB_PATH = os.path.join(base_path, "flash cards.db")

# فواصل تکرار بر اساس روز (Days)
REVIEW_INTERVALS_DAYS = [1, 3, 7, 14, 30, 60, 120]

# **مقدار ثابت آستانه**: مقدار اولیه count و مقداری که count پس از ارتقاء به آن ریست می‌شود.
REVIEW_THRESHOLD = 5  # مقدار پیش‌فرض را 5 قرار دادم


# ======================= Database Layer =======================
class DatabaseManager:
    """مدیریت دیتابیس و منطق SRS"""

    def __init__(self):
        self.conn = sqlite3.connect(DB_PATH)
        self.cursor = self.conn.cursor()
        self.create_settings_table()  # ایجاد جدول تنظیمات

    # -------------------- متدهای جدید برای تنظیمات --------------------
    def create_settings_table(self):
        """ایجاد جدول 'settings' اگر وجود نداشته باشد."""
        # این جدول فقط یک ردیف برای ذخیره آخرین تنظیمات خواهد داشت
        self.cursor.execute("""
                            CREATE TABLE IF NOT EXISTS settings
                            (
                                id
                                INTEGER
                                PRIMARY
                                KEY,
                                num_cards
                                INTEGER,
                                show_time
                                INTEGER,
                                card_side
                                TEXT
                            )
                            """)
        self.conn.commit()

    def load_settings(self):
        """بارگذاری تنظیمات ذخیره‌شده یا بازگرداندن مقادیر پیش‌فرض."""
        self.cursor.execute("SELECT num_cards, show_time, card_side FROM settings WHERE id = 1")
        row = self.cursor.fetchone()

        # مقادیر پیش‌فرض
        default_settings = {
            'num_cards': 10,
            'show_time': 3,
            'card_side': "front"
        }

        if row:
            # اگر تنظیمات ذخیره‌شده وجود دارد
            return {
                'num_cards': row[0],
                'show_time': row[1],
                'card_side': row[2]
            }

        # اگر تنظیمات وجود ندارد، با پیش‌فرض شروع کن
        self.save_settings(default_settings['num_cards'], default_settings['show_time'], default_settings['card_side'])
        return default_settings

    def save_settings(self, num_cards, show_time, card_side):
        """ذخیره تنظیمات فعلی در دیتابیس."""
        # همیشه ردیف 1 را به‌روزرسانی/جایگزین می‌کند
        self.cursor.execute("""
            INSERT OR REPLACE INTO settings (id, num_cards, show_time, card_side)
            VALUES (1, ?, ?, ?)
        """, (num_cards, show_time, card_side))
        self.conn.commit()

    # ------------------------------------------------------------------

    def get_cards_for_review(self, num_cards):
        """
        بازیابی کارت‌ها برای مرور: کلماتی که تاریخ مرور آن‌ها گذشته یا امروز است.
        خروجی: (words, meaning, code, review_intervals, count, next_time_review)
        """
        today = datetime.now().strftime("%Y-%m-%d 23:59:59")

        query = """
                SELECT words, meaning, code, review_intervals, count, next_time_review
                FROM my_table
                WHERE next_time_review <= ? \
                   OR next_time_review IS NULL
                ORDER BY review_intervals ASC LIMIT ? \
                """
        self.cursor.execute(query, (today, num_cards,))
        return self.cursor.fetchall()

    def update_review_stats(self, code, current_interval, current_count):
        """
        **منطق SRS Count-down (کاهش شمارنده)**
        این متد تنها زمانی فراخوانی می‌شود که مرور موفق (Next) باشد.
        """
        try:
            current_interval = int(current_interval)
            current_count = int(current_count)

            final_interval = current_interval

            # 1. کاهش شمارنده
            new_count = current_count - 1

            # 2. بررسی شرط ارتقاء (اگر به 0 رسید)
            if new_count <= 0:

                # ارتقاء به پله بعدی
                if current_interval in REVIEW_INTERVALS_DAYS:
                    current_index = REVIEW_INTERVALS_DAYS.index(current_interval)
                    if current_index < len(REVIEW_INTERVALS_DAYS) - 1:
                        final_interval = REVIEW_INTERVALS_DAYS[current_index + 1]

                # ریست کردن شمارنده به مقدار آستانه
                new_count = REVIEW_THRESHOLD

                # 3. تعیین تاریخ تکرار بعدی (Time-based Scheduling)
            next_review_date = (datetime.now() + timedelta(days=final_interval)).strftime("%Y-%m-%d 00:00:00")

            # 4. به‌روزرسانی دیتابیس
            self.cursor.execute("""
                                UPDATE my_table
                                SET review_intervals = ?,
                                    count            = ?,
                                    next_time_review = ?
                                WHERE code = ?
                                """, (final_interval, new_count, next_review_date, code))
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Error updating review stats: {e}")
            return False

    def close(self):
        self.conn.close()


# ──────────────────────────────────────────────
# صفحه تنظیمات Review (با منطق ذخیره‌سازی اصلاح‌شده)
# ──────────────────────────────────────────────
class ReviewPage(QWidget):
    """صفحه‌ی Review (فرم تنظیمات)"""

    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.db = DatabaseManager()
        self.setup_ui()
        self.load_settings_to_ui()

    def load_settings_to_ui(self):
        """تنظیمات ذخیره‌شده را در فیلدهای فرم بارگذاری می‌کند."""
        settings = self.db.load_settings()
        self.num_cards.setValue(settings['num_cards'])
        self.show_time.setValue(settings['show_time'])
        self.card_side.setCurrentText(settings['card_side'])

    def setup_ui(self):
        self.setStyleSheet("background: transparent;")

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(40, 40, 40, 40)
        main_layout.setAlignment(Qt.AlignCenter)

        # ───── کانتینر مرکزی ─────
        center_container = QWidget()
        center_container.setStyleSheet("""
            QWidget {
                background-color: rgba(0, 0, 0, 150); /* Dark translucent background for container */
                border-radius: 20px;
                padding: 30px;
            }
        """)
        center_layout = QVBoxLayout(center_container)
        center_layout.setAlignment(Qt.AlignCenter)
        center_layout.setSpacing(15)

        title = QLabel("🃏 Review Settings")
        # **استایل تایتل جدید**
        title.setStyleSheet("font-size: 32px; font-weight: 800; color: #ADD8E6;")  # Light Blue
        title.setAlignment(Qt.AlignCenter)
        center_layout.addWidget(title)

        # استایل برای Labelها در فرم
        label_style = "color: #D3D3D3; font-size: 18px; font-weight: 600;"

        # **استایل جدید برای Captionها (بهبود یافته)**
        caption_style = "color: #B0C4DE; font-size: 15px; margin-top: 5px; font-weight: 400;"

        # استایل برای Inputها و SpinBoxها
        input_style = """
            QSpinBox, QComboBox {
                font-size: 18px; 
                padding: 8px 15px; 
                border-radius: 10px; 
                border: 2px solid #5F9EA0; /* Cadet Blue */
                color: white; 
                background-color: rgba(40, 40, 40, 0.9);
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox QAbstractItemView {
                background-color: rgba(50, 50, 50, 240);
                color: white;
                selection-background-color: #5F9EA0;
            }
        """

        form_widget = QWidget()
        form_widget.setStyleSheet("background: transparent;")
        form_layout = QFormLayout(form_widget)
        form_layout.setFormAlignment(Qt.AlignCenter)
        form_layout.setLabelAlignment(Qt.AlignLeft)
        form_layout.setSpacing(15)

        # === 1. تعداد کارت‌ها ===
        self.num_cards = QSpinBox()
        self.num_cards.setRange(1, 10000)
        self.num_cards.setFixedWidth(220)
        self.num_cards.setStyleSheet(input_style)

        num_cards_widget = QVBoxLayout()
        num_cards_widget.addWidget(self.num_cards)
        # کپشن بهبودیافته
        caption_num_cards = QLabel("Specify the maximum number of cards to be reviewed in this session.")
        caption_num_cards.setStyleSheet(caption_style)
        num_cards_widget.addWidget(caption_num_cards)

        form_layout.addRow(QLabel("Number of cards:").setStyleSheet(label_style), num_cards_widget)

        # === 2. زمان نمایش ===
        self.show_time = QSpinBox()
        self.show_time.setRange(0, 600)  # 0 برای حالت دستی
        self.show_time.setFixedWidth(220)
        self.show_time.setStyleSheet(input_style)
        self.show_time.setSuffix(" seconds (0=Manual)")

        show_time_widget = QVBoxLayout()
        show_time_widget.addWidget(self.show_time)
        # کپشن بهبودیافته
        caption_show_time = QLabel(
            "Set the display duration (in seconds) for the first side. **0** enables manual flipping.")
        caption_show_time.setStyleSheet(caption_style)
        show_time_widget.addWidget(caption_show_time)

        form_layout.addRow(QLabel("Show time:").setStyleSheet(label_style), show_time_widget)

        # === 3. سمت شروع ===
        self.card_side = QComboBox()
        self.card_side.addItems(["front", "back"])
        self.card_side.setFixedWidth(220)
        self.card_side.setStyleSheet(input_style)

        card_side_widget = QVBoxLayout()
        card_side_widget.addWidget(self.card_side)
        # کپشن بهبودیافته
        caption_card_side = QLabel(
            "Select the side that appears first (e.g., **front** for question, **back** for answer).")
        caption_card_side.setStyleSheet(caption_style)
        card_side_widget.addWidget(caption_card_side)

        form_layout.addRow(QLabel("Card side:").setStyleSheet(label_style), card_side_widget)
        center_layout.addWidget(form_widget)

        main_layout.addStretch(1)
        main_layout.addWidget(center_container)
        main_layout.addStretch(1)

        # ───── دکمه‌ها ─────
        bottom_layout = QHBoxLayout()

        # دکمه ذخیره
        save_btn = self.create_save_button()

        back_btn = self.create_back_button()
        start_btn = self.start_review_button()

        bottom_layout.addWidget(back_btn, alignment=Qt.AlignLeft)
        bottom_layout.addWidget(save_btn, alignment=Qt.AlignLeft)
        bottom_layout.addStretch(1)
        bottom_layout.addWidget(start_btn, alignment=Qt.AlignRight)
        main_layout.addLayout(bottom_layout)

    # متد ساخت دکمه ذخیره
    def create_save_button(self):
        btn = QPushButton("Save Settings")
        btn.setFixedSize(160, 50)
        btn.setStyleSheet("""
            QPushButton {
                font-size: 18px;
                font-weight: 600;
                color: #FFFFFF; 
                background-color: #5F9EA0; /* Cadet Blue */
                border: 1px solid #FFFFFF;
                border-radius: 10px;
                margin-left: 20px;
            }
            QPushButton:hover {
                background-color: #4682B4; /* Steel Blue */
            }
        """)
        btn.clicked.connect(self.save_settings)
        return btn

    # 🌟 جدید: متد خصوصی برای ذخیره تنظیمات بدون پیام
    def _save_settings_to_db(self):
        """مقادیر فیلدها را در دیتابیس ذخیره می‌کند (بدون نمایش پیام)."""
        num = self.num_cards.value()
        t = self.show_time.value()
        side = self.card_side.currentText()

        self.db.save_settings(num, t, side)

    # 🌟 متد ذخیره تنظیمات (فقط برای دکمه Save)
    def save_settings(self):
        """مقادیر فیلدها را در دیتابیس ذخیره کرده و پیام موفقیت نمایش می‌دهد."""
        self._save_settings_to_db()
        QMessageBox.information(self, "Settings Saved", "Review settings have been saved successfully!")

    def create_back_button(self):
        btn = QPushButton("← Back")
        btn.setFixedSize(140, 50)
        # **استایل جدید دکمه Back**
        btn.setStyleSheet("""
            QPushButton {
                font-size: 18px;
                font-weight: 600;
                color: #ADD8E6; /* Light Blue */
                background-color: rgba(0, 0, 0, 160);
                border: 1px solid #ADD8E6;
                border-radius: 10px;
            }
            QPushButton:hover {
                background-color: rgba(30, 144, 255, 100);
            }
        """)
        btn.clicked.connect(lambda: self.main_window.stack.setCurrentWidget(self.main_window.main_menu))
        return btn

    def start_review_button(self):
        btn = QPushButton("Start Review 🚀")
        btn.setFixedSize(200, 60)
        # **استایل جدید دکمه Start**
        btn.setStyleSheet("""
            QPushButton {
                font-size: 22px;
                font-weight: bold;
                color: white;
                background-color: #3CB371; /* Medium Sea Green */
                border: 3px solid white;
                border-radius: 15px;
            }
            QPushButton:hover {
                background-color: #2E8B57; /* Sea Green */
            }
            QPushButton:pressed {
                background-color: #256E4A;
            }
        """)
        btn.clicked.connect(self.start_review)
        return btn

    # 🌟 متد شروع مرور (بدون نمایش پیام)
    def start_review(self):
        # تنظیمات را بدون نمایش پیام ذخیره کن تا آخرین مقادیر استفاده شوند.
        self._save_settings_to_db()

        num = self.num_cards.value()
        t = self.show_time.value()
        side = self.card_side.currentText()

        page = CardViewerPage(self.main_window, num, t, side)
        self.main_window.stack.addWidget(page)
        self.main_window.stack.setCurrentWidget(page)


# ──────────────────────────────────────────────
# صفحه نمایش کارت‌ها
# ──────────────────────────────────────────────
class CardViewerPage(QWidget):
    def __init__(self, main_window, num_cards=50, show_time=3, side="front"):
        super().__init__()
        self.main_window = main_window
        self.num_cards = num_cards
        self.show_time = show_time
        self.side = side

        # کارت‌ها شامل: (word, meaning, code, interval, count, next_time_review)
        self.cards = []
        self.current_index = 0
        self.showing_front = (self.side == "front")
        self.db = DatabaseManager()

        # timer برای حالت اتوماتیک (تایمر اصلی نمایش سمت اول)
        self.main_timer = QTimer(self)
        self.main_timer.timeout.connect(self.flip_to_back_auto)

        # تایمر جدید برای نمایش سمت دوم یا نمایش 1 ثانیه‌ای بعد از next
        self.flip_timer = QTimer(self)
        self.flip_timer.timeout.connect(lambda: self._advance_card())

        # بارگذاری داده‌ها و ساخت UI
        self.load_cards()
        self.setup_ui()

        # اگر کارت وجود داشته باشه، شروع کن
        if self.cards:
            self.show_card()
            if self.show_time > 0:
                self.main_timer.start(self.show_time * 1000)
        else:
            QMessageBox.information(self, "No Cards", "No cards found for review. Returning to main menu.")
            self.main_window.stack.setCurrentWidget(self.main_window.main_menu)

    def load_cards(self):
        """خواندن کارت‌ها از دیتابیس (با تمام ستون‌های SRS)"""
        rows = self.db.get_cards_for_review(self.num_cards)

        if rows:
            if self.num_cards and self.num_cards < len(rows):
                rows = rows[: self.num_cards]
            random.shuffle(rows)
        self.cards = rows

    def setup_ui(self):
        # لایه‌بندی کلی
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(40, 40, 40, 40)
        main_layout.setAlignment(Qt.AlignCenter)

        # کانتینر وسط (برای مرکز کامل افقی+عمودی)
        center_container = QWidget()
        center_layout = QVBoxLayout(center_container)
        center_layout.setAlignment(Qt.AlignCenter)

        # ----------------- کارت انگلیسی (front) -----------------
        self.card_english = QLabel()
        self.card_english.setFixedSize(950, 525)
        self.card_english.setWordWrap(True)
        self.card_english.setAlignment(Qt.AlignCenter)
        # **استایل مدرن برای Front Card**
        self.card_english.setStyleSheet("""
            QLabel {
                background-color: qlineargradient(x1:0,y1:0,x2:1,y2:1,
                    stop:0 #4682B4, stop:1 #6495ED); /* Steel Blue to Cornflower Blue */
                border-radius: 25px;
                border: 4px solid #FFFFFF;
                color: #FFFFFF;
                font-size: 200px;
                font-weight: 900;
                padding: 20px;
                box-shadow: 0 10px 20px rgba(0, 0, 0, 0.5); /* Shadow for depth */
            }
        """)

        # ----------------- کارت فارسی (back) -----------------
        self.card_farsi = QLabel()
        self.card_farsi.setFixedSize(950, 525)
        self.card_farsi.setWordWrap(True)
        self.card_farsi.setAlignment(Qt.AlignCenter)
        # **استایل مدرن برای Back Card**
        self.card_farsi.setStyleSheet("""
            QLabel {
                background-color: qlineargradient(x1:1,y1:0,x2:0,y2:1,
                    stop:0 #FF8C00, stop:1 #FFA07A); /* Dark Orange to Light Salmon */
                border-radius: 25px;
                border: 4px solid #FFFFFF;
                color: #000000;
                font-size: 200px;
                font-weight: 900;
                padding: 20px;
                box-shadow: 0 10px 20px rgba(0, 0, 0, 0.5);
            }
        """)

        # برچسب اطلاعات SRS
        self.stats_label = QLabel()
        self.stats_label.setAlignment(Qt.AlignCenter)
        # **استایل جدید برای Stats Label**
        self.stats_label.setStyleSheet(
            "color: #ADD8E6; font-size: 18px; font-weight: 600; margin-top: 15px; background: rgba(0, 0, 0, 100); padding: 5px 15px; border-radius: 8px;")

        # افکت‌های شفافیت
        self.effect_english = QGraphicsOpacityEffect(self.card_english)
        self.effect_english.setOpacity(1.0)
        self.card_english.setGraphicsEffect(self.effect_english)

        self.effect_farsi = QGraphicsOpacityEffect(self.card_farsi)
        self.effect_farsi.setOpacity(0.0)
        self.card_farsi.setGraphicsEffect(self.effect_farsi)

        # QStackedLayout برای پشته کارت‌ها
        self.stack = QStackedLayout()
        self.stack.addWidget(self.card_english)
        self.stack.addWidget(self.card_farsi)

        center_layout.addLayout(self.stack)
        center_layout.addWidget(self.stats_label, alignment=Qt.AlignCenter)
        main_layout.addWidget(center_container, alignment=Qt.AlignCenter)

        # دکمه‌ها پایین صفحه
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(25)
        btn_layout.setAlignment(Qt.AlignCenter)

        self.back_btn = QPushButton("← Back (Esc)")
        self.flip_btn = QPushButton("Flip (F)")
        self.next_btn = QPushButton("Next (N)")
        self.pause_btn = QPushButton("Pause (P)")

        # **استایل‌های جدید برای دکمه‌های کنترلی**
        button_base_style = """
            QPushButton {
                font-size: 20px;
                font-weight: bold;
                color: white;
                border-radius: 12px;
                border: 2px solid white;
                padding: 10px 20px;
                min-width: 150px;
            }
            QPushButton:hover {
                border: 2px solid #ADD8E6;
                color: #ADD8E6;
            }
        """

        # Back Button Specific Style
        self.back_btn.setStyleSheet(button_base_style + """
            QPushButton { background-color: rgba(105, 105, 105, 180); } /* Dim Gray */
            QPushButton:hover { background-color: rgba(169, 169, 169, 180); } /* Dark Gray */
        """)

        # Flip Button Specific Style
        self.flip_btn.setStyleSheet(button_base_style + """
            QPushButton { background-color: rgba(255, 165, 0, 180); } /* Orange */
            QPushButton:hover { background-color: rgba(255, 140, 0, 220); } /* Darker Orange */
        """)

        # Next Button Specific Style (Success/Progress)
        self.next_btn.setStyleSheet(button_base_style + """
            QPushButton { background-color: rgba(60, 179, 113, 180); } /* Medium Sea Green */
            QPushButton:hover { background-color: rgba(46, 139, 87, 220); } /* Sea Green */
        """)

        # Pause Button Specific Style
        self.pause_btn.setStyleSheet(button_base_style + """
            QPushButton { background-color: rgba(255, 99, 71, 180); } /* Tomato */
            QPushButton:hover { background-color: rgba(205, 92, 92, 220); } /* Indian Red */
        """)

        for btn in (self.back_btn, self.flip_btn, self.next_btn, self.pause_btn):
            btn.setFixedSize(190, 65)
            btn_layout.addWidget(btn)

        main_layout.addSpacing(25)
        main_layout.addLayout(btn_layout)

        # اتصال سیگنال‌ها
        self.back_btn.clicked.connect(self.go_back_to_menu)
        self.flip_btn.clicked.connect(self.flip_card)
        self.next_btn.clicked.connect(lambda: self.next_card(from_timer=False))
        self.pause_btn.clicked.connect(self.toggle_timer)

        # افزودن میان‌برهای صفحه‌کلید
        self.add_shortcuts()

    def go_back_to_menu(self):
        self.main_timer.stop()
        self.flip_timer.stop()
        self.main_window.stack.setCurrentWidget(self.main_window.main_menu)

    def add_shortcuts(self):
        """تعریف و اتصال میان‌برهای صفحه‌کلید"""

        QShortcut(QKeySequence(Qt.Key_Escape), self).activated.connect(self.go_back_to_menu)
        QShortcut(QKeySequence(Qt.Key_F), self).activated.connect(self.flip_card)
        QShortcut(QKeySequence(Qt.Key_N), self).activated.connect(lambda: self.next_card(from_timer=False))
        QShortcut(QKeySequence(Qt.Key_P), self).activated.connect(self.toggle_timer)

    def show_card(self):
        """نمایش متن، جهت‌دهی و اطلاعات SRS."""
        if not self.cards:
            self.card_english.setText("No cards found.")
            self.card_farsi.setText("")
            self.stats_label.setText("")
            return

        # استخراج ۶ ستون
        word, meaning, code, interval, count, next_time_review = self.cards[self.current_index]

        # محتوا و جهت‌دهی
        self.card_english.setText(word)
        self.card_english.setLayoutDirection(Qt.LeftToRight)

        self.card_farsi.setText(meaning)
        self.card_farsi.setLayoutDirection(Qt.RightToLeft)

        # نمایش بر اساس وضعیت فعلی
        if self.showing_front:
            self.stack.setCurrentWidget(self.card_english)
            self.effect_english.setOpacity(1.0)
            self.effect_farsi.setOpacity(0.0)
        else:
            self.stack.setCurrentWidget(self.card_farsi)
            self.effect_english.setOpacity(0.0)
            self.effect_farsi.setOpacity(1.0)

        # نمایش اطلاعات SRS
        next_review_display = "Review Today"
        if next_time_review and next_time_review != 'None':
            next_review_display = f"Next Due: {next_time_review.split()[0]}"

        # نمایش Progress بر اساس REVIEW_THRESHOLD (Count-down)
        self.stats_label.setText(
            f"Card {self.current_index + 1}/{len(self.cards)} | Interval: {interval} days | Successes Remaining: {count}/{REVIEW_THRESHOLD} | {next_review_display}"
        )

    def flip_card(self):
        """انیمیشن هم‌زمان fade out کارت فعلی و fade in کارت بعدی."""
        if not self.cards:
            return

        # ... کدهای انیمیشن
        if self.showing_front:
            current_effect = self.effect_english
            next_effect = self.effect_farsi
            next_widget = self.card_farsi
        else:
            current_effect = self.effect_farsi
            next_effect = self.effect_english
            next_widget = self.card_english

        next_widget.show()
        next_effect.setOpacity(0.0)
        self.stack.setCurrentWidget(next_widget)

        fade_out = QPropertyAnimation(current_effect, b"opacity", self)
        fade_out.setDuration(320)
        fade_out.setStartValue(1.0)
        fade_out.setEndValue(0.0)

        fade_in = QPropertyAnimation(next_effect, b"opacity", self)
        fade_in.setDuration(320)
        fade_in.setStartValue(0.0)
        fade_in.setEndValue(1.0)

        fade_out.start()
        fade_in.start()

        self.showing_front = not self.showing_front
        self.show_card()

    @pyqtSlot()
    def flip_to_back_auto(self):
        """در حالت خودکار، کارت را به سمت دیگر (پشتی) برمی‌گرداند یا به کارت بعدی می‌رود."""

        # اگر در حال نمایش سمت اول هستیم (بر اساس تنظیمات) Flip کن
        if self.showing_front == (self.side == "front"):
            self.main_timer.stop()
            self.flip_card()
            self.flip_timer.start(self.show_time * 1000)
        else:
            # اگر در سمت دوم هستیم (و تایمر تمام شده): مرور موفق نبوده، فقط برو به کارت بعدی.
            self.main_timer.stop()
            self.flip_timer.stop()
            self._advance_card()  # بدون به روز رسانی دیتابیس

    def next_card(self, from_timer=False):
        """
        هندل کردن فشار دکمه Next (N) توسط کاربر:
        1. به‌روزرسانی آمار SRS (کاهش count).
        2. حرکت به کارت بعدی.
        """
        if not self.cards:
            return

        # 1. اگر کاربر دکمه Next را در حالی که سمت اول کارت نمایش داده می‌شود، بزند:
        if not from_timer and self.showing_front == (self.side == "front"):
            self.main_timer.stop()
            self.flip_card()  # فلپ به سمت دوم (پیش‌نمایش سریع)

            # --- به‌روزرسانی دیتابیس در اینجا (چون Next زده شده = مرور موفق)
            word, meaning, code, current_interval, current_count, last_review_time = self.cards[self.current_index]
            self.db.update_review_stats(code, current_interval, current_count)

            # به‌روزرسانی لیست داخلی (Fetch مجدد) برای نمایش آمار جدید در کارت بعدی
            new_data = self.db.cursor.execute("""
                                              SELECT words, meaning, code, review_intervals, count, next_time_review
                                              FROM my_table
                                              WHERE code = ?
                                              """, (code,)).fetchone()
            if new_data:
                self.cards[self.current_index] = new_data
            # -------------------------------------------------------------------

            self.flip_timer.stop()
            self.flip_timer.start(1000)  # تایمر 1 ثانیه‌ای برای رفتن به کارت بعدی

            return

        # 2. اگر next از تایمر 1 ثانیه‌ای آمده یا کاربر در حال نمایش سمت دوم next زده:
        self._advance_card()

    def _advance_card(self):
        """
        فقط حرکت به کارت بعدی. این متد آمار SRS را دستکاری نمی‌کند.
        اگر به انتهای لیست رسید، به منوی اصلی برگردد.
        """
        if not self.cards:
            return

        # برو به کارت بعدی
        next_index = self.current_index + 1

        # توقف تایمرها
        self.main_timer.stop()
        self.flip_timer.stop()

        if next_index >= len(self.cards):
            # اتمام مرور
            QMessageBox.information(self, "Review Complete",
                                    f"Review session for {len(self.cards)} cards has been completed! Returning to main menu.")
            self.go_back_to_menu()
            return

        self.current_index = next_index

        # وقتی کارت بعدی میاد، از تنظیم اولیه side پیروی کن
        self.showing_front = (self.side == "front")
        self.show_card()

        # شروع تایمر برای کارت جدید اگر در حالت اتوماتیک هستیم
        if self.show_time > 0 and self.pause_btn.text() == "Pause (P)":
            self.main_timer.start(self.show_time * 1000)

    def toggle_timer(self):
        """تغییر وضعیت مکث/ادامه برای هر دو تایمر."""
        if self.main_timer.isActive() or self.flip_timer.isActive():
            self.main_timer.stop()
            self.flip_timer.stop()
            self.pause_btn.setText("Resume (P)")
        else:
            if self.cards and self.show_time > 0:
                self.main_timer.start(self.show_time * 1000)
                self.pause_btn.setText("Pause (P)")