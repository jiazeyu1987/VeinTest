import slicer.util as util
import qt, slicer
import math


class FocusWidget(qt.QWidget):
    parent_widget = None
    geometry = None
    current_depth = 3
    radius_probe = 30

    def __init__(self, length=100, major_ticks=10, minor_ticks=5):
        super().__init__()
        self.length = length
        self.major_ticks = major_ticks
        self.minor_ticks = minor_ticks

        self.setAttribute(qt.Qt.WA_TransparentForMouseEvents, False)
        self.parent_widget = qt.QWidget()
        self.parent_widget.setParent(slicer.app.layoutManager().sliceWidget("Red"))
        self.parent_widget.setStyleSheet("background:transparent;")  # 设置样式表
        util.addWidget2(self.parent_widget, self)
        self.parent_widget.setAttribute(qt.Qt.WA_TransparentForMouseEvents, True)
        self.setAttribute(qt.Qt.WA_TransparentForMouseEvents, True)
        self.initLater()

    def initLater(self):
        slice_widget = slicer.app.layoutManager().sliceWidget("Red")
        slice_widget_width = slice_widget.width
        slice_widget_height = slice_widget.height
        width = slice_widget_width // 2
        height = slice_widget_height
        posX = util.ultra_x
        posY = util.ultra_y
        self.left_pos = posX
        self.right_pos = posX + util.ultra_width
        self.length = height
        self.setMinimumSize(width, height)
        self.parent_widget.geometry = qt.QRect(posX, posY, util.ultra_width, util.ultra_height)

    def paintEvent(self, event):
        painter = qt.QPainter(self)
        pen = qt.QPen(qt.Qt.red)
        painter.setPen(pen)

        depth_pixel = util.hifu_depth / self.current_depth * util.ultra_height

        middle_pos = (self.left_pos + self.right_pos) / 2

        angle_rad1 = math.radians(util.angle)
        angle_rad2 = math.radians(-util.angle)
        start_point = qt.QPoint(middle_pos, depth_pixel)
        end_point1 = qt.QPoint(
            int(middle_pos + 300 * math.sin(angle_rad1)),
            int(depth_pixel - 300 * math.cos(angle_rad1))
        )

        end_point2 = qt.QPoint(
            int(middle_pos + 300 * math.sin(angle_rad2)),
            int(depth_pixel - 300 * math.cos(angle_rad2))
        )

        # Draw lines
        painter.drawLine(start_point, end_point1)
        painter.drawLine(start_point, end_point2)

        pen.setStyle(qt.Qt.DotLine)
        painter.setPen(pen)

        painter.drawEllipse(middle_pos - self.radius_probe / 2, depth_pixel - self.radius_probe / 2, self.radius_probe,
                            self.radius_probe)

    def setDepth(self, value):
        self.current_depth = value
        self.update()

    def show(self):
        self.parent_widget.show()

    def hide(self):
        self.parent_widget.hide()
