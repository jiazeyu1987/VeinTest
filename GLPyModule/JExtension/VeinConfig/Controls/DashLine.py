from PyQt5.QtWidgets import QGraphicsItem, QGraphicsEllipseItem
from PyQt5.QtGui import QBrush, QPen, QColor, QRadialGradient, QPainter
from PyQt5.QtCore import QRectF, Qt, pyqtSignal, QPointF, QObject, QPoint

from qt import *
class DashLine(QGraphicsItem):
    def __init__(self, startPos=QPoint(), endPos=QPoint(), color=Qt.red, linewidth=1, parent=None):
        # QObject.__init__(self)
        # QGraphicsItem.__init__(self, parent)

        super(DashLine, self).__init__(parent)

        self.point1 = startPos
        self.point2 = endPos
        self.color = color
        self.linewidth = linewidth

    def boundingRect(self):
        width = (self.point1 - self.point2).manhattanLength()
        height = self.linewidth * 2
        x = width / 2
        y = height / 2
        # 返回按钮的边界矩形
        return QRectF(x, y, width, height)

    def paint(self, painter, option, widget=None):

        painter.setRenderHint(QPainter.Antialiasing)

        # 外圈
        # painter.fill(self.boundingRect())

        # 内圈  一定要在外圈之后，需要覆盖
        pen = QPen(self.color, self.linewidth, Qt.DotLine)  # 边框
        brush = QBrush(self.color)  # 填充
        painter.setPen(pen)
        painter.setBrush(brush)
        painter.drawLine(self.point1, self.point2)



# 示例使用代码：
if __name__ == '__main__':

    from PyQt5.QtWidgets import QGraphicsScene, QGraphicsView, QApplication
    import sys
    import CircleButtons

    app = QApplication(sys.argv)
    scene = QGraphicsScene()

    button = CircleButtons.CircleButton(internalRadius=10, externalRadius=10, text='RX')  # 创建一个半径为50，颜色为红色的圆形按钮
    button.setPos(100, 100)  # 设置按钮位置
    # button.is_pressed.connect(lambda: print("Button clicked!"))  # 连接点击信号

    button1 = CircleButtons.CircleButton(internalRadius=10, externalRadius=10, text='RX')  # 创建一个半径为50，颜色为红色的圆形按钮
    button1.setPos(20, 50)  # 设置按钮位置

    line = DashLine(button.pos(), button1.pos())
    scene.addItem(line)

    scene.addItem(button)
    scene.addItem(button1)


    # line = DashLine(QPoint(0,0), QPoint(100, 100))



    view = QGraphicsView(scene)
    view.show()

    view.rotate(90)

    sys.exit(app.exec_())
