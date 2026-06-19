import sys
from PyQt5.QtWidgets import QApplication
from src.overlay import OverlayWindow
from src.models import Target

def main():
    app = QApplication(sys.argv)
    w = OverlayWindow()
    w.show()

    # Show a large obvious rectangle
    t = Target(bbox_id=1, x1=200, y1=200, x2=900, y2=600, label="VISIBILITY", confidence=1.0)
    w.signals.show_target.emit(t)

    print("Overlay visibility test running. You should see a big yellow box.")
    print("Close this terminal or press Ctrl+C to exit.")
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()