import slicer.util as util
import slicer, qt
import os


class UltraSoundColorBar:
    uiWidget = None
    ui = None
    parent = None
    geometry = None

    imageB_Path = None
    imagePDI_Path = None
    imageB_Label = None
    imagePDI_Label = None

    def __init__(self, main):
        # 获取当前文件的绝对路径
        current_file_path = os.path.abspath(__file__)
        # 获取当前文件所在目录的上一层目录
        parent_directory = os.path.dirname(os.path.dirname(current_file_path))
        # 其他插件也会用到这个弹窗，所以不能通过parent加载ui文件
        self.uiWidget = util.loadUI(parent_directory + '/Resources/UI/ColorBarUI.ui')
        # self.uiWidget = util.loadUI(main.resourcePath('UI/ColorBarUI.ui'))
        self.ui = util.childWidgetVariables(self.uiWidget)
        self.parent = qt.QWidget()
        self.parent.setParent(slicer.app.layoutManager().sliceWidget("Red"))
        util.addWidget2(self.parent, self.uiWidget)

        self.imageB_Path = main.resourcePath('UI/colorbar1.jpg')
        self.imagePDI_Path = main.resourcePath('UI/colorbar2.jpg')
        self.imageB_Label = qt.QLabel()
        self.imagePDI_Label = qt.QLabel()
        util.add_pixelmap_to_label(self.imageB_Path, self.imageB_Label)
        util.add_pixelmap_to_label(self.imagePDI_Path, self.imagePDI_Label)
        util.singleShot(100, self.initLater)

    def initLater(self):
        width = 30
        height = util.ultra_height / 2
        posX = util.ultra_x
        posY = util.ultra_y + height / 2
        self.ui.label_2.setFixedSize(width, height - 30)
        self.imageB_Label.setFixedSize(width, height - 30)
        self.imagePDI_Label.setFixedSize(width, height - 30)
        self.parent.geometry = qt.QRect(posX, posY, width, height)

    def show(self, imageType):
        self.switch_to_mode(imageType)
        self.parent.show()

    def hide(self):
        self.parent.hide()

    def switch_to_mode(self, imageType):
        if imageType == "MODE_BMODE":
            util.addWidgetOnly(self.ui.label_2, self.imageB_Label)
        else:
            util.addWidgetOnly(self.ui.label_2, self.imagePDI_Label)
