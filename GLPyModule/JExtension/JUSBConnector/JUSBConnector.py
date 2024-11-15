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
# JUSBConnector
#

class JUSBConnector(ScriptedLoadableModule):

    def __init__(self, parent):
        ScriptedLoadableModule.__init__(self, parent)
        self.parent.title = "JUSBConnector"  # TODO: make this more human readable by adding spaces
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


class PurayHidUnit:
    def __init__(self, uiwidget, ui, vid, pid, key) -> None:
        self.uiwidget = uiwidget
        self.ui = ui
        self.vid = vid
        self.pid = pid
        self.key = key

        self.ui.btn_connect.setEnabled(False)
        self.ui.operator_panel.setEnabled(False)
        self.ui.btn_close_software.setEnabled(False)
        self.ui.btn_write_switch.setEnabled(False)
        self.ui.btn_software_status.setEnabled(False)

        self.ui.btn_connect.connect('clicked()', self.on_connect)
        self.ui.btn_read.connect('clicked()', self.on_read_info)
        self.ui.btn_write.connect('clicked()', self.on_write_info)
        self.ui.btn_software_status.connect('clicked()', self.change_software_status)
        self.ui.btn_close_software.connect('clicked()', self.close_software_status)
        self.ui.btn_write_switch.connect('clicked()', self.switch_software_status)

    def close_software_status(self):
        util.getModuleWidget("RequestStatus").send_cmd(f"{self.key}, Send, 0, ChangeSoftwareStatus, 0")

    def switch_software_status(self):
        util.getModuleWidget("RequestStatus").send_cmd(f"{self.key}, Send, 0, SwitchSoftwareStatus, 0")
        util.singleShot(1100, self._switch_software_status)

    def _switch_software_status(self):
        self.ui.btn_close_software.setEnabled(True)
        self.ui.btn_write_switch.setEnabled(False)
        self.ui.btn_software_status.setEnabled(True)
        self.ui.operator_panel.setEnabled(False)
        self.ui.widget_6.setEnabled(True)
        self.ui.label_3.setText("写入状态")

    def change_software_status(self):
        util.getModuleWidget("RequestStatus").send_cmd(f"{self.key}, Send, 0, ChangeSoftwareStatus, 1")

    def on_write_info(self):
        gap = 3000
        self.ui.btn_write.setEnabled(False)
        util.processEvents()
        index = self.ui.comboBox.currentIndex
        text1 = self.ui.le_software_info.text
        ascii_codes = [ord(char).__str__() for char in text1]
        str1 = "#".join(ascii_codes)
        util.getModuleWidget("RequestStatus").send_cmd(
            f"{self.key}, Send, {gap}, WriteSoftwareInfo, {index + 3}, {str1}")
        util.singleShot(gap, lambda: self.ui.btn_write.setEnabled(True))

    def on_read_info(self):
        gap = 1000
        self.ui.btn_read.setEnabled(False)
        index = self.ui.comboBox.currentIndex
        util.getModuleWidget("RequestStatus").send_cmd(f"{self.key}, Send, {gap}, ReadSoftwareInfo, {index + 3}")
        util.singleShot(gap, lambda: self.ui.btn_read.setEnabled(True))

    def on_connect(self):
        print("send cmd ",f"{self.key}, Init, {self.vid}, {self.pid}")
        util.getModuleWidget("RequestStatus").send_cmd(f"{self.key}, Init, {self.vid}, {self.pid}")

    def set_ui_status(self, status):
        if status == "-1":
            self.ui.btn_connect.setText("连接")
            self.ui.btn_connect.setStyleSheet("color: white;")
            self.ui.btn_connect.setEnabled(True)
            self.ui.operator_panel.setEnabled(False)
            self.ui.btn_close_software.setEnabled(False)
            self.ui.btn_write_switch.setEnabled(False)
            self.ui.btn_software_status.setEnabled(False)
        elif status == "-2":
            self.ui.btn_connect.setText("连接(请检查USB设备)")
            self.ui.btn_connect.setStyleSheet("color: red;")
            self.ui.btn_connect.setEnabled(True)
            self.ui.operator_panel.setEnabled(False)
        else:
            self.ui.btn_connect.setText("已连接")
            self.ui.btn_connect.setStyleSheet("color: green;")
            self.ui.btn_connect.setEnabled(False)
            self.ui.operator_panel.setEnabled(True)

    def set_software_status(self, value):
        if value == "-1":
            self._switch_software_status()
        elif value == "-2":
            return
        else:
            infolist = value.split(" ")
            if int(infolist[5], 16) == 0:
                self.ui.operator_panel.setEnabled(False)
                self.ui.btn_connect.setEnabled(False)
                self.ui.btn_close_software.setEnabled(False)
                self.ui.btn_software_status.setEnabled(True)
                self.ui.btn_write_switch.setEnabled(True)
                self.ui.label_3.setText("待机状态")
                self.ui.widget_10.setEnabled(False)
            elif int(infolist[5], 16) == 1:
                self.ui.operator_panel.setEnabled(True)
                self.ui.btn_connect.setEnabled(False)
                self.ui.btn_close_software.setEnabled(True)
                self.ui.btn_write_switch.setEnabled(False)
                self.ui.btn_software_status.setEnabled(False)
                self.ui.label_3.setText("工作状态")
                self.ui.widget_10.setEnabled(False)

    def tickEvent(self, value):
        map_info = {}
        info_list_str = value.split("*V* ")
        for row in info_list_str:
            if row == "":
                continue
            key_value_pair_list = row.split("*U* ")
            if (len(key_value_pair_list) != 2):
                print("ASLK:", len(key_value_pair_list))
                print("Error Data Format:", value)
                assert (True == False)
            key = key_value_pair_list[0]
            value = key_value_pair_list[1]
            map_info[key] = value

        self.ui.textEdit.setText("心跳：")
        if "connect_status" in map_info and map_info["connect_status"] != "nan":
            self.set_ui_status(map_info["connect_status"])
        if "heart_beat" in map_info and map_info["heart_beat"] != "nan":
            self.ui.textEdit.setText("心跳：" + map_info["heart_beat"])
        if "software_status" in map_info and map_info["software_status"] != "nan":
            self.set_software_status(map_info["software_status"])
        if "ReadSoftwareInfo" in map_info and map_info["ReadSoftwareInfo"] != "nan":
            infolist = map_info["ReadSoftwareInfo"].split(" ")
            self.ui.comboBox.setCurrentIndex(int(infolist[2], 16) - 3)
            str_result = ""
            for i in range(5, 64):
                # 十六进制字符串
                hex_str = infolist[i]
                # 将十六进制字符串转换为整数
                num = int(hex_str, 16)
                if num == 0:
                    break
                # 将整数转换为ASCII字符
                ascii_char = chr(num)
                str_result += ascii_char
            self.ui.le_software_info.setText(str_result)
            util.getModuleWidget("RequestStatus").send_cmd(f"{self.key}, EraseKey, ReadSoftwareInfo")


#
# JSystemInfoWidget
#

class JUSBConnectorWidget(JBaseExtensionWidget):
    vid = 0
    pid = 0

    def setup(self):
        super().setup()

    def create_widget(self, vid, pid, key):
        uiwidget = slicer.util.loadUI(self.resourcePath('UI/USBHidPuray.ui'))
        ui = slicer.util.childWidgetVariables(uiwidget)
        unit = PurayHidUnit(uiwidget, ui, vid, pid, key)
        return unit
