import sys
import slicer.util as util
# from PyQt5.QtWidgets import QGraphicsItem, QGraphicsView, QGraphicsScene, QApplication
# from PyQt5.QtGui import QBrush, QPen, QFont, QColor, QRadialGradient, QPainter, QPolygon, QPolygonF
# from PyQt5.QtCore import QRectF, Qt, pyqtSignal, QPointF, QObject, QPoin

from qt import *
import os

from Controls.ArrowLine import ArrowLine
from Controls.CircleButtons import CircleButton
from Controls.DashLine import DashLine
from Controls.DisplaceButton import DisplaceButton
from Controls.PerspectiveControlButton import *


class ControlView(QGraphicsView):

    def __init__(self, width=470, height=513, angle=0, parent=None):
        # QObject.__init__(self)
        # QGraphicsItem.__init__(self, parent)

        super(ControlView, self).__init__(parent)

        self.dashLineH = None
        self.dashLineV = None
        self.arrowLineH = None
        self.arrowLineV = None
        self.probeImage = None

        self.viewscene = QGraphicsScene()
        self.viewscene.setSceneRect(0, 0, width, height)
        self.setScene(self.viewscene)

        self.viewwidth = width
        self.viewheight = height

        # self.resize(self.width, self.height)

        self.rotate(angle)  # 设置整个View以一定的角度旋转

        self.createFronPerspective()
        self.createRightControlButtons()
        self.createPerspectiveControlButtons()

        self.setBackgroundBrush(Qt.black)
        self.setPerspective(mode='front')

        self._posZ.connect('pressed()', self._start_move_up)
        self._posZ.connect('released()', self._stop_move)
        self._negZ.connect('pressed()', self._start_move_down)
        self._negZ.connect('released()', self._stop_move)
        self._negX.connect('pressed()', self._start_move_right)
        self._negX.connect('released()', self._stop_move)
        self._posX.connect('pressed()', self._start_move_left)
        self._posX.connect('released()', self._stop_move)

        self._negY.connect('pressed()', self._start_move_back)
        self._negY.connect('released()', self._stop_move)
        self._posY.connect('pressed()', self._start_move_front)
        self._posY.connect('released()', self._stop_move)

        # TCP orientation
        # rx
        self._negRX.connect('pressed()', self._start_rotate_x_positive)
        self._negRX.connect('released()', self._stop_move)
        self._posRX.connect('pressed()', self._start_rotate_x_negative)
        self._posRX.connect('released()', self._stop_move)
        # ry
        self._negRY.connect('pressed()', self._start_rotate_y_positive)
        self._negRY.connect('released()', self._stop_move)
        self._posRY.connect('pressed()', self._start_rotate_y_negative)
        self._posRY.connect('released()', self._stop_move)
        # rz
        self._negRZ.connect('pressed()', self._start_rotate_z_positive)
        self._negRZ.connect('released()', self._stop_move)
        self._posRZ.connect('pressed()', self._start_rotate_z_negative)
        self._posRZ.connect('released()', self._stop_move)

    def createRightControlButtons(self):
        self._negZ = DisplaceButton(text='-', color=QColor("#396CCF"), angle=180, buttonW=48.13, buttonH=58.54,
                                    width=48.13, height=58.54)
        self.negZ = self.viewscene.addWidget(self._negZ)
        self.negZ.setPos(378, 393)

        self._posZ = DisplaceButton(text='+', color=QColor("#396CCF"), buttonW=48.13, buttonH=58.54, width=48.13,
                                    height=58.54)
        self.posZ = self.viewscene.addWidget(self._posZ)
        self.posZ.setPos(378, 145)

        self._negRZ = CircleButton(text='RZ-', color=QColor("#396CCF"), internalRadius=21, externalRadius=21)
        self.negRZ = self.viewscene.addWidget(self._negRZ)
        self.negRZ.setPos(336, 220)

        self._posRZ = CircleButton(text='RZ+', color=QColor("#396CCF"), internalRadius=21, externalRadius=21)
        self.posRZ = self.viewscene.addWidget(self._posRZ)
        self.posRZ.setPos(422, 220)

        # 数值的虚线
        # dashLineZ = DashLine(
        #     startPos=QPointF(int(self._posZ.pos.x() + self._posZ.width / 2), self._negRZ.pos.y()),
        #     endPos=QPointF(int(self._posZ.pos.x() + self._posZ.width / 2), self._negZ.pos.y() - 10),
        #     color=self._negRZ.color,
        # )
        #
        # self.viewscene.addItem(dashLineZ)
        #
        # # 横向的箭头线
        # startPos = QPointF(int(self._negRZ.pos.x() + self._negRZ.width / 2),
        #                    int(self._negRZ.pos.y() + 1.2 * self._negRZ.height))
        #
        # endPos = QPointF(int(self._posRZ.pos.x() + self._posRZ.width / 2),
        #                  int(self._posRZ.pos.y() + 1.2 * self._posRZ.height))
        #
        # controlPos = QPointF(int((startPos.x() + endPos.x()) / 2),
        #                      int((startPos.y() + endPos.y()) / 2 + 35))
        #
        # arrowRZ = ArrowLine(
        #     startpos=startPos,
        #     endpos=endPos,
        #     controlpos=controlPos,
        #     color=self._negRZ.color
        # )
        # self.viewscene.addItem(arrowRZ)

        self.addZAxisPicture()

    # 正视图
    def createFronPerspective(self, mode="front"):  # left right, front back
        self._negX = DisplaceButton(text='-', color=QColor("#F1675E"), buttonW=48.37, buttonH=58.74, width=73.52,
                                    height=75.69)
        self.negX = self.viewscene.addWidget(self._negX)
        # self.negX.setPos(self.width / 2, 0)

        self._posX = DisplaceButton(text='+', color=QColor("#F1675E"), buttonW=48.37, buttonH=58.74, width=73.74,
                                    height=75.73)
        self.posX = self.viewscene.addWidget(self._posX)
        # self.posX.setPos(self.width / 2, self.width)

        self._negY = DisplaceButton(text='-', color=QColor("#3CC181"))
        self.negY = self.viewscene.addWidget(self._negY)
        # self.negY.setPos(0, self.width / 2)

        self._posY = DisplaceButton(text='+', color=QColor("#3CC181"))
        self.posY = self.viewscene.addWidget(self._posY)
        # self.posY.setPos(self.width, self.width / 2)

        self._negRX = CircleButton(text='RX-', color=self._negX.color, internalRadius=21, externalRadius=21)
        self.negRX = self.viewscene.addWidget(self._negRX)
        # self.negRX.setPos(self.posX.pos().x() + self.posX.size().width() / 1.2,
        #                   self.posX.pos().y() - self.posX.size().width() / 2)

        self._posRX = CircleButton(text='RX+', color=self._negX.color, internalRadius=21, externalRadius=21)
        self.posRX = self.viewscene.addWidget(self._posRX)
        # self.posRX.setPos(self.posX.pos().x() - self.posX.size().width(),
        #                   self.posX.pos().y() - self.posX.size().width() / 2)
        self._negRY = CircleButton(text='RY-', color=self._negY.color, internalRadius=21, externalRadius=21)
        self.negRY = self.viewscene.addWidget(self._negRY)
        # self.negRY.setPos(self.negY.pos().x() + self.negY.size().width() / 1.2,
        #                   self.negY.pos().y() + self.negY.size().height() / 2)
        self._posRY = CircleButton(text='RY+', color=self._negY.color, internalRadius=21, externalRadius=21)
        self.posRY = self.viewscene.addWidget(self._posRY)
        # self.posRY.setPos(self.negY.pos().x() + self.negY.size().width(),
        #                   self.negY.pos().y() - self.negY.size().height() / 2)

    def onLeft(self):
        self.setPerspective("left")

    def onRight(self):
        self.setPerspective("right")

    def onFront(self):
        self.setPerspective("front")

    def onBack(self):
        self.setPerspective("back")

    def setPerspective(self, mode="front"):

        self.addProbePicture(mode)

        self.fronButton.setChoosed(False)
        self.backButton.setChoosed(False)
        self.leftButton.setChoosed(False)
        self.rightButton.setChoosed(False)

        if mode == "front":  # 根据ui的设计，从左上角开始，逆时针旋转计数
            self.fronButton.setChoosed(True)

            viewRotate = [self._negX, self._posY, self._posX, self._negY, ]  # rotate related
            viewPos = [self.negX, self.posY, self.posRX, self.posX, self.negRX, self.posRY, self.negY,
                       self.negRY]  # position related
            colors = [self._negX.color, self._negY.color]

        elif mode == ("back"):
            self.backButton.setChoosed(True)

            viewRotate = [self._posX, self._negY, self._negX, self._posY, ]
            viewPos = [self.posX, self.negY, self.negRX, self.negX, self.posRX, self.negRY, self.posY, self.posRY]
            colors = [self._negX.color, self._negY.color]

        elif mode == "left":
            self.leftButton.setChoosed(True)

            viewRotate = [self._posY, self._posX, self._negY, self._negX, ]  # rotate related
            viewPos = [self.posY, self.posX, self.posRY, self.negY, self.negRY, self.negRX, self.negX,
                       self.posRX]  # position related
            colors = [self._negY.color, self._negX.color]
        else:  # mode == "right":
            self.rightButton.choosed = True

            viewRotate = [self._negY, self._negX, self._posY, self._posX, ]  # rotate related
            viewPos = [self.negY, self.negX, self.negRY, self.posY, self.posRY, self.posRX, self.posX,
                       self.negRX]  # position related
            colors = [self._negY.color, self._negX.color]

        self.setButtonsPosition(viewRotate, viewPos)
        # self.createDashLines(viewPos, colors)
        # self.createArrowLines(viewPos, colors)

    def setButtonsPosition(self, viewRotate, viewPos):
        # 设置位置
        negxAngle = -36.51
        viewRotate[0].setRotation(negxAngle)
        viewRotate[2].setRotation(negxAngle + 180)

        negyAngle = -105
        viewRotate[3].setRotation(negyAngle)
        viewRotate[1].setRotation(negyAngle + 180)

        # 设置位置
        viewPos[0].setPos(26, 132)  # negX
        viewPos[3].setPos(234, 390)  # posX

        viewPos[4].setPos(142, 387)
        viewPos[2].setPos(271, 326)

        viewPos[6].setPos(3, 287)  # 3, 294是Ui上的，但是畫上圖之后，不適應
        viewPos[1].setPos(224, 230)  # 224, 236是Ui上的，

        viewPos[7].setPos(24, 232)
        viewPos[5].setPos(74, 366)

    def createDashLines(self, dashButtons=[], colors=[]):
        if self.dashLineH is not None:
            self.viewscene.removeItem(self.dashLineH)

        if self.dashLineV is not None:
            self.viewscene.removeItem(self.dashLineV)

        dashLineH = DashLine(
            startPos=QPointF(int(dashButtons[0].pos.x() + dashButtons[0].width - 6),
                             int(dashButtons[0].pos.y() + dashButtons[0].height)),
            endPos=QPointF((dashButtons[3].pos.x() + 6), dashButtons[3].pos.y()),
            color=colors[0],

        )
        self.dashLineH = self.viewscene.addItem(dashLineH)

        dashLineV = DashLine(
            startPos=QPointF(int(dashButtons[6].pos.x() + dashButtons[6].width),
                             int(dashButtons[6].pos.y() + dashButtons[6].height / 3)),
            endPos=QPointF(int(dashButtons[1].pos.x()),
                           int(dashButtons[1].pos.y() + dashButtons[1].height / 3 * 2)),
            color=colors[1],
        )

        self.dashLineV = self.viewscene.addItem(dashLineV)

    def createArrowLines(self, buttons=[], colors=[]):

        if self.arrowLineH is not None:
            self.viewscene.removeItem(self.arrowLineH)

        if self.arrowLineV is not None:
            self.viewscene.removeItem(self.arrowLineV)

        startPos = QPointF(int(buttons[5].pos.x() + buttons[5].width),
                           int(buttons[5].pos.y()))

        endPos = QPointF(int(buttons[7].pos.x() + buttons[7].width * 1.2),
                         int(buttons[7].pos.y() + buttons[7].height / 2))

        controlPos = QPointF(int((startPos.x() + endPos.x()) / 2 + 35),
                             int((startPos.y() + endPos.y()) / 2))

        arrowLineH = ArrowLine(
            startpos=startPos,
            endpos=endPos,
            controlpos=controlPos,
            color=colors[1]
        )
        self.arrowLineH = self.viewscene.addItem(arrowLineH)

        startPos = QPointF(int(buttons[2].pos.x() - 3),
                           int(buttons[2].pos.y()) - 3)

        endPos = QPointF(int(buttons[4].pos.x() + buttons[4].width / 2),
                         int(buttons[4].pos.y() - 10))

        controlPos = QPointF(int(endPos.x() + 4),
                             int(startPos.y() - 16))
        arrowLineV = ArrowLine(
            startpos=startPos,
            endpos=endPos,
            controlpos=controlPos,
            color=colors[0]
        )
        self.arrowLineV = self.viewscene.addItem(arrowLineV)

    def createPerspectiveControlButtons(self):

        label = QLabel()
        label.setStyleSheet('background-color:transparent;color:white;')
        label.setScaledContents(True)
        # posLabel.setFixedSize(100, 32)
        label.setFixedSize(48, 16)
        label.setFont(QFont('Arial', 16))
        label.setAlignment(Qt.AlignRight | Qt.AlignCenter)
        label.setText("视图:")
        self.viewscene.addWidget(label).setPos(12, 22)

        self.fronButton = ControlButton(text="front", radius=3)
        self.viewscene.addWidget(self.fronButton).setPos(64, 16)

        self.backButton = ControlButton(text="back", radius=0)
        self.viewscene.addWidget(self.backButton).setPos(143, 16)

        self.leftButton = ControlButton(text="left", radius=0)
        self.viewscene.addWidget(self.leftButton).setPos(222, 16)

        self.rightButton = ControlButton(text="right", radius=3)
        self.viewscene.addWidget(self.rightButton).setPos(301, 16)

        self.leftButton.pressed.connect(self.onLeft)
        self.rightButton.pressed.connect(self.onRight)
        self.fronButton.pressed.connect(self.onFront)
        self.backButton.pressed.connect(self.onBack)

    def addProbePicture(self, mode="front"):
        if self.probeImage is not None:
            self.viewscene.removeItem(self.probeImage)

        probeImage = QPixmap(os.path.join(os.path.dirname(__file__), f"{mode}Probe.png"))

        imgLabel = QLabel()
        imgLabel.setPixmap(probeImage)
        imgLabel.setScaledContents(True)
        # imgLabel.setFixedSize(90, 90)
        imgLabel.setFixedSize(196.45, 213.67)
        imgLabel.setStyleSheet('background-color:transparent;')
        self.probeImage = self.viewscene.addWidget(imgLabel)
        self.probeImage.setZValue(0)
        self.probeImage.setPos(66, 194)

    def addZAxisPicture(self, name="ZAxis.png"):
        zImage = QPixmap(os.path.join(os.path.dirname(__file__), name))

        imgLabel = QLabel()
        imgLabel.setPixmap(zImage)
        imgLabel.setScaledContents(True)
        # imgLabel.setFixedSize(90, 90)
        imgLabel.setFixedSize(103.63, 164)
        imgLabel.setStyleSheet('background-color:transparent;')
        self.viewscene.addWidget(imgLabel).setPos(354, 220)

    def _stop_move(self):
        # print("Stop called [py]")
        util.getModuleWidget("VeinConfigTop").clear_status_info()
        util.getModuleWidget("RequestStatus").send_cmd("UR, StopMove")

    def _start_move_up(self):
        # print("Move up called [py]")
        util.getModuleWidget("VeinConfigTop").set_status_info('机械臂移动', 'g')
        util.getModuleWidget("RequestStatus").send_cmd("UR, StartMoveUp")

    def _start_move_down(self):
        # print("Move down called [py]")
        util.getModuleWidget("VeinConfigTop").set_status_info('机械臂移动', 'g')
        util.getModuleWidget("RequestStatus").send_cmd("UR, StartMoveDown")

    def _start_move_right(self):
        util.getModuleWidget("VeinConfigTop").set_status_info('机械臂移动', 'g')
        util.getModuleWidget("RequestStatus").send_cmd("UR, StartMoveRight")

    def _start_move_left(self):
        util.getModuleWidget("VeinConfigTop").set_status_info('机械臂移动', 'g')
        util.getModuleWidget("RequestStatus").send_cmd("UR, StartMoveLeft")

    def _start_move_back(self):
        util.getModuleWidget("VeinConfigTop").set_status_info('机械臂移动', 'g')
        util.getModuleWidget("RequestStatus").send_cmd("UR, StartMoveBack")

    def _start_move_front(self):
        util.getModuleWidget("VeinConfigTop").set_status_info('机械臂移动', 'g')
        util.getModuleWidget("RequestStatus").send_cmd("UR, StartMoveFront")

    def _start_rotate_x_positive(self):
        util.getModuleWidget("VeinConfigTop").set_status_info('机械臂移动', 'g')
        util.getModuleWidget("RequestStatus").send_cmd("UR, StartRotateXPositive")

    def _start_rotate_x_negative(self):
        util.getModuleWidget("VeinConfigTop").set_status_info('机械臂移动', 'g')
        util.getModuleWidget("RequestStatus").send_cmd("UR, StartRotateXNegative")

    def _start_rotate_y_positive(self):
        util.getModuleWidget("VeinConfigTop").set_status_info('机械臂移动', 'g')
        util.getModuleWidget("RequestStatus").send_cmd("UR, StartRotateYPositive")

    def _start_rotate_y_negative(self):
        util.getModuleWidget("VeinConfigTop").set_status_info('机械臂移动', 'g')
        util.getModuleWidget("RequestStatus").send_cmd("UR, StartRotateYNegative")

    def _start_rotate_z_positive(self):
        # print("Rotate Z+ called [py]")
        util.getModuleWidget("VeinConfigTop").set_status_info('机械臂移动', 'g')
        util.getModuleWidget("RequestStatus").send_cmd("UR, StartRotateZPositive")

    def _start_rotate_z_negative(self):
        # print("Rotate Z- called [py]")
        util.getModuleWidget("VeinConfigTop").set_status_info('机械臂移动', 'g')
        util.getModuleWidget("RequestStatus").send_cmd("UR, StartRotateZNegative")

    def setFrontPerspective(self):
        print("setfront view")
        pass

    def setLeftPerspective(self):
        pass

    def setRightPerspective(self):
        pass

    def setBackPerspective(self):
        pass


if __name__ == '__main__':
    app = QApplication(sys.argv)
    view = ControlView()
    view.show()


    def onClicked():
        print("clicked")


    def onReleased():
        print("released")


    view._negX.clicked.connect(onClicked)
    view._posX.clicked.connect(onReleased)

    sys.exit(app.exec_())
