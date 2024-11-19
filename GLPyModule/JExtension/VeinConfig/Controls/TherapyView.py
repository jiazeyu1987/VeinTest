# from PyQt5.QtWidgets import QGraphicsItem, QGraphicsView, QGraphicsScene, QLabel
# from PyQt5.QtGui import QBrush, QPen, QFont, QColor, QRadialGradient, QPainter, QPolygon, QPolygonF, QImage, QPixmap
# from PyQt5.QtCore import QRectF, Qt, pyqtSignal, QPointF, QObject, QPoint
from qt import *
from Controls.CircleButtons import *
from Controls.DashLine import *
import slicer.util as util
import os


class TherapyView(QGraphicsView):
    def __init__(self, width=470, height=488, angle=0, parent=None):
        # QObject.__init__(self)
        # QGraphicsItem.__init__(self, parent)

        super(TherapyView, self).__init__(parent)
        self.viewscene = QGraphicsScene()
        self.viewscene.setSceneRect(0, 0, width, height)

        self.setScene(self.viewscene)

        self.viewwidth = width
        self.viewheight = height

        # self.resize(self.width, self.height)
        # self.setFixedSize(self.viewwidth, self.viewheight)

        self.rotate(angle)  # 设置整个View以一定的角度旋转
        self.internalRadius = 10
        self.totalPos = 0
        self.currentPos = 0
        self.posVector = []
        self.posVectorButtons = []
        self.name = "李明明"
        self.posName = "Vein 86 Seg 24"
        self.startX = 40
        self.startY = 197

        self.posHSpacing = -62
        self.posVSpacing = 80
        self.initPosNum = 7

        self.dashHlen = -self.posHSpacing - 2 * self.internalRadius
        self.dashVlen = 80 - 2 * self.internalRadius

        self.startDashX = self.startX + 2 * self.internalRadius + 2
        self.startDashY = self.startY + self.internalRadius

        # 注意这个endDashX、endDashY很重要，已经融入了递推公式里面
        self.endDashX = self.startX + self.internalRadius
        self.endDashY = self.startY

        self.dashFactor = -1

        self.setBackgroundBrush(Qt.black)
        self.showInfos()

    def addNewPos(self):

        _circle = CircleButton(internalRadius=self.internalRadius, externalRadius=self.internalRadius)
        circleButton = self.viewscene.addWidget(_circle)
        circleButton.setPos(self.startX, self.startY)

        self.totalPos += 1

        self.posVector.append(circleButton)  # 先装起来，备用
        self.posVectorButtons.append(_circle)
        # 更新button
        if self.totalPos % 7 == 1:
            self.posHSpacing *= -1

        self.startX += self.posHSpacing

        if self.totalPos % 7 == 0:
            self.startY = self.startY + self.posVSpacing
            self.startX -= self.posHSpacing

        if self.totalPos == 1:
            # self.viewscene.addWidget(_circle).setPos(self.startX, self.startY)
            x, y = _circle.setAsCurrentPos(True)
            circleButton.setPos(x, y)
            pass
        elif self.totalPos >= 2:  # 把最后两个连接起来

            # 更新dashLine
            if self.totalPos % 7 == 1:
                self.startDashX = self.endDashX + self.internalRadius * self.dashFactor
                self.startDashY = self.endDashY + self.internalRadius

                self.endDashX = self.startDashX
                self.endDashY = self.startDashY + self.dashVlen

            elif self.totalPos % 7 == 2:
                self.dashFactor *= -1

                self.startDashX = self.endDashX + self.internalRadius * self.dashFactor
                self.startDashY = self.endDashY + self.internalRadius

                self.endDashX = self.startDashX + self.dashHlen * self.dashFactor
                self.endDashY = self.startDashY

            else:
                self.startDashX = self.endDashX + self.internalRadius * 2 * self.dashFactor
                self.startDashY = self.endDashY

                self.endDashX = self.startDashX + self.dashHlen * self.dashFactor
                self.endDashY = self.startDashY

            dashLines = DashLine(
                startPos=QPoint(self.startDashX, self.startDashY),
                endPos=QPoint(self.endDashX, self.endDashY),
                color=QColor("#B1DAFF"),
                linewidth=2
            )
            self.viewscene.addItem(dashLines)

    def prePos(self):
        if self.currentPos > 0:
            x, y = self.posVectorButtons[self.currentPos].setAsCurrentPos(False)  # 先把当前的点，去选
            self.posVector[self.currentPos].setPos(x, y)
            self.currentPos -= 1
            x, y = self.posVectorButtons[self.currentPos].setAsCurrentPos(True)  # 选中
            self.posVector[self.currentPos].setPos(x, y)
            self.posVectorButtons[self.currentPos].update()  # 此处不调用，他会自动重绘

        self.update()

    def nextPos(self):
        new_flag = False
        if self.currentPos == len(self.posVector) - 1:
            self.addNewPos()
            new_flag = True
        x, y = self.posVectorButtons[self.currentPos].setAsCurrentPos(False)  # 先把当前的点，去选
        self.posVector[self.currentPos].setPos(x, y)
        self.currentPos += 1

        x, y = self.posVectorButtons[self.currentPos].setAsCurrentPos(True)  # 选中
        self.posVector[self.currentPos].setPos(x, y)
        self.posVectorButtons[self.currentPos].update()  # 此处不调用，他会自动重绘

        self.update()
        return new_flag

    def setCurrentPosTherapied(self):
        self.posVectorButtons[self.currentPos].setTherapy(True)
        self.posVectorButtons[self.currentPos].update()

    def setPosTherapied(self, pos):
        self.posVectorButtons[pos].setTherapy(True)
        self.posVectorButtons[pos].update()

    def showInfos(self):
        image = QPixmap(os.path.join(os.path.dirname(__file__), "patientPicture.png"))
        imgLabel = QLabel()
        imgLabel.setPixmap(image)
        imgLabel.setScaledContents(True)
        imgLabel.setFixedSize(32, 32)
        imgLabel.setStyleSheet('background-color:transparent;')
        self.viewscene.addWidget(imgLabel).setPos(12, 12)

        self.nameLabel = self.getNameLabel()
        self.posLabel = self.getPosNameLabel()
        self.pointLabel = self.getPointNameLabel()
        self.countLabel = self.getTherapyCountLabel()

    def setNameLabel(self, text):
        self.nameLabel.setText(text)

    def setPointLabel(self, text=None):
        if text is None:
            self.pointLabel.setText(f"Point {self.currentPos + 1}/{self.totalPos}")
        else:
            self.pointLabel.setText(text)

    def setTherapyCountLabel(self, count):
        self.countLabel.setText(f"Count {count}")

    def setPosNameLabel(self, text):
        self.posLabel.setText(text)

    def getNameLabel(self):

        textWidth = 200
        nameLabel = QLabel()
        nameLabel.setStyleSheet('background-color:transparent;color:white;')
        nameLabel.setScaledContents(True)
        # nameLabel.setFixedSize(100, 32)
        nameLabel.setFixedSize(textWidth, 32)
        nameLabel.setFont(QFont('Arial', 16))
        nameLabel.setAlignment(Qt.AlignLeft)
        nameLabel.setText(self.name)
        self.viewscene.addWidget(nameLabel).setPos(56, 12 + 4)
        return nameLabel

    def getPosNameLabel(self):
        textWidth = 250

        posLabel = QLabel()
        posLabel.setStyleSheet('background-color:transparent;color:white;')
        posLabel.setScaledContents(True)
        # posLabel.setFixedSize(100, 32)
        posLabel.setFixedSize(textWidth - 16, 32)
        posLabel.setFont(QFont('Arial', 18))
        posLabel.setAlignment(Qt.AlignLeft)
        posLabel.setText(self.posName)

        self.viewscene.addWidget(posLabel).setPos(12, 50)
        return posLabel

    def getPointNameLabel(self):
        textWidth = 250

        pointLabel = QLabel()
        pointLabel.setStyleSheet('background-color:transparent;color:white;')
        pointLabel.setScaledContents(True)
        # posLabel.setFixedSize(100, 32)
        pointLabel.setFixedSize(textWidth - 16, 32)
        pointLabel.setFont(QFont('Arial', 18))
        pointLabel.setAlignment(Qt.AlignRight | Qt.AlignCenter)
        pointLabel.setText(f"Point {self.currentPos}/{self.totalPos}")
        self.viewscene.addWidget(pointLabel).setPos(self.viewwidth - textWidth, 12)
        return pointLabel

    def getTherapyCountLabel(self):
        textWidth = 250

        pointLabel = QLabel()
        pointLabel.setStyleSheet('background-color:transparent;color:white;')
        pointLabel.setScaledContents(True)
        # posLabel.setFixedSize(100, 32)
        pointLabel.setFixedSize(textWidth - 16, 32)
        pointLabel.setFont(QFont('Arial', 18))
        pointLabel.setAlignment(Qt.AlignRight | Qt.AlignCenter)
        pointLabel.setText(f"Count 0")
        self.viewscene.addWidget(pointLabel).setPos(self.viewwidth - textWidth, 50)
        return pointLabel

    def isTherapyComplete(self):
        for i in range(self.totalPos):
            if not self.posVectorButtons[i].is_therapy:
                return False
        return True


if __name__ == '__main__':
    from PyQt5.QtWidgets import QApplication
    import sys

    app = QApplication(sys.argv)
    view = TherapyView(width=470, height=488)
    # view.resize(470, 488)

    view.addNewPos()
    view.addNewPos()
    view.addNewPos()
    view.addNewPos()
    view.addNewPos()
    view.addNewPos()
    view.addNewPos()
    view.addNewPos()
    view.addNewPos()
    view.addNewPos()
    view.addNewPos()
    view.addNewPos()
    view.addNewPos()
    view.addNewPos()
    view.addNewPos()
    view.addNewPos()
    view.addNewPos()
    view.addNewPos()
    view.addNewPos()

    view.nextPos()  # 第2个
    view.setCurrentPosTherapied()
    view.nextPos()
    view.nextPos()
    view.nextPos()
    view.nextPos()  # 第6个

    view.prePos()  # 第5个
    view.setCurrentPosTherapied()
    view.prePos()
    view.prePos()  # 第3个

    view.setCurrentPosTherapied()

    view.setPosNameLabel("Vein 1 Seg 2")
    view.setNameLabel("<name here>")
    view.setPointLabel()

    view.show()

    sys.exit(app.exec_())
