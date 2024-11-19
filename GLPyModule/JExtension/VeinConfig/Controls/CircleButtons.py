# from PyQt5.QtWidgets import QGraphicsItem, QGraphicsEllipseItem, QWidget, QPushButton
# from PyQt5.QtGui import QBrush, QPen, QColor, QRadialGradient, QPainter, QFont
from PyQt5.QtCore import QRectF, Qt, pyqtSignal, QPointF, QObject
from qt import *

import math


class CircleButton(QPushButton):
    # 自定义信号，可以在鼠标点击时触发
    pressed = pyqtSignal()
    released = pyqtSignal()

    def __init__(self, internalRadius=10.0, externalRadius=20.0, color=None, text='', parent=None):
        # QObject.__init__(self)
        # QGraphicsItem.__init__(self, parent)

        super(CircleButton, self).__init__(parent)

        self.text = text

        self.is_pressed = False
        self.is_current = False
        self.is_therapy = False
        self.mode = color
        self.color = color
        self.orginalColor = self.color
        self.internalRadius = internalRadius
        self.externalRadius = externalRadius
        self.radius = externalRadius

        self.center = QPoint(self.radius, self.radius)

        # 设置鼠标可点击
        # self.setAcceptHoverEvents(True)
        # if self.mode is not None:
        self.setMinimumSize(2 * self.radius, 2 * self.radius)
        self.setMaximumSize(2 * self.radius, 2 * self.radius)
        # self.setStyleSheet('background-color:white;')
        self.setStyleSheet('background-color:transparent;')

        self.timer = None
        self.changFlag = False
        self.midColor = QColor("#FFFFFF")

    def boundingRect(self):
        # 返回按钮的边界矩形
        return QRectF(0, 0, 2 * self.radius, 2 * self.radius)

    def paintEvent(self, event):

        if self.mode == None:
            self.color = QColor("#FF9568") if self.is_therapy else QColor("#50B584")  # 治疗与非治疗是不同的颜色

        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, True)
        # 绘制字符串
        # painter.drawText(QRectF(-self.radius, -self.radius, 2 * self.radius, 2 * self.radius), self.text)

        if self.externalRadius > self.internalRadius:
            gradient = QRadialGradient(self.center.x(), self.center.y(), self.externalRadius, self.center.x(),
                                       self.center.y())
            gradient.setColorAt(0.5, self.midColor);  # 内层渐变的透明色
            gradient.setColorAt(1, self.color);  # 外圈

            painter.setPen(Qt.transparent)
            painter.setBrush(QBrush(gradient))
            # 外圈
            # painter.drawEllipse(self.center, self.radius, self.radius)
            painter.drawEllipse(self.boundingRect())
            # painter.drawArc(self.boundingRect(), 0, 361)

            if self.timer is None:
                self.timer = QTimer()
                self.timer.start(1024)
                self.timer.timeout.connect(self.flashCircle)
                pass
        else:
            self.timer = None

        # 内圈  一定要在外圈之后，需要覆盖
        pen = QPen(self.color)  # 边框
        brush = QBrush(self.color if not self.is_pressed else self.color.darker(128))  # 填充
        painter.setPen(pen)
        painter.setBrush(brush)
        # painter.drawEllipse(QRectF(self.center.x()-self.internalRadius, self.center.y()-self.internalRadius, 2 * self.internalRadius, 2 * self.internalRadius))
        painter.drawEllipse(self.center, self.internalRadius, self.internalRadius)
        # painter.drawArc(self.boundingRect(), 0, 360*16)

        # 绘制字符串
        pen = QPen(Qt.white)  # 边框
        font = QFont()
        font.setPointSize(10)
        font.setBold(True)
        font.setFamily("Arial")

        painter.setPen(pen)
        painter.setFont(font)
        painter.drawText(self.boundingRect(), Qt.AlignCenter, self.text)

    def flashCircle(self):
        if not self:
            # print(self)
            if self.timer:
                # print(self.timer, "-stopped-")
                self.timer.stop()
            return
        self.midColor = self.color.darker(150) if self.changFlag else QColor("#FFFFFF")
        self.changFlag = not self.changFlag
        self.update()

    def contains(self, point):
        # 判断给定点是否在按钮内部
        center = self.center
        distance = math.sqrt((point.x() - center.x()) ** 2 + (point.y() - center.y()) ** 2)
        return distance <= self.radius

    def setTherapy(self, isTherapy):
        self.is_therapy = isTherapy
        self.update()

    def setAsCurrentPos(self, status, circleButton=None):

        # x = circleButton.pos().x()
        # y = circleButton.pos().y()
        x = self.x
        y = self.y
        if self.is_current != status:  # 说明传入的状态与当前的状态不一致，需要做改变
            self.is_current = status

            if status:
                self.externalRadius = 2 * self.internalRadius
                x -= self.externalRadius - self.internalRadius
                y -= self.externalRadius - self.internalRadius
            else:
                x += self.externalRadius - self.internalRadius
                y += self.externalRadius - self.internalRadius
                self.externalRadius = self.internalRadius

            self.radius = self.externalRadius
            self.center = QPointF(self.radius, self.radius)
            self.setMinimumSize(2 * self.radius, 2 * self.radius)
            self.setMaximumSize(2 * self.radius, 2 * self.radius)

            # circleButton.setPos(x, y)
            self.update()

        return x, y

    def mousePressEvent(self, event):
        # 当鼠标按下时，将按钮标记为被按下
        self.color = self.color.darker(128)
        if self.contains(event.pos()):
            self.is_pressed = True
            # self.clicked.emit()

            self.update()
        # super(CircleButton, self).mousePressEvent(event)
        self.pressed.emit()

    def mouseReleaseEvent(self, event):
        self.color = self.orginalColor
        # 当鼠标释放时，如果释放点在按钮内部，触发 clicked 信号
        # if self.is_pressed and self.contains(event.pos()):
        #     self.released.emit()
        self.is_pressed = False
        self.update()
        # super(CircleButton, self).mouseReleaseEvent(event)
        self.released.emit()


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

    button = CircleButton(internalRadius=10, externalRadius=20, text='RX')  # 创建一个半径为50，颜色为红色的圆形按钮
    # button.setPos(100, 100)  # 设置按钮位置
    # button.is_pressed.connect(lambda: print("Button clicked!"))  # 连接点击信号

    button1 = CircleButton(internalRadius=10, externalRadius=10, color=QColor("#396CCF"),
                           text='RX')  # 创建一个半径为50，颜色为红色的圆形按钮
    # button1.setPos(20, 20)  # 设置按钮位置

    scene.addWidget(button).setPos(100, 100)
    scene.addWidget(button1).setPos(20, 20)

    print(button.pos())
    view = QGraphicsView(scene)
    view.show()

    button.pressed.connect(onClicked)
    button1.released.connect(onRelease)

    sys.exit(app.exec_())
