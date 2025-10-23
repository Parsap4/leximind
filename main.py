# main.py - کد نهایی با تاریخ و دکمه About فقط در منوی اصلی

import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QPushButton, QVBoxLayout, QStackedWidget,
    QHBoxLayout, QDialog, QLabel, QTextEdit, QGridLayout
)
from PyQt5.QtCore import Qt, QDate
from background import AnimatedBackground
from review import ReviewPage
from edit import EditMainMenu
from edit import AddWordPage, EditRemovePage


# ------------------------------------------------------------------
# **کلاس پنجره About (بدون تغییر)**
# ------------------------------------------------------------------
class AboutDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("About Flash Card App")
        self.resize(500, 350)

        self.setStyleSheet("""
            QDialog {
                background-color: #2e2e2e;
                border: 2px solid #5F9EA0;
                border-radius: 10px;
            }
            QLabel, QTextEdit {
                color: #ADD8E6;
                font-size: 16px;
                background: transparent;
                border: none;
            }
            QTextEdit {
                font-size: 14px;
                padding: 10px;
                background-color: rgba(0, 0, 0, 100);
                border-radius: 5px;
            }
            QPushButton {
                background-color: #5F9EA0;
                color: white;
                border-radius: 8px;
                padding: 8px 15px;
            }
            QPushButton:hover {
                background-color: #778899;
            }
        """)

        layout = QVBoxLayout(self)

        title = QLabel("Flash Card Learning App")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #ADD8E6;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        about_text = """
        **[English]**
        This application helps you memorize vocabulary using the **Spaced Repetition System (SRS)** logic. You can add new words, review old ones, and track your progress through the interval/count system.

        **How it works (Count-Down SRS):**
        1. **Review:** Shows cards due today.
        2. **Next (N):** If you remember a word, its success counter (Count) decreases by 1.
        3. **Promotion:** When the Count reaches zero, the review interval increases (e.g., from 1 day to 3 days), and the Count resets to the threshold (e.g., 5).

        ---

        **[فارسی]**
        این برنامه به شما کمک می‌کند تا واژگان را با استفاده از منطق **سیستم تکرار با فاصله‌ (SRS)** حفظ کنید. می‌توانید کلمات جدید اضافه کنید، کلمات قدیمی را مرور کنید و پیشرفت خود را از طریق سیستم فاصله/شمارش ردیابی کنید.

        **نحوه کار (Count-Down SRS):**
        ۱. **مرور:** کارت‌هایی که تاریخ مرور آن‌ها فرا رسیده را نمایش می‌دهد.
        ۲. **بعدی (N):** اگر کلمه‌ای را به یاد آورید، شمارنده موفقیت (Count) آن ۱ واحد کاهش می‌یابد.
        ۳. **ارتقاء:** زمانی که شمارنده به صفر برسد، فاصله تکرار افزایش می‌یابد (مثلاً از ۱ روز به ۳ روز) و شمارنده به آستانه (مثلاً ۵) ریست می‌شود.
        """

        text_widget = QTextEdit()
        text_widget.setReadOnly(True)
        text_widget.setText(about_text)
        layout.addWidget(text_widget)

        close_button = QPushButton("Close")
        close_button.clicked.connect(self.accept)
        layout.addWidget(close_button, alignment=Qt.AlignCenter)


# ------------------------------------------------------------------


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Flash Card App")
        self.resize(900, 600)

        # پس‌زمینه متحرک
        self.bg = AnimatedBackground(self, count=35)
        self.bg.setGeometry(0, 0, self.width(), self.height())
        self.bg.lower()

        # استک صفحات
        self.stack = QStackedWidget(self)
        self.main_menu = QWidget()
        self.main_menu.setStyleSheet("background: transparent;")
        self.stack.addWidget(self.main_menu)

        self.review_page = None
        self.edit_menu = EditMainMenu(self)
        self.stack.addWidget(self.edit_menu)

        # تنظیم منوی اصلی (شامل دکمه‌ها، تاریخ و About)
        self.setup_main_menu()

        # لایه اصلی MainWindow فقط شامل Stack است
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.stack)
        self.setLayout(layout)
        self.stack.raise_()

    def resizeEvent(self, event):
        self.bg.setGeometry(0, 0, self.width(), self.height())
        super().resizeEvent(event)

    def setup_main_menu(self):
        # از QGridLayout برای قرار دادن اجزا در گوشه‌ها استفاده می‌کنیم
        menu_layout = QGridLayout(self.main_menu)
        menu_layout.setContentsMargins(20, 20, 20, 20)

        # -------------------- ۱. واترمارک تاریخ (گوشه بالا راست) --------------------
        date_label = QLabel(QDate.currentDate().toString("yyyy-MM-dd"))
        date_label.setStyleSheet("color: rgba(255, 255, 255, 120); font-size: 16px; font-weight: bold;")
        date_label.setAlignment(Qt.AlignTop | Qt.AlignRight)

        # اضافه کردن در ردیف 0، ستون 2 (بالا راست)
        menu_layout.addWidget(date_label, 0, 2, 1, 1, alignment=Qt.AlignTop | Qt.AlignRight)

        # -------------------- ۲. دکمه About (گوشه پایین چپ) --------------------
        about_btn = QPushButton("ⓘ About")
        about_btn.setFixedSize(120, 40)
        about_btn.setStyleSheet("""
            QPushButton {
                font-size: 18px;
                font-weight: 500;
                color: #ADD8E6;
                background-color: rgba(0, 0, 0, 160);
                border: 1px solid #ADD8E6;
                border-radius: 10px;
            }
            QPushButton:hover {
                background-color: rgba(65, 105, 225, 150);
            }
        """)
        about_btn.clicked.connect(self.show_about_dialog)

        # اضافه کردن در ردیف 2، ستون 0 (پایین چپ)
        menu_layout.addWidget(about_btn, 2, 0, 1, 1, alignment=Qt.AlignBottom | Qt.AlignLeft)

        # -------------------- ۳. منوی دکمه‌های اصلی (مرکز) --------------------
        center_buttons_container = QWidget()
        center_layout = QVBoxLayout(center_buttons_container)
        center_layout.setAlignment(Qt.AlignCenter)
        center_layout.setSpacing(25)

        buttons = [
            ("Review", self.show_review),
            ("Edit", self.show_edit),
            ("Exit", self.page_exit),
        ]

        for text, func in buttons:
            btn = QPushButton(text)
            btn.setFixedSize(400, 120)

            btn.setStyleSheet("""
                QPushButton {
                    font-size: 28px;
                    font-weight: 800;
                    color: #FFFFFF;
                    background-color: rgba(25, 25, 112, 180);
                    border: 2px solid rgba(255, 255, 255, 0.7);
                    border-radius: 20px;
                    padding: 15px 30px;
                }
                QPushButton:hover {
                    background-color: rgba(65, 105, 225, 220);
                    border: 2px solid #FFFFFF;
                }
                QPushButton:pressed {
                    background-color: rgba(45, 85, 205, 255);
                }
            """)
            center_layout.addWidget(btn, alignment=Qt.AlignCenter)
            btn.clicked.connect(func)

        # اضافه کردن کانتینر مرکزی به ردیف 1، ستون 1 (مرکز)
        menu_layout.addWidget(center_buttons_container, 1, 1, alignment=Qt.AlignCenter)

        # تنظیم ستون‌ها و ردیف‌ها برای کشیده شدن
        menu_layout.setColumnStretch(0, 1)  # فضای خالی چپ
        menu_layout.setColumnStretch(1, 3)  # فضای دکمه‌ها
        menu_layout.setColumnStretch(2, 1)  # فضای خالی راست
        menu_layout.setRowStretch(0, 1)  # فضای خالی بالا
        menu_layout.setRowStretch(1, 5)  # فضای دکمه‌ها
        menu_layout.setRowStretch(2, 1)  # فضای خالی پایین

    def show_about_dialog(self):
        """باز کردن پنجره About"""
        dialog = AboutDialog(self)
        dialog.exec_()

    def show_review(self):
        from review import ReviewPage
        # حذف صفحه قبلی در صورت وجود (برای جلوگیری از انباشتگی در Stack)
        if self.review_page:
            self.stack.removeWidget(self.review_page)
        self.review_page = ReviewPage(self)
        self.stack.addWidget(self.review_page)
        self.stack.setCurrentWidget(self.review_page)

    def show_edit(self):
        """نمایش صفحه مدیریت کلمات"""
        self.stack.setCurrentWidget(self.edit_menu)

    def page_exit(self):
        if hasattr(self.bg, "timer"):
            self.bg.timer.stop()
        self.close()

    def closeEvent(self, event):
        if hasattr(self.bg, "timer"):
            self.bg.timer.stop()
        event.accept()


# ------------------------------------------------------------------
# نقطه ورودی اصلی برنامه
# ------------------------------------------------------------------
if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())