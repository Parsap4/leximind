# main.py - کد نهایی با تاریخ و دکمه About فقط در منوی اصلی و بستن ایمن دیتابیس

import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QPushButton, QVBoxLayout, QStackedWidget,
    QDialog, QLabel, QTextEdit, QGridLayout
)
from PyQt5.QtCore import Qt, QDate
from background import AnimatedBackground, AnimatedBackground2
from review import ReviewPage
from edit import EditMainMenu
from edit import AddWordPage, EditRemovePage


# import jdatetime # <--- دیگر از jdatetime استفاده نمی‌کنیم


# ------------------------------------------------------------------
# **توابع تبدیل تاریخ (تبدیل تقریبی میلادی به شمسی)**
# ------------------------------------------------------------------

def gregorian_to_jalali(gy, gm, gd):
    """
    تبدیل تاریخ میلادی به شمسی بدون استفاده از کتابخانه خارجی.
    منبع: الگوریتم استاندارد (مانند الگوریتم Zeller یا تبدیل‌های مبتنی بر آفست)
    """
    g_days_in_month = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    j_days_in_month = [31, 31, 31, 31, 31, 31, 30, 30, 30, 30, 30, 29]

    # تعیین سال کبیسه میلادی
    if gy % 4 == 0 and (gy % 100 != 0 or gy % 400 == 0):
        g_days_in_month[1] = 29

    # محاسبه روزهای سپری شده از ابتدای سال میلادی
    day_count = gd
    for i in range(gm - 1):
        day_count += g_days_in_month[i]

    # آفست ثابت: روز شروع سال شمسی (مثلا ۳۰ مارس)
    # 21 مارس (روز 80) شروع سال شمسی است.
    # این عدد بستگی به سال میلادی و کبیسه بودن آن دارد.
    if gy > 1996 and gy % 4 == 1:
        day_count -= 79
    else:
        day_count -= 80

    if day_count > 0:
        jy = gy - 621
    else:
        day_count += 365 + (1 if gy % 4 == 0 and (gy % 100 != 0 or gy % 400 == 0) else 0)
        jy = gy - 622

    # تعیین سال کبیسه شمسی (برای سال‌های کبیسه دوره‌ای)
    if jy % 4 == 3:  # هر 4 سال یکبار
        j_days_in_month[11] = 30  # اسفند 30 روز

    jm = 0
    for i in range(12):
        if day_count <= j_days_in_month[i]:
            jm = i + 1
            break
        day_count -= j_days_in_month[i]

    jd = day_count

    return jy, jm, jd


def format_jalali(year, month, day):
    """قالب‌بندی تاریخ شمسی با استفاده از اعداد فارسی."""
    PERSIAN_NUMERALS = "۰۱۲۳۴۵۶۷۸۹"

    def to_persian(n):
        s = str(n)
        return "".join([PERSIAN_NUMERALS[int(d)] for d in s])

    p_year = to_persian(year)
    p_month = to_persian(month).zfill(2)
    p_day = to_persian(day).zfill(2)

    return f"{p_year}/{p_month}/{p_day}"


# ------------------------------------------------------------------


# برای دسترسی به DatabaseManager بدون ایجاد وابستگی دایره‌ای
try:
    from edit import DatabaseManager as EditDBManager
    from review import DatabaseManager as ReviewDBManager
except ImportError:
    # اگر این import ها شکست خوردند، فرض می‌کنیم DatabaseManager را نداریم.
    class EditDBManager:
        def close(self): pass


    class ReviewDBManager:
        def close(self): pass


# ------------------------------------------------------------------
# **کلاس پنجره About**
# ------------------------------------------------------------------
class AboutDialog(QDialog):
    # ... (کلاس AboutDialog بدون تغییر)
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("About Flash Card App")
        self.resize(500, 350)

        # استایل‌ها برای تم تیره
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

        # **تعریف و تنظیم پس‌زمینه‌ها**
        self.bg = AnimatedBackground(self, count=35)
        self.bg2 = AnimatedBackground2(self, count=35)  # <-- پس‌زمینه دوم/روشن
        self.current_theme = "dark"  # تم پیش‌فرض

        self.bg.setGeometry(0, 0, self.width(), self.height())
        self.bg2.setGeometry(0, 0, self.width(), self.height())
        self.bg2.hide()  # پنهان کردن تم روشن در ابتدا
        self.bg.lower()  # نمایش تم تیره (bg) در ابتدا

        self.stack = QStackedWidget(self)
        self.main_menu = QWidget()
        self.main_menu.setStyleSheet("background: transparent;")
        self.stack.addWidget(self.main_menu)

        self.review_page = None

        # EditMainMenu باید در ابتدا ساخته شود تا بتوانیم به صفحات داخلی آن (Add/Edit) دسترسی داشته باشیم.
        self.edit_menu = EditMainMenu(self)
        self.stack.addWidget(self.edit_menu)

        self.setup_main_menu()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.stack)
        self.setLayout(layout)
        self.stack.raise_()

    def resizeEvent(self, event):
        # **تنظیم اندازه برای هر دو پس‌زمینه**
        self.bg.setGeometry(0, 0, self.width(), self.height())
        self.bg2.setGeometry(0, 0, self.width(), self.height())
        super().resizeEvent(event)

    def setup_main_menu(self):
        # استفاده از QGridLayout برای قرار دادن اجزا در گوشه‌ها
        menu_layout = QGridLayout(self.main_menu)
        menu_layout.setContentsMargins(20, 20, 20, 20)

        # -------------------- ۱. واترمارک تاریخ (گوشه بالا راست) --------------------
        # **منطق نمایش تاریخ شمسی و میلادی با تبدیل دستی**
        current_gregorian = QDate.currentDate()
        gy = current_gregorian.year()
        gm = current_gregorian.month()
        gd = current_gregorian.day()

        # تبدیل میلادی به شمسی
        jy, jm, jd = gregorian_to_jalali(gy, gm, gd)

        # قالب‌بندی تاریخ‌ها
        gregorian_str = current_gregorian.toString("yyyy-MM-dd")  # میلادی با اعداد انگلیسی
        # شمسی با اعداد فارسی
        jalali_str = format_jalali(jy, jm, jd)

        # ساخت متن نهایی (شمسی در بالا، میلادی در پایین)
        date_text = f"{jalali_str}\n{gregorian_str}"

        date_label = QLabel(date_text)

        # **تنظیم فونت برای نمایش صحیح نویسه‌های فارسی**
        date_label.setStyleSheet("""
            color: rgba(255, 255, 255, 120);
            font-size: 16px;
            font-weight: bold;
            font-family: 'Tahoma', 'B Nazanin', sans-serif;
        """)

        date_label.setAlignment(Qt.AlignTop | Qt.AlignRight)

        menu_layout.addWidget(date_label, 0, 2, 1, 1, alignment=Qt.AlignTop | Qt.AlignRight)

        # -------------------- ۲. دکمه Toggle Theme (گوشه بالا چپ) --------------------
        theme_btn = QPushButton("🌙 Toggle Theme")
        theme_btn.setFixedSize(160, 40)
        theme_btn.setStyleSheet("""
            QPushButton {
                font-size: 18px;
                font-weight: 500;
                color: #FFFFFF;
                background-color: rgba(0, 0, 0, 160);
                border: 1px solid #FFFFFF;
                border-radius: 10px;
            }
            QPushButton:hover {
                background-color: rgba(65, 105, 225, 150);
            }
        """)
        theme_btn.clicked.connect(self.toggle_theme)

        # **اضافه کردن دکمه در گوشه بالا چپ**
        menu_layout.addWidget(theme_btn, 0, 0, 1, 1, alignment=Qt.AlignTop | Qt.AlignLeft)

        # -------------------- ۳. دکمه About (گوشه پایین چپ) --------------------
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

        menu_layout.addWidget(about_btn, 2, 0, 1, 1, alignment=Qt.AlignBottom | Qt.AlignLeft)

        # -------------------- ۴. منوی دکمه‌های اصلی (مرکز) --------------------
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

        menu_layout.addWidget(center_buttons_container, 1, 1, alignment=Qt.AlignCenter)

        menu_layout.setColumnStretch(0, 1)
        menu_layout.setColumnStretch(1, 3)
        menu_layout.setColumnStretch(2, 1)
        menu_layout.setRowStretch(0, 1)
        menu_layout.setRowStretch(1, 5)
        menu_layout.setRowStretch(2, 1)

    def show_about_dialog(self):
        """باز کردن پنجره About"""
        dialog = AboutDialog(self)
        dialog.exec_()

    def toggle_theme(self):
        """جابجایی بین تم تیره (bg) و تم روشن (bg2)"""
        # اگر تم فعلی تیره است، به روشن سوییچ کن
        if self.current_theme == "dark":
            self.bg.hide()
            self.bg2.show()
            self.bg2.lower()
            self.current_theme = "light"
        # اگر تم فعلی روشن است، به تیره سوییچ کن
        else:
            self.bg2.hide()
            self.bg.show()
            self.bg.lower()
            self.current_theme = "dark"
        # مطمئن شو که stack در بالاترین لایه قرار دارد
        self.stack.raise_()

    def show_review(self):
        from review import ReviewPage
        # بستن و حذف صفحه قبلی اگر وجود داشت (برای جلوگیری از انباشتگی و بستن اتصال دیتابیس قبلی)
        if self.review_page:
            self.close_review_page_db()
            self.stack.removeWidget(self.review_page)

        self.review_page = ReviewPage(self)
        self.stack.addWidget(self.review_page)
        self.stack.setCurrentWidget(self.review_page)

    def show_edit(self):
        # بستن اتصالات دیتابیس EditMenu قبلی
        self.close_edit_menu_db()

        # ساخت instance جدید از EditMainMenu برای اطمینان از اتصالات دیتابیس جدید
        self.edit_menu = EditMainMenu(self)
        self.stack.addWidget(self.edit_menu)
        self.stack.setCurrentWidget(self.edit_menu)

    def close_review_page_db(self):
        if self.review_page and hasattr(self.review_page, 'db'):
            try:
                self.review_page.db.close()
            except Exception:
                pass

    def close_edit_menu_db(self):
        """بستن اتصالات Edit/Add"""
        if self.edit_menu:
            if hasattr(self.edit_menu.add_page, 'db'):
                try:
                    self.edit_menu.add_page.db.close()
                except Exception:
                    pass
            if hasattr(self.edit_menu.edit_page, 'db'):
                try:
                    self.edit_menu.edit_page.db.close()
                except Exception:
                    pass

    def close_db_connections(self):
        """بستن تمام اتصالات دیتابیس قبل از خروج برنامه"""
        self.close_review_page_db()
        self.close_edit_menu_db()

    def page_exit(self):
        self.close_db_connections()  # بستن اتصالات قبل از خروج
        # **توقف تایمرهای هر دو پس‌زمینه**
        if hasattr(self.bg, "timer"):
            self.bg.timer.stop()
        if hasattr(self.bg2, "timer"):
            self.bg2.timer.stop()
        self.close()

    def closeEvent(self, event):
        self.close_db_connections()  # بستن اتصالات هنگام کلیک روی دکمه X
        # **توقف تایمرهای هر دو پس‌زمینه**
        if hasattr(self.bg, "timer"):
            self.bg.timer.stop()
        if hasattr(self.bg2, "timer"):
            self.bg2.timer.stop()
        event.accept()


# ------------------------------------------------------------------
# نقطه ورودی اصلی برنامه
# ------------------------------------------------------------------
if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())