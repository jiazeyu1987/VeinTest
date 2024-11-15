import slicer, vtk
import slicer.util as util


class ConnectInfo:
    def __init__(self) -> None:
        self.uiWidget = slicer.util.loadUI(util.getModuleWidget("RDNDevice").resourcePath('UI/ConnectInfo.ui'))
        self.ui = slicer.util.childWidgetVariables(self.uiWidget)
        slicer.mrmlScene.AddObserver(util.ChangeToConnectState, self.OnChangeToConnectState)
        slicer.mrmlScene.AddObserver(util.ChangeToDisConnectState, self.OnChangeToDisConnectState)
        slicer.mrmlScene.AddObserver(util.ChangeFSMState, self.OnChangeFSMState)
        buttonlist = [self.ui.pushButton, self.ui.pushButton_2, self.ui.pushButton_3, self.ui.pushButton_4,
                      self.ui.pushButton_5, self.ui.pushButton_6]
        for button in buttonlist:
            self.set_disconnect_state(button)

        self.ui.pushButton_2.connect('clicked()', self.on_test_robot_init)

    def on_test_robot_init(self):
        print("on robot init")
        util.getModuleWidget("RequestStatus").send_cmd(f"Power, Send, 0, SetRobotControl, {0}, {0}, {0}, {85}")

    def set_connect_state(self, button):
        btn_stylesheet = button.styleSheet
        btn_stylesheet = btn_stylesheet + "QPushButton { color: #ffffff; background-color: #044d00}"
        button.setStyleSheet(btn_stylesheet)

    def set_disconnect_state(self, button):
        btn_stylesheet = button.styleSheet
        btn_stylesheet = btn_stylesheet + "QPushButton { color: #ffffff; background-color: #660000}"
        button.setStyleSheet(btn_stylesheet)

    @vtk.calldata_type(vtk.VTK_OBJECT)
    def OnChangeFSMState(self, caller, str_event, calldata):
        new_state = calldata.GetAttribute("value")
        if new_state == util.FSM_INITIAL_STATE:
            self.ui.label.setText("初始设备状态")
        if new_state == util.FSM_CHECK_DEVICE_STATE:
            self.ui.label.setText("检查设备状态")
        if new_state == util.FSM_READY_STATE:
            self.ui.label.setText("正常运行状态")
        if new_state == util.FSM_HAND_EYE_CALIBRATION_STATE:
            self.ui.label.setText("手眼标定状态")
        if new_state == util.FSM_TREATMENT_STATE:
            self.ui.label.setText("治疗状态")
        if new_state == util.FSM_END_STATE:
            self.ui.label.setText("结束状态")

    @vtk.calldata_type(vtk.VTK_OBJECT)
    def OnChangeToConnectState(self, caller, str_event, calldata):
        key = calldata.GetAttribute("value")
        print("OnChangeToConnectState:", key)
        # if key == "IME":
        #     self.set_connect_state(self.ui.pushButton)
        if key == "UR":
            self.set_connect_state(self.ui.pushButton_2)
        if key == "UltrasoundGenerator":
            self.set_connect_state(self.ui.pushButton_4)
        if key == "Power":
            self.set_connect_state(self.ui.pushButton_5)
        if key == "WaterControl":
            self.set_connect_state(self.ui.pushButton_3)
        # if key == "System":
        #     self.set_connect_state(self.ui.pushButton_6)

    @vtk.calldata_type(vtk.VTK_OBJECT)
    def OnChangeToDisConnectState(self, caller, str_event, calldata):
        key = calldata.GetAttribute("value")
        print("OnChangeToDisConnectState:", key)
        if key == "IME":
            self.set_disconnect_state(self.ui.pushButton)
        if key == "UR":
            self.set_disconnect_state(self.ui.pushButton_2)
        if key == "UltrasoundGenerator":
            self.set_disconnect_state(self.ui.pushButton_4)
        if key == "Power":
            self.set_connect_state(self.ui.pushButton_5)
        if key == "WaterControl":
            self.set_connect_state(self.ui.pushButton_3)
        if key == "System":
            self.set_connect_state(self.ui.pushButton_6)
