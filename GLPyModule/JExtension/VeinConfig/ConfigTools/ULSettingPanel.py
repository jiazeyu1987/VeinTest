import os
import slicer.util as util


# 弹窗设置，区别于嵌入ui已有widget
class ULSettingPanel:
    def __init__(self):
        # 获取当前文件的绝对路径
        current_file_path = os.path.abspath(__file__)
        # 获取当前文件所在目录的上一层目录
        parent_directory = os.path.dirname(os.path.dirname(current_file_path))
        # 其他插件也会用到这个弹窗，所以不能通过parent加载ui文件
        self.uiWidget = util.loadUI(parent_directory + '/Resources/UI/ULSettingPanel.ui')
        self.ui = util.childWidgetVariables(self.uiWidget)

    def show(self):
        self.uiWidget.show()

    def hide(self):
        self.uiWidget.hide()
