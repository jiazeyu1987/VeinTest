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

from TreatTools.ProgressButton import ProgressButton
#
# JUltrasoundGenerator
#

class JUltrasoundGenerator(ScriptedLoadableModule):

    def __init__(self, parent):
        ScriptedLoadableModule.__init__(self, parent)
        self.parent.title = "JUltrasoundGenerator"  # TODO: make this more human readable by adding spaces
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
class ParamConfig:
    def __init__(self, params):
        self.module_path = os.path.dirname(slicer.util.modulePath("VeinTreat"))
        self.uiWidget = slicer.util.loadUI(self.module_path + '/Resources/UI/ParamConfig.ui')
        self.uiWidget.setWindowFlag(qt.Qt.FramelessWindowHint)

        self.ui = slicer.util.childWidgetVariables(self.uiWidget)

        self.params = params

        self._init_ui()

    def _init_ui(self):
        label_style = '''
            font-size: 22px;
            color: rgba(255,255,255,217);
            text-align: right;
        '''
        self.ui.label.setStyleSheet(label_style)
        self.ui.label_2.setStyleSheet(label_style)
        self.ui.label_3.setStyleSheet(label_style)
        self.ui.label_4.setStyleSheet(label_style)
        self.ui.label_7.setStyleSheet(label_style)

        edit_style = '''
            background: #232428;
            border-radius: 4px 4px 4px 4px;
            border: 1px solid #699FC3;
        '''
        self.ui.power.setStyleSheet(edit_style)
        self.ui.width.setStyleSheet(edit_style)
        self.ui.circle.setStyleSheet(edit_style)
        self.ui.treat_time.setStyleSheet(edit_style)
        self.ui.cool_time.setStyleSheet(edit_style)

        self.ui.power.setText(self.params[0])
        self.ui.width.setText(self.params[1])
        self.ui.circle.setText(self.params[2])
        self.ui.treat_time.setText(self.params[3])
        self.ui.cool_time.setText(self.params[4])

        self.ui.btn1.clicked.connect(self._on_reject)
        self.ui.btn1.setStyleSheet(util.button2_style.format("20"))
        self.ui.btn2.clicked.connect(self._on_modify)
        self.ui.btn2.setStyleSheet(util.button2_style.format("20"))

    def _on_modify(self):
        self.params[0] = self.ui.power.text
        self.params[1] = self.ui.width.text
        self.params[2] = self.ui.circle.text
        self.params[3] = self.ui.treat_time.text
        self.params[4] = self.ui.cool_time.text
        util.getModuleWidget("JUltrasoundGenerator").on_set_power_treat(self.params)
        self._on_accept()

    def on_get_value(self):
        return self.params

    def exec_(self):
        return self.uiWidget.exec_()

    def _on_reject(self):
        self.uiWidget.reject()

    def _on_accept(self):
        self.uiWidget.accept()



class JUltrasoundGeneratorWidget(JBaseExtensionWidget):
    unit = None

    def setup(self):
        super().setup()
        self.ui.tabWidget.tabBar().hide()
        self.unit = util.getModuleWidget("JUSBConnector").create_widget(1155, 22352, "UltrasoundGenerator")
        util.addWidget2(self.ui.unit_container, self.unit.uiwidget)
        # logpath = self.resourcePath('log/communicate.log').replace("\\","/")
        # util.singleShot(100,lambda:util.getModuleWidget("RequestStatus").send_cmd(f"UltrasoundGenerator, OpenAndShowLog, {logpath}"))
        self.feedback_columns = [('电压', 'V'), ('电流', 'A'), ('功率', 'W')]
        self.params = [0, 0, 0, 0, 0]
        self.treat_power = 0
        self.width = 0
        self.circle = 0
        self.cool_time = 0
        self.total_time = 0
        self.settings_columns = ['功率', '突发宽度', '突发周期', '治疗时间', '冷却时间']
        self.btn_treat = ProgressButton()
        util.addWidget2(self.ui.widget_treatment, self.btn_treat)
        self.btn_treat.setEnabled(True)

    def init_ui(self):
        self.ui.btn_setting_power.connect('clicked()', self.on_setting_power)
        self.ui.btn_start.connect('clicked()', self.on_start)
        self.ui.btn_mcu.connect('clicked()', self.on_reset_mcu)
        self.ui.pushButton.connect('clicked()', self.on_set_work)
        self.ui.pushButton_2.connect('clicked()',self.on_set_paras)
        self.ui.pushButton_3.connect('clicked()',self.on_stop)
        slicer.mrmlScene.AddObserver(util.ReconnectEvent, self.OnReconnectEvent)

        validator = qt.QIntValidator(self.ui.lineEdit)
        self.ui.lineEdit.setValidator(validator)
        validator = qt.QIntValidator(self.ui.lineEdit_2)
        self.ui.lineEdit_2.setValidator(validator)
        validator = qt.QIntValidator(self.ui.lineEdit_4)
        self.ui.lineEdit_4.setValidator(validator)
        validator = qt.QIntValidator(self.ui.lineEdit_5)
        self.ui.lineEdit_5.setValidator(validator)
        validator = qt.QIntValidator(self.ui.lineEdit_12)
        self.ui.lineEdit_12.setValidator(validator)
        self.timer_start = qt.QTimer()
        self.timer_start.timeout.connect(self.start_completed)

    def on_settings(self):
        detail_info = f'''
                    <span style="font-size: 28px;">设置</span>
                '''
        for (key, value) in zip(self.settings_columns, self.params):
            detail_info += f'''<p>{key}：{value}</p>'''
        #print("OOOOOAAAAAAAAA:",detail_info)
        self.ui.label.setText(detail_info)


    def on_set_paras(self):
        dialog = ParamConfig(self.params)
        result = dialog.exec_()
        if result == qt.QDialog.Rejected:
            return
        self.params = dialog.on_get_value()
        self.on_settings()
        self.btn_treat.set_duration(self.params[4], self.params[3])
        self.treat_power = float(self.params[0])
        self.width = float(self.params[1])
        self.circle = float(self.params[2])
        self.total_time = float(self.params[3])
        self.cool_time = float(self.params[4])

    @vtk.calldata_type(vtk.VTK_OBJECT)
    def OnReconnectEvent(self, caller, str_event, calldata):
        val = calldata.GetAttribute("value")
        if val == "UltrasoundGenerator":
            #print("on reconnect with ultrasound generator")
            self.unit.on_connect()
            self.unit.change_software_status()

    def on_set_power_treat(self, params):
        power = int(float(params[0]) * 100)
        # vol = int(math.sqrt(power * util.WaterBladderConfig["power_factor"] * 100) * 10)
        width = int(float(params[1]) * 1000)
        circle = int(float(params[2]) * 1000)
        total = int(float(params[3]) * 1000)
        #print(f"ultrasound generation is {power, width, circle, total}")

        util.getModuleWidget("RequestStatus").send_cmd(
            f"UltrasoundGenerator, Send, 0, SetPower, 3000, {power}, {width}, {circle}, {total}")

    def on_setting_power(self):
        fre = int(self.ui.lineEdit.text)
        vol = int(self.ui.lineEdit_2.text)
        width = int(self.ui.lineEdit_4.text)
        circle = int(self.ui.lineEdit_5.text)
        total = int(self.ui.lineEdit_12.text)
        if fre < 500 or fre > 5000:
            util.showWarningText("【工作频率】数值需要设置在规定数值之间")
        if vol < 1 or vol > 30000:
            util.showWarningText("【直流电压】数值需要设置在规定数值之间")
        if width < 1 or width > 2000:
            util.showWarningText("【突发宽度】数值需要设置在规定数值之间")
        if circle < 1 or circle > 2000:
            util.showWarningText("【突发周期】数值需要设置在规定数值之间")
        if total < 1 or total > 65000:
            util.showWarningText("【输出总时间】数值需要设置在规定数值之间")
        # power = int(txt)
        # if power < 0 or power > 500:
        #   util.showWarningText("数值需要设置在0~500之间")
        util.getModuleWidget("RequestStatus").send_cmd(
            f"UltrasoundGenerator, Send, 0, SetPower, {fre}, {vol}, {width}, {circle}, {total}")

    def on_start(self):
        util.getModuleWidget("RequestStatus").send_cmd(f"UltrasoundGenerator, Send, 0, StartGenerator, 85")
        self.timer_start.start(int(self.ui.lineEdit_12.text) + 100)
        self.ui.btn_start.setEnabled(False)
        self.ui.lb_start.setText("功率正在发射中：")
        self.ui.btn_start.setText("发射中")
        self.ui.btn_start.setStyleSheet("color: red;")

    def on_stop(self):
        util.getModuleWidget("RequestStatus").send_cmd(f"UltrasoundGenerator, Send, 0, StartGenerator, 170")
        self.ui.btn_start.setEnabled(True)
        self.ui.lb_start.setText("功率已发射完成：")
        self.ui.btn_start.setText("发射")
        self.ui.btn_start.setStyleSheet("")

    def start_completed(self):
        util.getModuleWidget("RequestStatus").send_cmd(f"UltrasoundGenerator, Send, 0, StartGenerator, 170")
        self.ui.btn_start.setEnabled(True)
        self.ui.lb_start.setText("功率已发射完成：")
        self.ui.btn_start.setText("发射")
        self.ui.btn_start.setStyleSheet("")

    def on_set_work(self):
        util.getModuleWidget("RequestStatus").send_cmd(
            f"UltrasoundGenerator, Send, 0, SetWorkStatus, 1")

    def on_reset_mcu(self):
        util.getModuleWidget("RequestStatus").send_cmd(f"UltrasoundGenerator, Send, 0, ResetMCU, 1")

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

    def analyse_heart_beat(self, stringlist):
        chararray = stringlist.split(" ")
        if len(chararray) != 65:
            return
        # #print(chararray)
        # 0xAA
        head = chararray[0]
        # 0x02
        packet_type = chararray[1]
        # 0x01
        operator_type = chararray[2]
        # 0x00
        packet_number = chararray[3:5]

        # 待机状态
        software_status = chararray[5]
        util.parameter_config['UG_software_status'] = int(software_status, 16)
        # PA软件版本低/高
        PA_version = chararray[6:8]
        util.parameter_config['PA_version'] = util.convert_2byte_to_int(PA_version)
        # 功放ID号低/高
        PA_ID = chararray[8:10]
        util.parameter_config['PA_ID'] = util.convert_2byte_to_int(PA_ID)
        # PA设定工作频率低/高
        PA_Frequency = chararray[10:12]
        # 工作频率更新状态（0未成功下发，1成功设置）
        PA_Frequency_Status = chararray[12]
        #print('AC_voltage0')
        # 直流电压设定低/高
        volyage = chararray[13:15]
        # 直流电压更新状态（0未成功下发，1成功设置）
        volyage_status = chararray[15]
        # 突发宽度低/高
        width = chararray[16:18]
        # 突发周期低/高
        circle = chararray[18:20]
        # 总时间低/高
        total = chararray[20:22]
        # 突发时间更新状态（0未成功下发，1成功设置）
        sudden_status = chararray[22]
        # 输出交流电压有效值低/高
        AC_voltage = chararray[23:25]
        util.parameter_config['AC_voltage'] = util.convert_2byte_to_int(AC_voltage) / 100
        # 输出交流电流有效值低/高
        AC_current = chararray[25:27]
        util.parameter_config['AC_current'] = util.convert_2byte_to_int(AC_current) / 100
        # 功放工作状态字节
        amplifier_working_status = chararray[27]
        # 功放错误信息字节
        amplifier_error_status = chararray[28]
        # PA在线状态 00离线  01在线
        Working_status = int(chararray[29], 16)
        #print('AC_voltage')
        self.ui.lineEdit_6.setText(f"功放ID号:{util.convert_2byte_to_int(PA_ID)}")
        self.ui.lineEdit_7.setText(f"待机状态:{int(software_status, 16)}")
        self.ui.lineEdit_8.setText(f"PA设定功率:{util.convert_2byte_to_int(PA_Frequency)}")
        self.ui.lineEdit_9.setText(f"直流电压:{util.convert_2byte_to_int(volyage)}")
        self.ui.lineEdit_11.setText(f"突发宽度:{util.convert_2byte_to_int(width)}")
        self.ui.lineEdit_10.setText(f"突发周期:{util.convert_2byte_to_int(circle)}")
        self.ui.lineEdit_3.setText(f"总时间:{util.convert_2byte_to_int(total)}")
        #print('AC_voltage2')
        amplifier_output_status, DC_power_status, *_ = util.extract_states_from_hex_string(chararray[27])

        over_temp, output_current, DC_power_connect, *_ = util.extract_states_from_hex_string(chararray[28])
        #print('AC_voltage3')

        AC_voltage = util.parameter_config['AC_voltage']
        #print('AC_voltage31')
        AC_current = util.parameter_config['AC_current']
        #print('AC_voltage32')
        AC_power = round(AC_voltage * AC_current, 2)
        #print('AC_voltage33')
        self.UG_params = [AC_voltage, AC_current, AC_power]
        #print('AC_voltage34')
        detail_info = f'''
                    <span style="font-size: 28px;">反馈</span>
                '''
        for (key, value) in zip(self.feedback_columns, self.UG_params):
            detail_info += f'''<p>{key[0]}：{value}{key[1]}</p>'''
            #print('AC_voltage345')
        #print('AC_voltage4',detail_info)
        self.ui.label_4.setText(detail_info)