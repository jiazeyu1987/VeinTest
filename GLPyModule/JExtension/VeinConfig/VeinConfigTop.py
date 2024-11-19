import math
import win32process
import win32gui

import qt, slicer
from slicer.ScriptedLoadableModule import *
from slicer.util import VTKObservationMixin
import slicer.util as util
import os
import sqlite3
from datetime import datetime
import time
from ConfigTools.WaterBladder import WaterBladder
import numpy as np


class VeinConfigTop(ScriptedLoadableModule):

    def __init__(self, parent):
        ScriptedLoadableModule.__init__(self, parent)
        self.parent.title = "VeinConfigTop"  # TODO: make this more human readable by adding spaces
        self.parent.categories = [
            "Examples"]  # TODO: set categories (folders where the module shows up in the module selector)
        self.parent.dependencies = []  # TODO: add here list of module names that this module requires
        self.parent.contributors = ["sun qing wen"]  # TODO: replace with "Firstname Lastname (Organization)"
        # TODO: update with short description of the module and a link to online module documentation
        self.parent.helpText = """
    
    """
        # TODO: replace with organization, grant and thanks
        self.parent.acknowledgementText = """

"""


class VeinConfigTopWidget(ScriptedLoadableModuleWidget, VTKObservationMixin):

    def __init__(self, parent=None) -> None:
        """Called when the user opens the module the first time and the widget is initialized."""
        ScriptedLoadableModuleWidget.__init__(self, parent)
        VTKObservationMixin.__init__(self)  # needed for parameter node observation
        self.logic = None
        self._parameterNode = None
        self._parameterNodeGuiTag = None

    def setup(self) -> None:
        """Called when the user opens the module the first time and the widget is initialized."""
        ScriptedLoadableModuleWidget.setup(self)

        # Load widget from .ui file (created by Qt Designer).
        # Additional widgets can be instantiated manually and added to self.layout.
        self.uiWidget = slicer.util.loadUI(self.resourcePath("UI/VeinConfigTop.ui"))
        self.layout.addWidget(self.uiWidget)
        self.ui = slicer.util.childWidgetVariables(self.uiWidget)

        # Set scene in MRML widgets. Make sure that in Qt designer the top-level qMRMLWidget's
        # "mrmlSceneChanged(vtkMRMLScene*)" signal in is connected to each MRML widget's.
        # "setMRMLScene(vtkMRMLScene*)" slot.
        self.uiWidget.setMRMLScene(slicer.mrmlScene)

        #self.cursor = util.db_conn.cursor()
        self._init_ui()

    def _init_ui(self):
        self.TARGET_JOINT_POS = [43.87, -143.93, 123.31, -136.06, -90.51, -85.47]

        self.ui.btn_water_bladder.setStyleSheet('''
            font: 22px;
            color: rgba(255,255,255,217);
            text-align: center;
            background: #2075F5; 
            border-radius: 20px;
            padding-left: 24px;
        ''')
        self.ui.btn_water_bladder.clicked.connect(self.show_water_bladder)
        self.water_bladder = util.global_data_map['WaterBladder']

        self.ui.label_info.setAlignment(qt.Qt.AlignCenter)

        self.ui.btn_complete_treat.setIcon(qt.QIcon(self.resourcePath('Icons/back.png')))
        self.ui.btn_complete_treat.setIconSize(qt.QSize(42, 42))
        self.ui.btn_complete_treat.setStyleSheet('''
            border: none;
            background: transparent;
        ''')
        self.ui.btn_complete_treat.clicked.connect(self.complete_treat)

        self.ui.label_datetime.setStyleSheet("font-size: 28px;")
        self.is_24_hour_format = True
        self.time_timer = qt.QTimer()
        self.time_timer.timeout.connect(self.show_time)
        self.time_timer.start(1000)
        self.show_time()

        self.toggle_timer = qt.QTimer()
        self.toggle_timer.timeout.connect(self.toggle_color)
        self.blinking = False

        self.scrcpy_timer = qt.QTimer()
        self.scrcpy_timer.timeout.connect(self.startUltrasound)

        self.check_timer = qt.QTimer()
        self.check_timer.timeout.connect(self.findUltrasound)
        # self.scrcpy_timer.start(300)
        self.taskID = None
        self.handle = None
        self.ultra_process = None

    def enter(self):
        self.set_water_bladder_status(3)
        self.clear_status_info()

    def exit(self):
        pass

    def start_check_scrcpy(self):
        self.scrcpy_timer.start(1000)

    def stop_check_scrcpy(self):
        self.scrcpy_timer.stop()
        process = qt.QProcess()
        process.start("taskkill.exe", ["scrcpy.exe"])
        process.waitForFinished()

    def startUltrasound(self):
        if self.ultra_process is None or self.ultra_process.state() == qt.QProcess.NotRunning:
            # print("start ultrasound")
            util.removeFromParent2(util.ultra_container)
            util.ultra_container = None
            util.getModuleWidget('VeinConfig').show_ultra_info()
            util.getModuleWidget('VeinTreat').show_ultra_info()
            self.handle = None
            self.ultra_process = qt.QProcess()
            self.ultra_process.start('scrcpy.exe', util.scrcpy_command)
            self.taskID = self.ultra_process.processId()
            # print(f"taskID is {self.taskID}")
            self.check_timer.start(300)

    def findUltrasound(self):
        if not self.taskID:
            print("error---")
            return

        def get_all_hwnd(hwnd, mouse):
            if win32gui.IsWindow(hwnd) and win32gui.IsWindowEnabled(hwnd) and win32gui.IsWindowVisible(hwnd):
                _, window_pid = win32process.GetWindowThreadProcessId(hwnd)
                # print(window_pid, self.taskID)
                if window_pid == self.taskID:
                    self.handle = hwnd
                    window = qt.QWindow.fromWinId(self.handle)
                    util.ultra_container = qt.QWidget.createWindowContainer(window)
                    # print(f"Found window handle: {self.handle}")
                    # print(f"Window title: {win32gui.GetWindowText(hwnd)}")
                    self.check_timer.stop()
                    return False
            return True

        win32gui.EnumWindows(get_all_hwnd, 0)

    def calculateJointPosError(self):
        joint_pos_str = util.global_data_map["joint_positions"]
        joint_pos_rad = joint_pos_str.split(",")
        joint_pos_deg = [round(math.degrees(float(radian)), 2) for radian in joint_pos_rad]

        assert len(joint_pos_deg) == len(self.TARGET_JOINT_POS), "Target and current joints do not have the same size"

        errors = [target - current for target, current in zip(self.TARGET_JOINT_POS, joint_pos_deg)]
        err = np.linalg.norm(errors)
        return err

    def moveToTarget(self):
        joint_pos_rad = [math.radians(x) for x in self.TARGET_JOINT_POS]
        joint_pos_str = ', '.join(str(x) for x in joint_pos_rad)
        util.getModuleWidget("RequestStatus").send_cmd(f"UR, MoveByJoint, {joint_pos_str}, True")

    def calculateJointPosError(self):
        joint_pos_str = util.global_data_map["joint_positions"]
        joint_pos_rad = joint_pos_str.split(",")
        joint_pos_deg = [round(math.degrees(float(radian)), 2) for radian in joint_pos_rad]

        assert len(joint_pos_deg) == len(self.TARGET_JOINT_POS), "Target and current joints do not have the same size"

        errors = [target - current for target, current in zip(self.TARGET_JOINT_POS, joint_pos_deg)]
        err = np.linalg.norm(errors)
        return err

    def show_water_bladder(self) -> None:
        self.water_bladder.exec_()

    def complete_treat(self) -> None:
        # print("complete treatment")
        # print(util.global_data_map['is_closed_water'])
        curr_page = util.global_data_map['page']
        if curr_page == 4 and not util.global_data_map['has_treat']:
            util.send_event_str(util.SetPage, 3)
            return
        self.ui.btn_complete_treat.setChecked(True)
        if curr_page == 3:
            result = util.getModuleWidget("JMessageBox").show_four_popup(
                '确认水囊已经下水处理？\n（若未完成，请点击左上角“水处理”按钮，进行处理）')
            if result == qt.QDialog.Rejected:
                return
            result = util.getModuleWidget("JMessageBox").show_four_popup('确认当前患者已治疗完所有静脉？')
            if result == qt.QDialog.Rejected:
                return
            self.ui.btn_complete_treat.setChecked(False)

            patient_id = util.global_data_map["patientID"]
            treatment_instruction = util.getModuleWidget("VeinConfig").get_treatment_instruction()
            treat_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            self.cursor.execute(
                f'UPDATE PatientInfo SET treatment_instruction = ?,IsTreated = ?,ModifyTime= ? WHERE ID = ?',
                (treatment_instruction, 1, treat_time, patient_id))
            util.db_conn.commit()
            with util.backup_db_conn:
                util.db_conn.backup(util.backup_db_conn)
            util.send_event_str(util.SetPage, 2)
            self.stop_check_scrcpy()
            util.vein_count = 0
            util.segment_count.clear()
        elif curr_page == 4:
            result = util.getModuleWidget("JMessageBox").show_two_popup('确认当前段落治疗完成？')
            if result == qt.QDialog.Rejected:
                return
            self.ui.btn_complete_treat.setChecked(False)

            segment_id = util.global_data_map["segmentID"]
            self.cursor.execute("UPDATE SegmentInfo SET IsTreated = ? WHERE ID=?", (1, segment_id))
            util.db_conn.commit()
            with util.backup_db_conn:
                util.db_conn.backup(util.backup_db_conn)
            util.send_event_str(util.SetPage, 3)

        self.ui.btn_complete_treat.setChecked(False)

    def set_hour_format(self, flag):
        self.is_24_hour_format = flag

    def show_time(self):
        if self.is_24_hour_format:
            self.ui.label_datetime.text = datetime.now().strftime("%m/%d %H:%M")
            return
        self.ui.label_datetime.text = datetime.now().strftime("%m/%d %I:%M %p")

    def set_status_info(self, info, flag):
        if flag == 'g':
            self.ui.label_info.setStyleSheet('''
                font: 28px;
                color: #FFFFFF;
                background: rgba(60,193,129,51);
                border-radius: 0px;
            ''')
            self.ui.label.setPixmap(qt.QPixmap(self.resourcePath('Icons/green.png')))
        elif flag == 'y':
            self.ui.label_info.setStyleSheet('''
                font: 28px;
                color: #FFFFFF;
                background: rgba(255, 221, 51,51);
                border-radius: 0px;
            ''')
            self.ui.label.setPixmap(qt.QPixmap(self.resourcePath('Icons/yellow.png')))
        elif flag == 'r':
            self.ui.label_info.setStyleSheet('''
                font: 28px;
                color: #FFFFFF;
                background: rgba(255, 102, 102,51);
                border-radius: 0px;
            ''')
            self.ui.label.setPixmap(qt.QPixmap(self.resourcePath('Icons/red.png')))
        self.ui.label_info.text = info

    def clear_status_info(self):
        self.ui.label_info.text = ""
        self.ui.label_info.setStyleSheet('''
            font: 28px;
            color: #FFFFFF;
            background: rgba(60,193,129,51);
            border-radius: 0px;
        ''')
        self.ui.label.clear()

    def start_toggle(self):
        self.toggle_timer.start(500)

    def stop_toggle(self):
        self.toggle_timer.stop()

    def toggle_color(self):
        if self.blinking:
            self.ui.label_2.setStyleSheet('''
                background: #E2B134;
                border-radius: 14px;
            ''')
        else:
            self.ui.label_2.setStyleSheet('''
                background: #212121;
                border-radius: 14px;
            ''')
        self.blinking = not self.blinking

    def set_water_bladder_status(self, status):
        # print(f"blob status {status}")
        if status == 0:
            self.ui.label_2.setStyleSheet('''
                background: #3CC181;
                border-radius: 14px;
            ''')
        elif status == 1:
            self.ui.label_2.setStyleSheet('''
                background: #E2B134;
                border-radius: 14px;
            ''')
        elif status == 2:
            self.ui.label_2.setStyleSheet('''
                background: #FF513A;
                border-radius: 14px;
            ''')
        else:
            self.ui.label_2.setStyleSheet('''
                background: #212121;
                border-radius: 14px;
            ''')
