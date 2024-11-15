import slicer.util as util
import slicer, qt
import os


class InfoLabel:
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
        self.uiWidget = util.loadUI(parent_directory + '/Resources/UI/InfoLabel.ui')
        # self.uiWidget = util.loadUI(main.resourcePath('UI/InfoLabel.ui'))
        self.ui = util.childWidgetVariables(self.uiWidget)
        self.uiWidget.setParent(slicer.app.layoutManager().sliceWidget("Red"))
        self.logo_path = main.resourcePath('UI/logo.png')

        util.singleShot(100, self.initLater)

    def initLater(self):
        width = util.ultra_width
        height = 120
        posX = util.ultra_x
        posY = util.ultra_y - 120
        self.uiWidget.geometry = qt.QRect(posX, posY, width, height)
        pixelmap = qt.QPixmap(self.logo_path)
        self.ui.label_logo.setPixmap(pixelmap)
        self.ui.label_logo.setFixedSize(80, 80)

    def update_info(self, info):
        self.ui.lable_info.text = info + ",\nF:xx"

    def show(self):
        self.uiWidget.show()

    def hide(self):
        self.uiWidget.hide()
