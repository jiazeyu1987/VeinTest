import imp
import os
from re import A
from tabnanny import check
from time import sleep
import unittest
import logging
import vtk, qt, ctk, slicer, math
from slicer.ScriptedLoadableModule import *
from slicer.util import VTKObservationMixin
import slicer.util as util
import SlicerWizard.Utilities as su
import numpy as np
from Base.JBaseExtension import JBaseExtensionWidget


#
# JPowerControl
#

class JPowerControl(ScriptedLoadableModule):

    def __init__(self, parent):
        ScriptedLoadableModule.__init__(self, parent)
        self.parent.title = "JPowerControl"  # TODO: make this more human readable by adding spaces
        self.parent.categories = [
            "JPlugins"]  # TODO: set categories (folders where the module shows up in the module selector)
        self.parent.dependencies = []  # TODO: add here list of module names that this module requires
        self.parent.contributors = ["jia ze yu"]  # TODO: replace with "Firstname Lastname (Organization)"
        # TODO: update with short description of the module and a link to online module documentation
        self.parent.helpText = """

"""
        # TODO: replace with organization, grant and thanks
        self.parent.acknowledgementText = """

"""


#
# JSystemInfoWidget
#

class JPowerControlWidget(JBaseExtensionWidget):
    unit = None

    def setup(self):
        super().setup()
        self.ui.tabWidget.tabBar().hide()
        self.unit = util.getModuleWidget("JUSBConnector").create_widget(1122, 22352, "Power")
        util.addWidget2(self.ui.unit_container, self.unit.uiwidget)
        # logpath = self.resourcePath('log/communicate.log').replace("\\","/")
        # util.singleShot(100,lambda:util.getModuleWidget("RequestStatus").send_cmd(f"Power, OpenAndShowLog, {logpath}"))

    def init_ui(self):
        self.ui.btn_setting_fan.connect('clicked()', self.on_setting_fan)
        self.ui.btn_mcu.connect('clicked()', self.on_reset_mcu)
        self.ui.btn_ndi_power.connect('clicked()', self.on_ndi_power)
        # self.ui.btn_pc_power.connect('clicked()',self.on_pc_power)
        self.ui.btn_water_power.connect('clicked()', self.on_water_power)
        self.ui.btn_robot_power.connect('clicked()', self.on_robot_power)
        self.ui.btn_pa_power.connect('clicked()', self.on_pa_power)
        self.ui.btn_robot_control_1.connect('clicked()', self.on_robot_control_1)
        self.ui.btn_robot_control_2.connect('clicked()', self.on_robot_control_2)
        self.ui.btn_robot_control_3.connect('clicked()', self.on_robot_control_3)
        self.ui.btn_robot_control_4.connect('clicked()', self.on_robot_control_4)
        slicer.mrmlScene.AddObserver(util.ReconnectEvent, self.OnReconnectEvent)

    @vtk.calldata_type(vtk.VTK_OBJECT)
    def OnReconnectEvent(self, caller, str_event, calldata):
        val = calldata.GetAttribute("value")
        if val == "Power":
            print("on reconnect with power")
            self.unit.on_connect()
            self.unit.change_software_status()

    def get_num(self, num):
        def get_ops(num):
            if num == 170:
                return 85
            elif num == 85:
                return 170

        t1 = self.ui.btn_robot_control_1.text
        t2 = self.ui.btn_robot_control_2.text
        t3 = self.ui.btn_robot_control_3.text
        t4 = self.ui.btn_robot_control_4.text

        if t1 == "关闭":
            n1 = 85
        else:
            n1 = 170

        if t2 == "关闭":
            n2 = 85
        else:
            n2 = 170

        if t3 == "关闭":
            n3 = 85
        else:
            n3 = 170

        if t4 == "关闭":
            n4 = 85
        else:
            n4 = 170

        if num == 1:
            n1 = get_ops(n1)
        if num == 2:
            n2 = get_ops(n2)
        if num == 3:
            n3 = get_ops(n3)
        if num == 4:
            n4 = get_ops(n4)

        return n1, n2, n3, n4

    def on_robot_control_1(self):
        n1, n2, n3, n4 = self.get_num(1)
        util.getModuleWidget("RequestStatus").send_cmd(f"Power, Send, 0, SetRobotControl, {n1}, {n2}, {n3}, {n4}")

    def on_robot_control_2(self):
        n1, n2, n3, n4 = self.get_num(2)
        util.getModuleWidget("RequestStatus").send_cmd(f"Power, Send, 0, SetRobotControl, {n1}, {n2}, {n3}, {n4}")

    def on_robot_control_3(self):
        n1, n2, n3, n4 = self.get_num(3)
        util.getModuleWidget("RequestStatus").send_cmd(f"Power, Send, 0, SetRobotControl, {n1}, {n2}, {n3}, {n4}")

    def on_robot_control_4(self):
        n1, n2, n3, n4 = self.get_num(4)
        util.getModuleWidget("RequestStatus").send_cmd(f"Power, Send, 0, SetRobotControl, {n1}, {n2}, {n3}, {n4}")

    def on_pa_power(self):
        if self.ui.btn_pa_power.text == "关闭":
            util.getModuleWidget("RequestStatus").send_cmd(f"Power, Send, 0, PAPower, 170")
        else:
            util.getModuleWidget("RequestStatus").send_cmd(f"Power, Send, 0, PAPower, 85")

    def on_robot_power(self):
        if self.ui.btn_robot_power.text == "关闭":
            util.getModuleWidget("RequestStatus").send_cmd(f"Power, Send, 0, RobotPower, 170")
        else:
            util.getModuleWidget("RequestStatus").send_cmd(f"Power, Send, 0, RobotPower, 85")

    def on_water_power(self):
        if self.ui.btn_water_power.text == "关闭":
            util.getModuleWidget("RequestStatus").send_cmd(f"Power, Send, 0, WaterPower, 170")
        else:
            util.getModuleWidget("RequestStatus").send_cmd(f"Power, Send, 0, WaterPower, 85")

    def on_pc_power(self):
        if self.ui.btn_pc_power.text == "关闭":
            util.getModuleWidget("RequestStatus").send_cmd(f"Power, Send, 0, PCPower, 170")
        else:
            util.getModuleWidget("RequestStatus").send_cmd(f"Power, Send, 0, PCPower, 85")

    def on_ndi_power(self):
        if self.ui.btn_ndi_power.text == "关闭":
            util.getModuleWidget("RequestStatus").send_cmd(f"Power, Send, 0, NDIPower, 170")
        else:
            util.getModuleWidget("RequestStatus").send_cmd(f"Power, Send, 0, NDIPower, 85")

    def on_reset_mcu(self):
        util.getModuleWidget("RequestStatus").send_cmd(f"Power, Send, 0, ResetMCU, 1")

    def on_setting_fan(self):
        txt = self.ui.le_fan.text
        power = int(txt)
        if power < 20 or power > 100:
            util.showWarningText("数值需要设置在20~100之间")
        util.getModuleWidget("RequestStatus").send_cmd(f"Power, Send, 0, SetFan, {power}")

    def tickEvent(self, value):
        self.unit.tickEvent(value)
        map_info = {}
        info_list_str = value.split("*V* ")
        for row in info_list_str:
            if row == "":
                continue
            key_value_pair_list = row.split("*U* ")
            assert (len(key_value_pair_list) == 2)
            key = key_value_pair_list[0]
            value = key_value_pair_list[1]
            map_info[key] = value

        if "heart_beat" in map_info and map_info["heart_beat"] != "nan":
            self.analyse_heart_beat(map_info["heart_beat"])
        if "software_status" in map_info and map_info["software_status"] != "nan":
            self.set_software_status_sub(map_info["software_status"])

    def set_software_status_sub(self, value):
        if value == "-1":
            return
        elif value == "-2":
            return
        else:
            infolist = value.split(" ")
            if int(infolist[5], 16) == 0:
                self.ui.widget_2.setEnabled(False)
            elif int(infolist[5], 16) == 1:
                self.ui.widget_2.setEnabled(True)

    def set_button_state(self, btn, state):
        if state == 0:
            btn.setText("关闭")
            btn.setStyleSheet("color: red;")
        else:
            btn.setText("打开")
            btn.setStyleSheet("color: green;")

    def analyse_heart_beat(self, stringlist):
        chararray = stringlist.split(" ")
        if len(chararray) != 65:
            return
        head = chararray[0]
        packet_type = chararray[1]
        if packet_type != "0x02":
            print("UUUUUUUU:", stringlist)
            return
        operator_type = chararray[2]
        packet_number = chararray[3]
        packet_number2 = chararray[4]
        tail = chararray[63]
        flag = chararray[64]

        software_status = chararray[5]
        motherboard_power = chararray[6]
        PA_Status = chararray[7]
        emergency_stop_state = chararray[8]
        emergency_stop_state_int = int(emergency_stop_state, 16)
        robot1 = chararray[9]
        robot2 = chararray[10]
        robot3 = chararray[11]
        transformer = chararray[12]
        fan_speed_h = chararray[13]
        fan_speed_l = chararray[14]
        machine_temp_h = chararray[15]
        machine_temp_l = chararray[16]
        power_status = chararray[17]
        robot_status = chararray[18]
        power_off = chararray[19]
        power_off_int = int(power_off, 16)
        if power_off_int == 11:
            res = util.messageBox("确定要关闭系统吗", windowTitle="提示")
            if res == 0:
                return
            print("is closing system")
            import subprocess
            subprocess.call('shutdown /s /t 1')
            # util.quit()
            return
        self.ui.lineEdit_2.setText("主板电源:" + motherboard_power)
        self.ui.lineEdit_3.setText("功放故障:" + PA_Status)
        self.ui.lineEdit_4.setText("急停状态:" + emergency_stop_state)
        self.ui.lineEdit_5.setText("机器人输出:" + robot1 + " " + robot2 + " " + robot3)
        self.ui.lineEdit_6.setText("变压器异常:" + transformer)
        fan_speed = int(fan_speed_h, 16) * 255 + int(fan_speed_l, 16)
        self.ui.lineEdit_7.setText("风扇速度:" + fan_speed.__str__())
        machine_temp = int(machine_temp_h, 16) * 255 + int(machine_temp_l, 16)
        self.ui.lineEdit_8.setText("机器温度:" + machine_temp.__str__())

        power_status = int(power_status, 16)

        mask = 1 << 0
        PA_power = power_status & mask != 0
        self.ui.lineEdit_9.setText("功放电源:" + PA_power.__str__())
        if PA_power:
            self.set_button_state(self.ui.btn_pa_power, 0)
        else:
            self.set_button_state(self.ui.btn_pa_power, 1)

        mask = 1 << 1
        robot_arm_power = power_status & mask != 0
        self.ui.lineEdit_10.setText("机械臂电源:" + robot_arm_power.__str__())
        if robot_arm_power:
            self.set_button_state(self.ui.btn_robot_power, 0)
        else:
            self.set_button_state(self.ui.btn_robot_power, 1)

        mask = 1 << 2
        pc_power = power_status & mask != 0
        self.ui.lineEdit_11.setText("主机电源:" + pc_power.__str__())
        if pc_power:
            self.set_button_state(self.ui.btn_pc_power, 0)
        else:
            self.set_button_state(self.ui.btn_pc_power, 1)

        mask = 1 << 3
        water_power = power_status & mask != 0
        self.ui.lineEdit_12.setText("水处理电源:" + water_power.__str__())
        if water_power:
            self.set_button_state(self.ui.btn_water_power, 0)
        else:
            self.set_button_state(self.ui.btn_water_power, 1)

        mask = 1 << 4
        ndi_power = power_status & mask != 0
        self.ui.lineEdit_13.setText("双目电源:" + ndi_power.__str__())
        if ndi_power:
            self.set_button_state(self.ui.btn_ndi_power, 0)
        else:
            self.set_button_state(self.ui.btn_ndi_power, 1)

        self.ui.lineEdit_14.setText("机器人状态:" + robot_status)
        robot_status = int(robot_status, 16)
        mask = 1 << 0
        robot_control_1 = robot_status & mask != 0
        if robot_control_1:
            self.set_button_state(self.ui.btn_robot_control_1, 0)
        else:
            self.set_button_state(self.ui.btn_robot_control_1, 1)

        mask = 1 << 1
        robot_control_2 = robot_status & mask != 0
        if robot_control_2:
            self.set_button_state(self.ui.btn_robot_control_2, 0)
        else:
            self.set_button_state(self.ui.btn_robot_control_2, 1)

        mask = 1 << 2
        robot_control_3 = robot_status & mask != 0
        if robot_control_3:
            self.set_button_state(self.ui.btn_robot_control_3, 0)
        else:
            self.set_button_state(self.ui.btn_robot_control_3, 1)

        mask = 1 << 3
        robot_control_4 = robot_status & mask != 0
        if robot_control_4:
            self.set_button_state(self.ui.btn_robot_control_4, 0)
        else:
            self.set_button_state(self.ui.btn_robot_control_4, 1)

        if emergency_stop_state_int == 1:
            util.send_fsm_event("emergency_stop_state_1")
