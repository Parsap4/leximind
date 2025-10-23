# background.py
import random
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QPainter, QColor, QFont
from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import Qt


class AnimatedBackground(QWidget):
    """پس‌زمینه‌ای که حروف انگلیسی رنگی رو پایین میاره"""

    def __init__(self, parent=None, count=35):
        super().__init__(parent)
        self.letters = []
        self.count = count
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_letters)
        self.timer.start(50)  # به‌روزرسانی در هر 50 میلی‌ثانیه
        self.generate_letters()
        # مهم: برای دیدن حروف باید پس‌زمینه خود ویجت شفاف باشد
        self.setAttribute(Qt.WA_NoSystemBackground)
        self.setAutoFillBackground(False)
        self.setMouseTracking(False)

    def generate_letters(self):
        """تولید موقعیت‌ها، اندازه‌ها و رنگ‌های تصادفی برای حروف"""
        w, h = max(1, self.width()), max(1, self.height())
        self.letters.clear()
        for _ in range(self.count):
            letter = random.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
            x = random.uniform(0, w)
            y = random.uniform(0, h)
            color = QColor(random.randint(50, 255), random.randint(50, 255), random.randint(50, 255))
            size = random.randint(14, 48)
            speed = random.uniform(0.7, 3.0)
            self.letters.append({
                "letter": letter, "x": x, "y": y,
                "color": color, "size": size, "speed": speed
            })

    def resizeEvent(self, event):
        """بازسازی حروف هنگام تغییر اندازه پنجره"""
        self.generate_letters()
        super().resizeEvent(event)

    def update_letters(self):
        """به‌روزرسانی موقعیت حروف (حرکت به سمت پایین)"""
        h, w = max(1, self.height()), max(1, self.width())
        for l in self.letters:
            l["y"] += l["speed"]
            if l["y"] > h:
                l["y"] = -10.0
                l["x"] = random.uniform(0, w)
        self.update()

    def paintEvent(self, event):
        """رسم حروف"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # رسم یک پس‌زمینه جامد برای پایه (به‌جای شفافیت کامل)
        painter.fillRect(self.rect(), QColor(44, 62, 80, 255))

        for l in self.letters:
            painter.setPen(l["color"])
            font = QFont("Arial", l["size"])
            painter.setFont(font)
            painter.drawText(int(l["x"]), int(l["y"]), l["letter"])

        painter.end()