# from PyQt5.QtWidgets import QGraphicsItem, QGraphicsEllipseItem, QWidget, QPushButton
# from PyQt5.QtGui import QBrush, QPen, QColor, QRadialGradient, QPainter, QFont
from PyQt5.QtCore import pyqtSignal
from qt import *
import math

class ControlButton(QPushButton):
    # 自定义信号，可以在鼠标点击时触发
    pressed = pyqtSignal()
    released = pyqtSignal()

    def __init__(self, w = 80, h = 32, text='', choosed=False, radius = 3,  parent=None):
        # QObject.__init__(self)
        # QGraphicsItem.__init__(self, parent)

        super(ControlButton, self).__init__(parent)

        self.w = w
        self.h = h
        self.text = text
        if self.text == "front":
            self.drawText = "正视图"
        elif self.text == "back":
            self.drawText = "后视图"
        elif self.text == "left":
            self.drawText = "左视图"
        else:
            self.drawText = "右视图"


        self.choosed = choosed

        self.choosedColor = QColor("#215BB3")
        self.originalColor = QColor("#000000")

        self.borderColor = QColor("#699FC3")
        self.borderWidth = 1
        self.radius = radius

        self.setFixedSize(self.w, self.h)


        # 设置鼠标可点击

        # self.setStyleSheet('background-color:white;')
        self.setStyleSheet('background-color:transparent;')


    def boundingRect(self):
        # 返回按钮的边界矩形
        return QRectF(0, 0, self.w,  self.h)
    def setChoosed(self, status=True):
        if self.choosed != status:
            self.choosed = status
            self.update()


    def paintEvent(self, event):

        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, True)

        # 边框
        pen = QPen(self.borderColor)
        painter.setPen(pen)
        painter.drawRoundedRect(QRectF(0, 0, self.w,  self.h), self.radius, self.radius)


        self.color = self.choosedColor if self.choosed else self.originalColor
        painter.setBrush(QBrush(self.color))
        # painter.drawRoundedRect(QRectF(self.borderWidth, self.borderWidth, self.w-2 *self.borderWidth,  self.h-2*self.borderWidth), self.radius, self.radius)
        painter.drawRoundedRect(QRectF(0, 0, self.w,  self.h), self.radius, self.radius)


        # 绘制字符串
        pen = QPen(Qt.white)  # 边框
        font = QFont()
        font.setPointSize(12)
        font.setBold(False)
        font.setFamily("Arial")


        painter.setPen(pen)
        painter.setBrush(self.color)
        painter.setFont(font)
        painter.drawText(QRectF(0, 0, self.w,  self.h), Qt.AlignCenter, self.drawText)

    def mousePressEvent(self, event):
        # 当鼠标按下时，将按钮标记为被按下
        self.choosed = True
        self.pressed.emit()

    def mouseReleaseEvent(self, event):
        # 当鼠标释放时，如果释放点在按钮内部，触发 clicked 信号
        self.released.emit()
        pass



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

    button = ControlButton(text="正视图")  # 创建一个半径为50，颜色为红色的圆形按钮
    scene.addWidget(button).setPos(0, 0)
    view = QGraphicsView(scene)
    view.show()

    button.pressed.connect(onClicked)

    sys.exit(app.exec_())
