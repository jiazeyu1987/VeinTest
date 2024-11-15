import qt
import slicer.util as util


class CompareDialog(qt.QDialog):
    def __init__(self, parent):
        super().__init__()
        self.parent_window = parent
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('影像比较')
        self.setGeometry(150, 100, 1080, 640)

        layout = qt.QHBoxLayout()
        before_label = qt.QLabel(self)
        before_pixmap = qt.QPixmap(self.parent_window.resourcePath(util.treatment_before_after['.before']))
        before_label.setPixmap(before_pixmap.scaled(640, 640, qt.Qt.KeepAspectRatio, qt.Qt.SmoothTransformation))
        before_label.setAlignment(qt.Qt.AlignCenter)

        after_label = qt.QLabel(self)
        after_pixmap = qt.QPixmap(self.parent_window.resourcePath(util.treatment_before_after['.after']))
        after_label.setPixmap(after_pixmap.scaled(640, 640, qt.Qt.KeepAspectRatio, qt.Qt.SmoothTransformation))
        after_label.setAlignment(qt.Qt.AlignCenter)

        layout.addWidget(before_label)
        layout.addWidget(after_label)

        self.setLayout(layout)
