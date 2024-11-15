import slicer
import slicer.util as util
import os
import qt


# 嵌入ui已有widget
class URController:
    def __init__(self):
        # 获取当前文件的绝对路径
        current_file_path = os.path.abspath(__file__)
        # 获取当前文件所在目录的上一层目录
        parent_directory = os.path.dirname(os.path.dirname(current_file_path))
        # 其他插件也会用到这个弹窗，所以不能通过parent加载ui文件
        self.uiWidget = slicer.util.loadUI(parent_directory + '/Resources/UI/URController.ui')
        self.ui = util.childWidgetVariables(self.uiWidget)

        self._init_ui()

    def _init_ui(self):
        # TCP position
        self.ui.btn_move_up.connect('pressed()', self.start_move_up)
        self.ui.btn_move_up.connect('released()', self.stop_move)
        self.ui.btn_move_down.connect('pressed()', self.start_move_down)
        self.ui.btn_move_down.connect('released()', self.stop_move)
        self.ui.btn_move_right.connect('pressed()', self.start_move_right)
        self.ui.btn_move_right.connect('released()', self.stop_move)
        self.ui.btn_move_left.connect('pressed()', self.start_move_left)
        self.ui.btn_move_left.connect('released()', self.stop_move)
        self.ui.btn_move_back.connect('pressed()', self.start_move_back)
        self.ui.btn_move_back.connect('released()', self.stop_move)
        self.ui.btn_move_front.connect('pressed()', self.start_move_front)
        self.ui.btn_move_front.connect('released()', self.stop_move)

        # TCP orientation
        # rx
        self.ui.btn_rotate_x_positive.connect('pressed()', self.start_rotate_x_positive)
        self.ui.btn_rotate_x_positive.connect('released()', self.stop_move)
        self.ui.btn_rotate_x_negative.connect('pressed()', self.start_rotate_x_negative)
        self.ui.btn_rotate_x_negative.connect('released()', self.stop_move)
        # ry
        self.ui.btn_rotate_y_positive.connect('pressed()', self.start_rotate_y_positive)
        self.ui.btn_rotate_y_positive.connect('released()', self.stop_move)
        self.ui.btn_rotate_y_negative.connect('pressed()', self.start_rotate_y_negative)
        self.ui.btn_rotate_y_negative.connect('released()', self.stop_move)
        # rz
        self.ui.btn_rotate_z_positive.connect('pressed()', self.start_rotate_z_positive)
        self.ui.btn_rotate_z_positive.connect('released()', self.stop_move)
        self.ui.btn_rotate_z_negative.connect('pressed()', self.start_rotate_z_negative)
        self.ui.btn_rotate_z_negative.connect('released()', self.stop_move)

    def start_move_up(self):
        print("Move up called [py]")
        util.getModuleWidget("RequestStatus").send_cmd("UR, StartMoveUp")

    def start_move_down(self):
        print("Move down called [py]")
        util.getModuleWidget("RequestStatus").send_cmd("UR, StartMoveDown")

    def start_move_right(self):
        self.ui.btn_move_right.setFocus()  # 手动设置焦点
        # 使用 isDown() 方法获取按钮的按压状态
        if self.ui.btn_move_right.isDown():
            print("right Button is pressed")
        else:
            print("right Button is not pressed")
        util.getModuleWidget("RequestStatus").send_cmd("UR, StartMoveRight")

    def start_move_left(self):
        util.getModuleWidget("RequestStatus").send_cmd("UR, StartMoveLeft")

    def start_move_back(self):
        util.getModuleWidget("RequestStatus").send_cmd("UR, StartMoveBack")

    def start_move_front(self):
        util.getModuleWidget("RequestStatus").send_cmd("UR, StartMoveFront")

    def stop_move(self):
        print("Stop called [py]")
        util.getModuleWidget("RequestStatus").send_cmd("UR, StopMove")

    def start_rotate_x_positive(self):
        util.getModuleWidget("RequestStatus").send_cmd("UR, StartRotateXPositive")

    def start_rotate_x_negative(self):
        util.getModuleWidget("RequestStatus").send_cmd("UR, StartRotateXNegative")

    def start_rotate_y_positive(self):
        util.getModuleWidget("RequestStatus").send_cmd("UR, StartRotateYPositive")

    def start_rotate_y_negative(self):
        util.getModuleWidget("RequestStatus").send_cmd("UR, StartRotateYNegative")

    def start_rotate_z_positive(self):
        print("Rotate Z+ called [py]")
        util.getModuleWidget("RequestStatus").send_cmd("UR, StartRotateZPositive")

    def start_rotate_z_negative(self):
        print("Rotate Z- called [py]")
        util.getModuleWidget("RequestStatus").send_cmd("UR, StartRotateZNegative")
