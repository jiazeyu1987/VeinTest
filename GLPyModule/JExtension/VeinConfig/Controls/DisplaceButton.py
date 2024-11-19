from PyQt5.QtWidgets import QGraphicsItem, QGraphicsEllipseItem, QWidget, QPushButton
from PyQt5.QtGui import QBrush, QPen, QFont, QColor, QRadialGradient, QPainter, QPolygon, QPolygonF, QTransform
from PyQt5.QtCore import QRectF, Qt, pyqtSignal, QPointF, QObject, QPoint
from qt import *
class DisplaceButton(QPushButton):
    # 自定义信号，可以在鼠标点击时触发
    clicked = pyqtSignal()
    pressed = pyqtSignal()

    def __init__(self, width=73.52, height=75.69, color=Qt.red, text='', angle=0, parent=None, buttonW=48.37, buttonH=58.74):
        # QObject.__init__(self)
        # QGraphicsItem.__init__(self, parent)

        super(DisplaceButton, self).__init__(parent)

        self.buttonW = buttonW
        self.buttonH = buttonH
        self.viewwidth = width
        self.viewheight = height
        if buttonW > width:
            self.viewwidth = buttonW
        if buttonH > height:
            self.viewheight = buttonH

        self.buttonRect = self.getButtonRect()

        self.color = color
        self.oringColor = color

        self.text = text
        self.rotationAngle = angle

        self.setFixedSize(self.viewwidth, self.viewheight)

        # self.setStyleSheet('background-color:white;')
        self.setStyleSheet('background-color:transparent;')

    def boundingRect(self):
        # 返回按钮的边界矩形
        return QRectF(0, 0, self.viewwidth, self.viewheight)
    def getButtonRect(self):
        return QRectF((self.viewwidth - self.buttonW) / 2, (self.viewheight - self.buttonH) / 2, self.buttonW, self.buttonH)

    def getRotationTransform(self):
        transform = QTransform()
        self.center = QPoint(self.viewwidth / 2, self.viewheight / 2)
        transform.translate(self.center.x(), self.center.y())
        transform.rotate(self.rotationAngle)

        transform.translate(-self.center.x(), -self.center.y())
        return transform

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        pen = QPen(self.color)  # 边框
        brush = QBrush(self.color)  # 填充
        painter.setPen(pen)
        painter.setBrush(brush)
        painter.setTransform(self.getRotationTransform())

        path = QPolygonF(
            [
                # QPointF(self.width / 2, 0),
                # QPointF(0, self.height / 2),
                # QPointF(self.width / 5, self.height / 2),
                # QPointF(self.width / 5, self.height),
                # QPointF(self.width / 5 * 4, self.height),
                # QPointF(self.width / 5 * 4, self.height / 2),
                # QPointF(self.width / 5 * 5, self.height / 2),
                # QPointF(self.width / 2, 0),

                QPointF(self.buttonRect.x() + self.buttonRect.width() / 2, self.buttonRect.y()),
                QPointF(self.buttonRect.x(), self.buttonRect.y() + self.buttonRect.height() / 2),
                QPointF(self.buttonRect.x() + self.buttonRect.width() / 5, self.buttonRect.y() + self.buttonRect.height() / 2),
                QPointF(self.buttonRect.x() + self.buttonRect.width() / 5, self.buttonRect.y() + self.buttonRect.height()),
                QPointF(self.buttonRect.x() + self.buttonRect.width() / 5 * 4, self.buttonRect.y() + self.buttonRect.height()),
                QPointF(self.buttonRect.x() + self.buttonRect.width() / 5 * 4, self.buttonRect.y() + self.buttonRect.height() / 2),
                QPointF(self.buttonRect.x() + self.buttonRect.width() / 5 * 5, self.buttonRect.y() + self.buttonRect.height() / 2),
                QPointF(self.buttonRect.x() + self.buttonRect.width() / 2, self.buttonRect.y() ),
            ]
        )
        painter.drawPolygon(path)

        # 绘制字符串
        pen = QPen(Qt.white)  # 边框
        font = QFont()
        font.setPointSize(15)
        font.setBold(True)
        font.setFamily("Arial")

        painter.setPen(pen)
        painter.setFont(font)
        painter.drawText(self.boundingRect(), Qt.AlignCenter, self.text)

    def mousePressEvent(self, event):
        # 当鼠标按下时，将按钮标记为被按下

        self.color = self.color.darker(128)

        if self.contains(event.pos()):
            self.is_pressed = True
            # self.clicked.emit()

        self.update()
        # super(DisplaceButton, self).mousePressEvent(event)
        self.pressed.emit()

    def mouseReleaseEvent(self, event):
        # 当鼠标释放时，如果释放点在按钮内部，触发 clicked 信号

        self.color = self.oringColor
        # if self.is_pressed and self.contains(event.pos()):
        #     self.released.emit()
        self.is_pressed = False
        self.update()
        # super(DisplaceButton, self).mouseReleaseEvent(event)
        self.released.emit()

    def contains(self, point):
        # 判断给定点是否在按钮内部
        pass
        # center = QPointF(0, 0)
        # distance = (point - center).manhattanLength()
        # return distance <= self.radius
    def setTherapy(self, isTherapy):
        self.is_therapy = isTherapy
        self.update()
    def setRotation(self, angle):
        self.rotationAngle = angle
        self.repaint()

# 示例使用代码：
if __name__ == '__main__':

    from PyQt5.QtWidgets import QGraphicsScene, QGraphicsView, QApplication
    import sys

    def onClicked():
        print("clicked")
    def onRelease():
        print("released")

    app = QApplication(sys.argv)
    scene = QGraphicsScene()

    button = DisplaceButton( text='RX')  # 创建一个半径为50，颜色为红色的圆形按钮
    # button.setPos(100, 100)  # 设置按钮位置
    # button.is_pressed.connect(lambda: print("Button clicked!"))  # 连接点击信号

    button1 = DisplaceButton(text='RY')  # 创建一个半径为50，颜色为红色的圆形按钮
    # button1.setPos(20, 20)  # 设置按钮位置


    item = scene.addWidget(button)
    item.setRotation(60)
    # scene.addWidget(button1).setPos(20, 20)

    view = QGraphicsView(scene)
    view.show()

    button.clicked.connect(onClicked)
    button1.clicked.connect(onRelease)

    sys.exit(app.exec_())
