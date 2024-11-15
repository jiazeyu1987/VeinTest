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
import time


#
# JWaterControl
#

class JWaterControl(ScriptedLoadableModule):

    def __init__(self, parent):
        ScriptedLoadableModule.__init__(self, parent)
        self.parent.title = "JWaterControl"  # TODO: make this more human readable by adding spaces
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

class JWaterControlWidget(JBaseExtensionWidget):
    unit = None

    def setup(self):
        super().setup()
        self.ui.tabWidget.tabBar().hide()
        self.unit = util.getModuleWidget("JUSBConnector").create_widget(0x0477, 0x5750, "WaterControl")
        util.addWidget2(self.ui.unit_container, self.unit.uiwidget)
        # logpath = self.resourcePath('log/communicate.log').replace("\\","/")
        # util.singleShot(100,lambda:util.getModuleWidget("RequestStatus").send_cmd(f"WaterControl, OpenAndShowLog, {logpath}"))

        self.water_pump_direction = "0x00"
        self.water_pump_speed = "0x05"
        self.water_pump_status = "0xAA"

        self.oxygen_auto_control_status = 170

        self.counts = {'fan_speed': 0, 'water_bladder_temp': 0, 'press_value': 0, 'make_cold_fan_speed': 0,
                       'cacuum_pump': 0}

    def init_ui(self):
        self.ui.btn_mcu.connect('clicked()', self.on_reset_mcu)
        self.ui.btn1.connect('clicked()', self.on_set_fan_speed)
        self.ui.pushButton.connect('clicked()', self.on_set_water_pump_speed)
        self.ui.pushButton_2.connect('clicked()', self.on_set_cacuum_speed)
        self.ui.pushButton_4.connect('clicked()', self.on_set_water_box_temp)
        self.ui.pushButton_5.connect('clicked()', self.open_colding_fan)
        self.ui.pushButton_8.connect('clicked()', self.close_colding_fan)
        self.ui.pushButton_9.connect('clicked()', self.close_24V_power)
        self.ui.pushButton_7.connect('clicked()', self.open_24V_power)
        self.ui.pushButton_10.connect('clicked()', self.close_valve_power)
        self.ui.pushButton_11.connect('clicked()', self.open_valve_power)
        self.ui.pushButton_16.connect('clicked()', self.back_to_origin)
        self.ui.btn_compressor.connect('clicked()', self.on_set_compressor)
        self.ui.btn_warm_manual.connect('clicked()', self.warm_manual)
        self.ui.pushButton_6.connect('clicked()', self.on_set_step_paras)
        self.ui.pushButton_13.connect('clicked()', self.on_set_oxygen)
        self.ui.btn_fill_water.connect('clicked()', self.on_fill_water)
        self.ui.btn_drain_water.connect('clicked()', self.on_drain_water)
        self.ui.btn_stop.connect('clicked()', self.on_stop)
        self.ui.btn_auto_control.connect('clicked()', self.on_oxygen_auto_control)
        self.ui.btn_set_reference_temp.connect('clicked()', self.on_set_reference_temp)
        self.ui.btn_set_water_direction.connect('clicked()', self.on_set_water_direction)
        self.ui.btn_set_water_status.connect('clicked()', self.on_set_water_status)

        # 设置按钮的样式表，确保在选中状态时不显示为灰色
        self.ui.btn_auto_control.setStyleSheet("""
            QPushButton:checked {
                background-color: lightblue;
                color: black;
            }
            QPushButton {
                background-color: white;
                color: black;
            }
        """)
        slicer.mrmlScene.AddObserver(util.ReconnectEvent, self.OnReconnectEvent)

        self.compressor_fault_codes = ['', '硬件检测电流故障', '软件检测电流故障', '驱动器过温保护',
                                       '输入电压低于设定规范', '输入电压高于设定规范', '定位启动失败',
                                       '运行中电机堵转或启动失败', '缺相错误']

    @vtk.calldata_type(vtk.VTK_OBJECT)
    def OnReconnectEvent(self, caller, str_event, calldata):
        val = calldata.GetAttribute("value")
        if val == "WaterControl":
            print("on reconnect with WaterControl")
            self.unit.on_connect()
            self.unit.change_software_status()

    def on_set_oxygen(self):
        txt = self.ui.lineEdit_14.text
        density = float(txt)
        if not (0 <= density <= 100):
            util.showWarningText("数值需要设置在0~100之间")
            return
        bytes, intbytes = util.convert_float_to_bytes(density)
        adjust = self.ui.comboBox_3.currentIndex + 1
        util.getModuleWidget("RequestStatus").send_cmd(
            f"WaterControl, Send, 0, SetOxygen, {intbytes[0]}, {intbytes[1]}, {intbytes[2]}, {intbytes[3]}, {adjust}, {self.oxygen_auto_control_status}")

    def on_oxygen_auto_control(self):
        check_status = self.ui.btn_auto_control.isChecked()
        if check_status:
            self.oxygen_auto_control_status = 85
            return
        self.oxygen_auto_control_status = 170

    def int_to_hex_byte_array(self, integer):
        # 确保整数可以用32位表示
        if integer < 0 or integer > 0xFFFFFFFF:
            raise ValueError("整数超出了可以用4个字节表示的范围")

        # 将整数转换为4字节的字节序列，使用大端表示
        bytes_representation = integer.to_bytes(4, byteorder='big')

        # 将字节序列转换为16进制表示
        hex_representation = bytes_representation.hex()

        # 将16进制字符串分割成长度为2的子字符串，形成一个数组
        hex_byte_array = [hex_representation[i:i + 2] for i in range(0, len(hex_representation), 2)]

        return hex_byte_array

    def hex_byte_array_to_int_array(self, hex_byte_array):
        # 将每个16进制字符串元素转换为整数，并存储在新的数组中
        int_array = [int(hex_byte, 16) for hex_byte in hex_byte_array]
        return int_array

    def on_set_step_paras(self):
        speed = self.ui.comboBox.currentIndex
        direction = self.ui.comboBox_2.currentIndex
        txt = self.ui.lineEdit_3.text
        value = int(txt)
        if not (0 <= value <= 10):
            util.showWarningText("数值需要设置在0~10之间")
            return
        circles = value * 6400
        hex_byte_array = self.int_to_hex_byte_array(circles)
        int_array = self.hex_byte_array_to_int_array(hex_byte_array)
        self.step_paras_status = 85
        util.getModuleWidget("RequestStatus").send_cmd(
            f"WaterControl, Send, 0, SetStepParas, {speed}, {direction}, {int_array[0]}, {int_array[1]}, {int_array[2]}, {int_array[3]}, {self.step_paras_status}")

    def back_to_origin(self):
        util.getModuleWidget("RequestStatus").send_cmd(f"WaterControl, Send, 0, SetVMotorOrigin, 85")

    def open_valve_power(self):
        util.getModuleWidget("RequestStatus").send_cmd(f"WaterControl, Send, 0, SetValve, 85")

    def close_valve_power(self):
        util.getModuleWidget("RequestStatus").send_cmd(f"WaterControl, Send, 0, SetValve, 170")

    def open_24V_power(self):
        util.getModuleWidget("RequestStatus").send_cmd(f"WaterControl, Send, 0, Set24VPower, 85")

    def close_24V_power(self):
        util.getModuleWidget("RequestStatus").send_cmd(f"WaterControl, Send, 0, Set24VPower, 170")

    def open_colding_fan(self):
        util.getModuleWidget("RequestStatus").send_cmd(f"WaterControl, Send, 0, SetColdFanPower, 64, 85")

    def close_colding_fan(self):
        util.getModuleWidget("RequestStatus").send_cmd(f"WaterControl, Send, 0, SetColdFanPower, 0, 170")

    def warm_manual(self):
        txt = self.ui.lineEdit_31.text
        speed_ratio = int(txt)
        if not (0 <= speed_ratio <= 100):
            util.showWarningText("数值需要设置在0~100之间")
            return
        self.open_status = 85
        if 0 == speed_ratio:
            self.open_status = 170
        util.getModuleWidget("RequestStatus").send_cmd(
            f"WaterControl, Send, 0, ManualHeating, {speed_ratio}, {self.open_status}")

    def on_set_compressor(self):
        txt = self.ui.lineEdit_29.text
        speed = int(txt)
        if not (0 <= speed <= 6000):
            util.showWarningText("数值需要设置在0~6000之间")
            return
        self.compressor_status = 85
        if speed < 1800:
            self.compressor_status = 170
        _, intbytes = util.convert_int_to_2byte_bytes(speed)
        util.getModuleWidget("RequestStatus").send_cmd(
            f"WaterControl, Send, 0, SetCompressor, {intbytes[0]}, {intbytes[1]}, {self.compressor_status}")

    def on_set_compressor_inner(self, speed=0):
        self.compressor_status = 85
        util.compressor_work = True
        if speed < 1800:
            self.compressor_status = 170
            util.compressor_work = False
        _, intbytes = util.convert_int_to_2byte_bytes(speed)
        util.getModuleWidget("RequestStatus").send_cmd(
            f"WaterControl, Send, 0, SetCompressor, {intbytes[0]}, {intbytes[1]}, {self.compressor_status}")

    def on_set_water_box_temp(self):
        txt = self.ui.lineEdit_5.text
        temp = float(txt)
        if not (0 <= temp <= 100):
            util.showWarningText("数值需要设置在0~100之间")
            return
        self.water_box_status = 85
        if 0 == temp:
            self.water_box_status = 170
        _, intbytes = util.convert_float_to_bytes(temp)
        util.getModuleWidget("RequestStatus").send_cmd(
            f"WaterControl, Send, 0, SetWaterBox, {intbytes[0]}, {intbytes[1]}, {intbytes[2]}, {intbytes[3]}, {self.water_box_status}")

    def on_set_fan_speed(self):
        txt = self.ui.l1.text
        speed = int(txt)
        if not (0 <= speed <= 100):
            util.showWarningText("数值需要设置在0~100之间")
            return
        self.fan_speed = speed
        self.fan_status = 85
        if 0 == speed:
            self.fan_status = 170
        util.getModuleWidget("RequestStatus").send_cmd(
            f"WaterControl, Send, 0, SetFan, {self.fan_speed}, {self.fan_status}")

    def on_set_cacuum_speed(self):
        txt = self.ui.lineEdit_2.text
        speed = int(txt)
        if not (0 <= speed <= 100):
            util.showWarningText("数值需要设置在0~100之间")
            return
        self.vacuum_pump_speed = speed
        self.vacuum_pump_status = 85
        if 0 == speed:
            self.vacuum_pump_status = 170
            self.vacuum_pump_speed = 1
        util.getModuleWidget("RequestStatus").send_cmd(
            f"WaterControl, Send, 0, SetVacuumPump, {self.vacuum_pump_speed}, {self.vacuum_pump_status}")

    def on_set_cacuum_speed_inner(self, speed=0):
        self.vacuum_pump_speed = speed
        self.vacuum_pump_status = 85
        util.cacuum_work = True
        if 0 == speed:
            self.vacuum_pump_status = 170
            self.vacuum_pump_speed = 1
            util.cacuum_work = False
        util.getModuleWidget("RequestStatus").send_cmd(
            f"WaterControl, Send, 0, SetVacuumPump, {self.vacuum_pump_speed}, {self.vacuum_pump_status}")

    def on_reset_mcu(self):
        util.getModuleWidget("RequestStatus").send_cmd(f"WaterControl, Send, 0, ResetMCU, 1")

    def add_pressure(self, speed=5):
        self.water_pump_direction = 0
        self.water_pump_speed = speed
        self.water_pump_status = 90
        util.getModuleWidget("RequestStatus").send_cmd(
            f"WaterControl, Send, 0, SetWaterPump, {self.water_pump_direction}, {self.water_pump_speed}, {self.water_pump_status}")

    def sub_pressure(self, direction=0, speed=5):
        self.water_pump_direction = direction
        self.water_pump_speed = speed
        self.water_pump_status = 165
        util.getModuleWidget("RequestStatus").send_cmd(
            f"WaterControl, Send, 0, SetWaterPump, {self.water_pump_direction}, {self.water_pump_speed}, {self.water_pump_status}")

    def on_fill_water(self, speed=2):
        self.water_pump_direction = 0
        self.water_pump_speed = speed
        self.water_pump_status = 85
        # print(int(self.water_pump_direction, 16), int(self.water_pump_speed, 16), int(self.water_pump_status, 16))
        util.getModuleWidget("RequestStatus").send_cmd(
            f"WaterControl, Send, 0, SetWaterPump, {self.water_pump_direction}, {self.water_pump_speed}, {self.water_pump_status}")

    def on_drain_water(self, speed=2):
        self.water_pump_direction = 17
        self.water_pump_speed = speed
        self.water_pump_status = 85
        util.getModuleWidget("RequestStatus").send_cmd(
            f"WaterControl, Send, 0, SetWaterPump, {self.water_pump_direction}, {self.water_pump_speed}, {self.water_pump_status}")

    def on_stop(self):
        self.water_pump_status = 170
        util.getModuleWidget("RequestStatus").send_cmd(
            f"WaterControl, Send, 0, SetWaterPump, {self.water_pump_direction}, {self.water_pump_speed}, {self.water_pump_status}")

    def on_set_water_pump_speed(self):
        txt = self.ui.lineEdit.text
        speed = int(txt)
        if not (0 <= speed <= 5):
            util.showWarningText("数值需要设置在0~5之间")
            return
        self.water_pump_speed = speed
        util.getModuleWidget("RequestStatus").send_cmd(
            f"WaterControl, Send, 0, SetWaterPump, {self.water_pump_direction}, {self.water_pump_speed}, {self.water_pump_status}")

    def on_set_water_direction(self):
        direction = self.ui.comboBox_4.currentText
        if direction == "AB正向":
            self.water_pump_direction = 0
        elif direction == "AB反向":
            self.water_pump_direction = 17
        elif direction == "A正B反":
            self.water_pump_direction = 1
        elif direction == "A反B正":
            self.water_pump_direction = 16
        util.getModuleWidget("RequestStatus").send_cmd(
            f"WaterControl, Send, 0, SetWaterPump, {self.water_pump_direction}, {self.water_pump_speed}, {self.water_pump_status}")

    def on_set_water_status(self):
        direction = self.ui.comboBox_5.currentText
        if direction == "AB打开":
            self.water_pump_status = 85
        elif direction == "AB关闭":
            self.water_pump_status = 170
        elif direction == "A开B关":
            self.water_pump_status = 90
        elif direction == "A关B开":
            self.water_pump_status = 165
        util.getModuleWidget("RequestStatus").send_cmd(
            f"WaterControl, Send, 0, SetWaterPump, {self.water_pump_direction}, {self.water_pump_speed}, {self.water_pump_status}")

    def on_set_reference_temp(self):
        txt = self.ui.lineEdit_6.text
        temp = float(txt)
        if not (0 <= temp <= 100):
            util.showWarningText("数值需要设置在0~100之间")
            return
        _, intbytes = util.convert_float_to_bytes(temp)
        util.getModuleWidget("RequestStatus").send_cmd(
            f"WaterControl, Send, 0, SetReferenceTemp, {intbytes[3]}, {intbytes[2]}, {intbytes[1]}, {intbytes[0]}, 85")

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

    def analyse_heart_beat(self, stringlist):
        chararray = stringlist.split(" ")
        # print("water control heart:", chararray)
        if len(chararray) != 65:
            return
        # print(chararray)

        # str1 = ""
        # for i in range(65):
        #   str1 = str1 + i.__str__()+":"+chararray[i]
        #   str1 = str1 + "   "
        # print(str1)
        # 帧头
        head = chararray[0]
        # 包类型
        packet_type = chararray[1]
        # 操作类型
        operator_type = chararray[2]
        # 数据包编号
        packet_number = chararray[3:5]
        # 帧尾
        tail = chararray[63]
        # 软件状态
        software_status = chararray[5]
        # 水囊温度
        water_bladder_str = "".join(chararray[6:10]).replace("0x", "")
        water_bladder_temp = util.convert_hex_to_float(water_bladder_str)
        self.ui.label_9.setText(f"{water_bladder_temp:.2f}")
        util.parameter_config['water_bladder_temp'] = water_bladder_temp

        # 水箱温度
        water_box_str = "".join(chararray[10:14]).replace("0x", "")
        water_box_temp = util.convert_hex_to_float(water_box_str)
        self.ui.label_14.setText(f"{water_box_temp:.2f}")
        util.parameter_config['water_box_temp'] = water_box_temp

        # 氧浓度
        oxygen_concentration_str = "".join(chararray[14:18]).replace("0x", "")
        oxygen_concentration = util.convert_hex_to_float(oxygen_concentration_str)
        self.ui.label_17.setText(f"{oxygen_concentration:.2f}")
        util.parameter_config['oxygen_concentration'] = oxygen_concentration

        # 风扇速度
        fan_speed_str = "".join(chararray[18:22]).replace("0x", "")
        fan_speed = util.convert_hex_to_float(fan_speed_str) * 60
        self.ui.label_2.setText(f"{fan_speed:.2f}")

        # 制冷风扇速度
        make_cold_fan_speed_str = "".join(chararray[22:26]).replace("0x", "")
        make_cold_fan_speed = util.convert_hex_to_float(make_cold_fan_speed_str) * 60
        self.ui.label_2.setText(f"{make_cold_fan_speed:.2f}")
        if make_cold_fan_speed < 2000 and util.compressor_work:
            self.counts['make_cold_fan_speed'] += 1
            if self.counts['make_cold_fan_speed'] == 3:
                self.counts['make_cold_fan_speed'] = 0
                print(f'make_cold_fan_speed is {make_cold_fan_speed}')
                util.getModuleWidget("JMessageBox").show_one_popup('压缩机故障，制冷风扇转速小于2000')

        # 真空泵速度
        cacuum_pump_str = "".join(chararray[26:30]).replace("0x", "")
        cacuum_pump = util.convert_hex_to_float(cacuum_pump_str) * 60
        self.ui.label_5.setText(f"{cacuum_pump:.2f}")
        if cacuum_pump < 400 and util.cacuum_work:
            self.counts['cacuum_pump'] += 1
            if self.counts['cacuum_pump'] == 3:
                self.counts['cacuum_pump'] = 0
                print(f'cacuum_pump is {cacuum_pump}')
                util.getModuleWidget("JMessageBox").show_one_popup('压缩机故障，真空泵转速小于400')

        # 电机当前位置
        electrical_machinery_str = "".join(chararray[30:34]).replace("0x", "")
        electrical_machinery = util.convert_hex_to_float(electrical_machinery_str)
        self.ui.label_25.setText(f"{electrical_machinery:.2f}")

        # 压力值
        press_value_str = "".join(chararray[34:38]).replace("0x", "")
        press_value = (util.convert_hex_to_float(press_value_str) * 3300 / 10 - 0.5) / 0.0225
        self.ui.label_37.setText(f"{press_value:.2f}kpa")
        util.parameter_config['press_value'] = press_value

        # 主板电源状态1、电机Home状态2、水位位置传感器3、阀状态4
        board_power_status, electrical_machinery_status, water_pos, valve_status, *_ = util.extract_states_from_hex_string(
            chararray[38])
        self.ui.label_33.setText(board_power_status)
        self.ui.label_27.setText(electrical_machinery_status)
        self.ui.label_48.setText(water_pos)
        util.parameter_config['water_pos'] = water_pos
        print(f'water_pos is {water_pos}')
        self.ui.label_22.setText(valve_status)

        # 风扇状态1，真空泵状态2，制热状态3，制冷状态4
        fan_status, cacuum_pump_status, make_hot_status, make_cold_status, *_ = util.extract_states_from_hex_string(
            chararray[39])
        self.ui.label_40.setText(fan_status)
        self.ui.label_42.setText(cacuum_pump_status)
        self.ui.label_67.setText(make_hot_status)
        self.ui.label_63.setText(make_cold_status)

        # 制冷风扇状态1,24v状态2，水囊手动制冷状态3，水箱手动制热状态4
        cold_fan_status, v24status, water_bladder_manual_cold_status, water_box_manual_cold_status, *_ = util.extract_states_from_hex_string(
            chararray[40])
        self.ui.label_15.setText(cold_fan_status)
        self.ui.label_19.setText(v24status)
        self.ui.label_66.setText(water_bladder_manual_cold_status)
        self.ui.label_23.setText(water_box_manual_cold_status)

        if v24status == 1:
            if fan_speed < 400:
                self.counts['fan_speed'] += 1
                if self.counts['fan_speed'] == 3:
                    self.counts['fan_speed'] = 0
                    print(f'fan_speed is {fan_speed}')
                    util.getModuleWidget("JMessageBox").show_one_popup('水箱风扇故障')

            if water_bladder_temp > 500:
                self.counts['water_bladder_temp'] += 1
                if self.counts['water_bladder_temp'] == 3:
                    self.counts['water_bladder_temp'] = 0
                    print(f'water_bladder_temp is {water_bladder_temp}')
                    util.getModuleWidget("JMessageBox").show_one_popup('水囊装置异常，导致水囊温度异常')

            if not (-20 < press_value < 100):
                self.counts['press_value'] += 1
                if self.counts['press_value'] == 3:
                    self.counts['press_value'] = 0
                    print(f'press_value is {press_value}')
                    util.getModuleWidget("JMessageBox").show_one_popup('水囊装置异常，导致压力值异常')

        # 电机原点动作状态 0上电默认 1开始寻找原点 2寻找动作中 3寻找结束 动作结束（3）后才能下发新的电机动作（8位数）
        machine_origin_action_status = int(chararray[41], 16)
        self.ui.label_35.setText(machine_origin_action_status)
        # 电机动作状态 0上电默认 1开始动作 2动作中 3动作结束 动作结束（3）后才能下发新的电机动作（8位数）
        machine_action_status = int(chararray[42], 16)
        self.ui.label_38.setText(machine_action_status)
        # 水泵A状态 0待机 1 动作,水泵A方向 0正向 1反向, 水泵B状态 0待机 1 动作, 水泵B方向 0正向 1反向
        A_water_pump_status, A_water_pump_direction, B_water_pump_status, B_water_pump_direction, *_ = util.extract_states_from_hex_string(
            chararray[43])
        self.ui.label_49.setText(f"{A_water_pump_direction}_{B_water_pump_direction}")
        self.ui.label_50.setText(f"{A_water_pump_status}_{B_water_pump_status}")
        # 水泵速度 （0（2.5圈/s），1（1.5625圈/s），2(1.25圈/s)，3(0.625)，4(0.3125圈/s)，5(0.15625圈/s) ）
        water_pump_speed = int(chararray[44], 16)
        self.ui.label_3.setText(f"{water_pump_speed}")
        # 压缩机状态
        compressor_status = int(chararray[45], 16)
        self.ui.label_56.setText(f"{compressor_status}")
        # 压缩机速度
        compressor_speed_str = "".join(chararray[46:48]).replace("0x", "")
        compressor_speed = util.convert_hex_to_half_int(compressor_speed_str)
        self.ui.label_54.setText(f"{compressor_speed}")
        # 压缩机电压
        compressor_voltage_str = "".join(chararray[48:50]).replace("0x", "")
        compressor_voltage = util.convert_hex_to_half_int(compressor_voltage_str) / 100
        self.ui.label_52.setText(f"{compressor_voltage}")
        # 压缩机电流
        compressor_current_str = "".join(chararray[50:52]).replace("0x", "")
        compressor_current = util.convert_hex_to_half_int(compressor_current_str)
        self.ui.label_60.setText(f"{compressor_current}")
        # 压缩机故障码
        compressor_fault_code = int(chararray[52], 16)
        self.ui.label_61.setText(f"{compressor_fault_code}")
        if util.compressor_work and compressor_fault_code > 0:
            print(f'compressor_fault_code is {compressor_fault_code}')
            util.getModuleWidget("JMessageBox").show_one_popup(self.compressor_fault_codes[compressor_fault_code])

        # 压缩机温度
        compressor_temp_str = "".join(chararray[53:55]).replace("0x", "")
        compressor_temp = util.convert_hex_to_half_int(compressor_temp_str)
        self.ui.label_62.setText(f"{compressor_temp}")
