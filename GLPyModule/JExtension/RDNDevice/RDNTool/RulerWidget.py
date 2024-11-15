import slicer.util as util
import qt, slicer


class RulerWidget(qt.QWidget):
    parent_widget = None
    geometry = None

    def __init__(self, length=100, major_ticks=10, minor_ticks=5):
        super().__init__()
        self.length = length
        self.major_ticks = major_ticks
        self.minor_ticks = minor_ticks

        self.setAttribute(qt.Qt.WA_TransparentForMouseEvents, True)
        self.parent_widget = qt.QWidget()
        self.parent_widget.setParent(slicer.app.layoutManager().sliceWidget("Red"))
        util.addWidget2(self.parent_widget, self)
        self.parent_widget.setAttribute(qt.Qt.WA_TransparentForMouseEvents, True)
        # self.setAttribute(qt.Qt.WA_TransparentForMouseEvents, True)
        util.singleShot(100, self.initLater)

    def initLater(self):
        # 获取红色切片图的宽度和高度
        width = 30
        height = util.ultra_height
        self.length = height
        self.setMinimumSize(width, height)

        # print(f"width and height is-----{slice_widget_width}x{slice_widget_height}")
        # 设置 parent_widget 的位置为右边居中
        posX = util.ultra_x + util.ultra_width - 30
        posY = util.ultra_y
        self.parent_widget.setGeometry(qt.QRect(posX, posY, width, height))

    def paintEvent(self, event):
        painter = qt.QPainter(self)
        pen = qt.QPen(qt.Qt.white)
        painter.setPen(pen)

        major_tick_length = 10
        minor_tick_length = 5

        # Draw major ticks
        for i in range(self.major_ticks + 1):
            y = i * (self.length / self.major_ticks)
            painter.drawLine(0, y + 5, major_tick_length, y + 5)
            painter.drawText(major_tick_length + 5, y + 5 + 5, str(i))

        # Draw minor ticks
        for i in range(1, self.major_ticks * self.minor_ticks):
            y = i * (self.length / (self.major_ticks * self.minor_ticks))
            if i % self.minor_ticks != 0:
                painter.drawLine(0, y + 5, minor_tick_length, y + 5)

    def setDepth(self, value=3):
        self.major_ticks = value
        self.update()

    def show(self):
        self.parent_widget.show()

    def hide(self):
        self.parent_widget.hide()
