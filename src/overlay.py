import math
from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5.QtCore import Qt, QTimer, QObject, pyqtSignal
from PyQt5.QtGui import QPainter, QColor, QPen, QBrush
from src.models import Target
from src.logger import logger


class OverlaySignals(QObject):
    show_target = pyqtSignal(object)
    clear_target = pyqtSignal()


class OverlayWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.signals = OverlaySignals()
        self.signals.show_target.connect(self._on_show_target)
        self.signals.clear_target.connect(self._on_clear_target)

        self.current_target: Target | None = None
        self._pulse_phase = 0.0
        self._dpr = 1.0

        self._setup_window()

        self._timer = QTimer(self)
        self._timer.timeout.connect(self._tick)
        self._timer.start(16)

        logger.info("Overlay window created")

    def _setup_window(self):
        # Window flags: keep it simple + reliable on Windows
        self.setWindowFlags(
            Qt.FramelessWindowHint |
            Qt.WindowStaysOnTopHint |
            Qt.Tool
        )

        # IMPORTANT: do NOT set WA_NoSystemBackground on Windows overlays (can break painting)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setAutoFillBackground(False)

        # Click-through (keep this, but only after visibility is confirmed)
        self.setAttribute(Qt.WA_TransparentForMouseEvents, True)

        # Use full geometry (includes taskbar area sometimes; more reliable alignment)
        screen = QApplication.primaryScreen()
        if screen:
            self._dpr = screen.devicePixelRatio()
            geo = screen.geometry()
            self.setGeometry(geo)
            logger.info(f"Overlay DPR = {self._dpr}, screen geometry = {geo}")
        else:
            logger.warning("No primary screen detected; using 1920x1080 fallback")
            self._dpr = 1.0
            self.setGeometry(0, 0, 1920, 1080)

        # Force opacity fully visible
        self.setWindowOpacity(1.0)

    def _tick(self):
        if self.current_target:
            self._pulse_phase = (self._pulse_phase + 0.06) % (2 * math.pi)
            self.update()

    def _on_show_target(self, target: Target):
        self.current_target = target
        self.show()
        self.raise_()
        self.activateWindow()  # sometimes helps on Windows
        logger.info(f"Overlay: showing target id={target.bbox_id} physical={target.bounds}")

    def _on_clear_target(self):
        self.current_target = None
        self.update()

    def _scale(self, v: int) -> int:
        return int(v / (self._dpr or 1.0))

    def paintEvent(self, event):
        if not self.current_target:
            return

        t = self.current_target

        # Convert physical -> logical for drawing
        x1 = self._scale(t.x1)
        y1 = self._scale(t.y1)
        x2 = self._scale(t.x2)
        y2 = self._scale(t.y2)
        w = max(1, x2 - x1)
        h = max(1, y2 - y1)

        pulse = 0.5 + 0.5 * abs(math.sin(self._pulse_phase))  # 0.5..1.0
        glow_alpha = int(160 * pulse)
        fill_alpha = 60  # visible but not blocking
        border_alpha = 255

        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Glow (thick)
        painter.setPen(QPen(QColor(255, 255, 0, glow_alpha), 18))
        painter.setBrush(Qt.NoBrush)
        painter.drawRoundedRect(x1 - 10, y1 - 10, w + 20, h + 20, 14, 14)

        # Fill
        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(QColor(255, 255, 0, fill_alpha)))
        painter.drawRoundedRect(x1, y1, w, h, 10, 10)

        # Border
        painter.setPen(QPen(QColor(255, 255, 0, border_alpha), 5))
        painter.setBrush(Qt.NoBrush)
        painter.drawRoundedRect(x1, y1, w, h, 10, 10)

        painter.end()