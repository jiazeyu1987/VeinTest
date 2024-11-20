import imp
import os
from re import A
from tabnanny import check
from time import sleep
import unittest
import logging
import vtk, qt, ctk, slicer
from slicer.ScriptedLoadableModule import *
from slicer.util import VTKObservationMixin
import slicer.util as util
import SlicerWizard.Utilities as su
import numpy as np
from Base.JBaseExtension import JBaseExtensionWidget
import math
import qt
from Controls.TherapyView import TherapyView
import sqlite3

#
# JURRobotArm
#

class AlertDialog(qt.QDialog):
    def __init__(self, message, button_text, button_callback, argument, parent=None):
        super().__init__(parent)
        self.initUI(message, button_text, button_callback, argument)

    def initUI(self, message, button_text, button_callback, argument):
        print("executing alert")
        self.setWindowTitle('')  # Hide title bar
        layout = qt.QVBoxLayout()

        # Add label to display message
        self.label = qt.QLabel(message, self)
        layout.addWidget(self.label)

        # Add button and connect to the provided callback
        self.button = qt.QPushButton(button_text, self)
        # self.button.clicked.connect(button_callback)
        self.button.clicked.connect(lambda: button_callback(argument))
        layout.addWidget(self.button)

        self.setLayout(layout)
        self.setModal(True)
        self.show()


class JURRobotArm(ScriptedLoadableModule):

    def __init__(self, parent):
        ScriptedLoadableModule.__init__(self, parent)
        self.parent.title = "JURRobotArm"  # TODO: make this more human readable by adding spaces
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
# JURRobotArmWidget
#

class JURRobotArmWidget(JBaseExtensionWidget):
    index = 0
    cb_path = ""
    bc_path = ""
    mh_path = ""
    hm_path = ""
    is_connected = False
    map_info = {}

    def setup(self):
        super().setup()
        self.ui.tabWidget.tabBar().hide()

        self.ui.pushButton.connect('clicked()',self.on_init)

        self.EMERGENCY_STOPPED_RESET = 1
        self.PROTECTIVE_STOPPED_RESET = 1
        self.IS_PROGRAM_RUNNING = 0
        self.MARGIN = 50
        self.ui.btn_disconnect.connect('clicked()', self.on_robot_arm_disconnect)
        self.ui.btn_connect.connect('clicked()', self.on_robot_arm_connect)
        self.ui.btn_robot_arm_stop.connect('clicked()', self.on_robot_arm_stop)
        self.ui.btn_rotate.connect('clicked()', self.on_btn_rotate)
        self.ui.btn_random_position.connect('clicked()', self.on_robot_position)
        self.ui.btn_set_tool.connect('clicked()', self.on_set_tool)
        self.ui.clear_alarm.connect('clicked()', self.on_clear_alarm)
        self.ui.set_collapse_sensitivity.connect('clicked()', self.on_set_collapse_sensitivity)
        self.ui.btn_set_speed.connect('clicked()', self.on_set_speed)
        # self.ui.btn_move_up.connect('clicked()', self.move_up)
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
        # Joint position
        self.ui.btn_move_joint_1_positive.pressed.connect(lambda: self.start_move_joint("1", "positive"))
        self.ui.btn_move_joint_1_positive.released.connect(self.stop_move)
        self.ui.btn_move_joint_1_negative.pressed.connect(lambda: self.start_move_joint("1", "negative"))
        self.ui.btn_move_joint_1_negative.released.connect(self.stop_move)
        self.ui.btn_move_joint_2_positive.pressed.connect(lambda: self.start_move_joint("2", "positive"))
        self.ui.btn_move_joint_2_positive.released.connect(self.stop_move)
        self.ui.btn_move_joint_2_negative.pressed.connect(lambda: self.start_move_joint("2", "negative"))
        self.ui.btn_move_joint_2_negative.released.connect(self.stop_move)
        self.ui.btn_move_joint_3_positive.pressed.connect(lambda: self.start_move_joint("3", "positive"))
        self.ui.btn_move_joint_3_positive.released.connect(self.stop_move)
        self.ui.btn_move_joint_3_negative.pressed.connect(lambda: self.start_move_joint("3", "negative"))
        self.ui.btn_move_joint_3_negative.released.connect(self.stop_move)
        self.ui.btn_move_joint_4_positive.pressed.connect(lambda: self.start_move_joint("4", "positive"))
        self.ui.btn_move_joint_4_positive.released.connect(self.stop_move)
        self.ui.btn_move_joint_4_negative.pressed.connect(lambda: self.start_move_joint("4", "negative"))
        self.ui.btn_move_joint_4_negative.released.connect(self.stop_move)
        self.ui.btn_move_joint_5_positive.pressed.connect(lambda: self.start_move_joint("5", "positive"))
        self.ui.btn_move_joint_5_positive.released.connect(self.stop_move)
        self.ui.btn_move_joint_5_negative.pressed.connect(lambda: self.start_move_joint("5", "negative"))
        self.ui.btn_move_joint_5_negative.released.connect(self.stop_move)
        self.ui.btn_move_joint_6_positive.pressed.connect(lambda: self.start_move_joint("6", "positive"))
        self.ui.btn_move_joint_6_positive.released.connect(self.stop_move)
        self.ui.btn_move_joint_6_negative.pressed.connect(lambda: self.start_move_joint("6", "negative"))
        self.ui.btn_move_joint_6_negative.released.connect(self.stop_move)

        # self.ui.btn_move_joint_1_positive.connect('pressed()', self.start_move_joint_1_positive)
        # self.ui.btn_move_joint_1_negative.connect('pressed()', self.start_move_joint_1_negative)
        # self.ui.btn_move_joint_2_positive.connect('pressed()', self.start_move_joint_2_positive)
        # self.ui.btn_move_joint_2_negative.connect('pressed()', self.start_move_joint_2_negative)
        # self.ui.btn_move_joint_3_positive.connect('pressed()', self.start_move_joint_3_positive)
        # self.ui.btn_move_joint_3_negative.connect('pressed()', self.start_move_joint_3_negative)
        # self.ui.btn_move_joint_4_positive.connect('pressed()', self.start_move_joint_4_positive)
        # self.ui.btn_move_joint_4_negative.connect('pressed()', self.start_move_joint_4_negative)
        # self.ui.btn_move_joint_5_positive.connect('pressed()', self.start_move_joint_5_positive)
        # self.ui.btn_move_joint_5_negative.connect('pressed()', self.start_move_joint_5_negative)
        # self.ui.btn_move_joint_6_positive.connect('pressed()', self.start_move_joint_6_positive)
        # self.ui.btn_move_joint_6_negative.connect('pressed()', self.start_move_joint_6_negative)
        self.robot_pos_list = [
            "-115.941, -120.35, 101.352, -84.631, 46.454, -5.334",
            "-113.8518, -112.1581, 90.118, -35.5823, 35.2602, 11.2884",
            "-113.8515, -112.1575, 90.118, -58.888, 111.4582, 2.5823",
            "-114.6216, -107.9574, 84.3776, -63.2757, 130.1117, 22.1925",
            "-115.7309, -111.2218, 90.7069, -81.4595, 136.6507, -13.3274",
            "-115.1123, -102.2342, 72.8365, -37.103, 132.9254, -62.1436",
            "-124.2002, -109.8128, 94.2714, -59.4211, 141.8623, -80.6352",
            "-126.7195, -117.4132, 104.3407, -89.9926, 142.2463, -45.4199"
        ]
        # util.singleShot(2000,self.on_robot_arm_connect)
        slicer.mrmlScene.AddObserver(util.ReconnectEvent, self.OnReconnectEvent)

        self.ui.ads.setVisible(False)
        self.ui.clear_alarm.setVisible(False)
        self.ui.btn_rotate.setVisible(False)
        self.ui.btn_random_position.setVisible(False)
        self.ui.btn_robot_arm_stop.setVisible(False)
        self.ui.set_collapse_sensitivity.setVisible(False)
        self.ui.btn_set_speed.setVisible(False)

        self.ui.slider1.singleStep = 0.01
        self.ui.slider1.minimum = -360
        self.ui.slider1.maximum = 360
        self.ui.slider1.value = 0
        self.ui.slider1.setDecimals(2)
        self.ui.slider1.connect('valueChanged(double)', self.on_ctkSliderWidgetChanged1)

        self.ui.slider2.singleStep = 0.01
        self.ui.slider2.minimum = -360
        self.ui.slider2.maximum = 360
        self.ui.slider2.value = 0
        self.ui.slider2.setDecimals(2)
        self.ui.slider2.connect('valueChanged(double)', self.on_ctkSliderWidgetChanged2)

        self.ui.slider3.singleStep = 0.01
        self.ui.slider3.minimum = -360
        self.ui.slider3.maximum = 360
        self.ui.slider3.value = 0
        self.ui.slider3.setDecimals(2)
        self.ui.slider3.connect('valueChanged(double)', self.on_ctkSliderWidgetChanged3)

        self.ui.slider4.singleStep = 0.01
        self.ui.slider4.minimum = -360
        self.ui.slider4.maximum = 360
        self.ui.slider4.value = 0
        self.ui.slider4.setDecimals(2)
        self.ui.slider4.connect('valueChanged(double)', self.on_ctkSliderWidgetChanged4)

        self.ui.slider5.singleStep = 0.01
        self.ui.slider5.minimum = -360
        self.ui.slider5.maximum = 360
        self.ui.slider5.value = 0
        self.ui.slider5.setDecimals(2)
        self.ui.slider5.connect('valueChanged(double)', self.on_ctkSliderWidgetChanged5)

        self.ui.slider6.singleStep = 0.01
        self.ui.slider6.minimum = -360
        self.ui.slider6.maximum = 360
        self.ui.slider6.value = 0
        self.ui.slider6.setDecimals(2)
        self.ui.slider6.connect('valueChanged(double)', self.on_ctkSliderWidgetChanged6)
        self._init_database()
        self.init_extra()
        

    def _init_database(self):
        dbpath = os.path.join(util.mainWindow().GetProjectBasePath(), "Resources", "ccwssm")
        backup_dbpath = os.path.join(util.mainWindow().GetProjectBasePath(), "Resources", "zccwssm")
        # 创建数据库连接
        util.db_conn = sqlite3.connect(dbpath)
        util.backup_db_conn = sqlite3.connect(backup_dbpath)
        print(f'backup db----{util.backup_db_conn}')
        self.cursor = util.db_conn.cursor()

        # 创建用户表格
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username VARCHAR(255) NOT NULL unique,
                    password VARCHAR(255) NOT NULL,
                    role INTEGER DEFAULT 0,
                    registration_time DATETIME,
                    last_login_time DATETIME
                    )
            ''')

        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS PatientInfo (
                ID INTEGER PRIMARY KEY AUTOINCREMENT,
                UserID INTEGER NOT NULL,
                PatientID VARCHAR(52),
                Name VARCHAR(100),
                Birthday VARCHAR(100),
                Age INTEGER,
                Gender INTEGER,
                TreatType INTEGER,
                Degree INTEGER,
                IsRelapse INTEGER,
                IsTreated INTEGER,
                Note VARCHAR(500),
                treatment_instruction VARCHAR(500),
                TreatTime VARCHAR(100),
                CreateTime VARCHAR(100),
                ModifyTime VARCHAR(100)
            )
        ''')

        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS VeinInfo (
                ID INTEGER PRIMARY KEY AUTOINCREMENT,
                PatientID VARCHAR(52),
                VeinName VARCHAR(100)
            )
        ''')

        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS SegmentInfo (
                ID INTEGER PRIMARY KEY AUTOINCREMENT,
                VeinID INTEGER,
                SegmentName VARCHAR(100),
                IsTreated INTEGER DEFAULT 0
            )
        ''')

        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS PointInfo (
                ID INTEGER PRIMARY KEY AUTOINCREMENT,
                SegmentID INTEGER,
                PointName VARCHAR(50),
                Count INTEGER DEFAULT 0,
                IsTreated INTEGER DEFAULT 0
            )
        ''')

        self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS SegmentImagesInfo (
                    ID INTEGER PRIMARY KEY AUTOINCREMENT,
                    PointID INTEGER,
                    ImagePath VARCHAR(300),
                    TreatPower INTEGER DEFAULT 0,
                    Width FLOAT DEFAULT 0.0,
                    Circle FLOAT DEFAULT 0.0,
                    CoolTime FLOAT DEFAULT 0.0,
                    TotalTime FLOAT DEFAULT 0.0,
                    TotalEnergy FLOAT DEFAULT 0.0,
                    flag TINYINT DEFAULT 0,
                    CreateTime VARCHAR(100),
                    ModifyTime VARCHAR(100)
                )
            ''')

        util.db_conn.commit()
        with util.backup_db_conn:
            util.db_conn.backup(util.backup_db_conn)

    def init_extra(self):
        self.ui.btn_pre.setStyleSheet(util.button2_style.format("21"))
        self.ui.btn_pre.setIcon(qt.QIcon(self.resourcePath('Icons/pre.png')))
        self.ui.btn_pre.clicked.connect(self.on_pre_pos)
        self.ui.btn_next.setStyleSheet(util.button2_style.format("21"))
        self.ui.btn_next.setIcon(qt.QIcon(self.resourcePath('Icons/next.png')))
        self.ui.btn_next.clicked.connect(self.on_next_pos)

        self.ui.btn_left.setStyleSheet(util.button2_style.format("21"))
        self.ui.btn_left.setIcon(qt.QIcon(self.resourcePath('Icons/left.png')))
        self.ui.btn_left.clicked.connect(self.on_left_pos)
        self.ui.btn_right.setStyleSheet(util.button2_style.format("21"))
        self.ui.btn_right.setIcon(qt.QIcon(self.resourcePath('Icons/right.png')))
        self.ui.btn_right.clicked.connect(self.on_right_pos)

        self.ui.btn_modify.setStyleSheet(util.button2_style.format("21"))
        self.ui.btn_modify.setIcon(qt.QIcon(self.resourcePath('Icons/modify.png')))
        self.ui.btn_modify.setIconSize(qt.QSize(32, 32))
        self.ui.btn_modify.toggled.connect(self._on_modify_step)
        self.ui.robot_step.setStyleSheet('''
                QComboBox {
                    background: transparent;
                    color: white;
                    font: 20px;
                }
                QComboBox::drop-down {
                    border: none;
                }
                QComboBox::down-arrow {
                    image: none;
                }
        ''')

        self.ui.vein_view.setStyleSheet(util.button2_style.format("32"))
        self.ui.vein_view.clicked.connect(self._changeView)
        self.vein_view_timer = qt.QTimer()
        self.vein_view_timer.timeout.connect(self._check_change_view_done)


        self.therapy_view = TherapyView()
        self.segment_id = 0
        self.init_extra_database()
        util.addWidget2(self.ui.widget_path, self.therapy_view)

    def on_init(self):
        self._setInitialPose()

    def _setInitialPose(self):
        result = util.getModuleWidget("JMessageBox").show_two_popup('是否确认初始位置及方向，进入治疗程序？')
        if result == qt.QDialog.Rejected:
            self.ui.btn_initial.setEnabled(False)
            return
        try:
            ret = util.getModuleWidget("RequestStatus").send_synchronize_cmd(f"UR, SetInitialPose")
            if not ret:
                raise RuntimeError("SetInitialPose returned False, cannot proceed forward.")
            util.send_event_str(util.SetPage, 4)

            # Proceed with the rest of the code if no error
            # print("SetInitialPose returned True, proceeding...")

        except RuntimeError as e:
            print(f"Error: {e}")


    def _changeView(self):
        # print("change view called [py]")
        try:
            #util.getModuleWidget("VeinConfigTop").set_status_info('治疗头位姿调整中', 'g')
            util.getModuleWidget("RequestStatus").send_cmd(f"UR, ChangeView, 1")
            self.vein_view_timer.start(500)
            # print("ChangeView returned, proceeding...")
        except RuntimeError as e:
            print(f"Error: {e}")

    def _check_change_view_done(self):
        if util.getModuleWidget("RequestStatus").send_synchronize_cmd(f"UR, IsRobotSteady") == "True":
            self.vein_view_timer.stop()
        return


    def init_extra_database(self):
        self.current_position = 1
        self.cursor = util.db_conn.cursor()
        self.cursor.execute(
            "SELECT ID,Count,IsTreated,s.ImagePath FROM PointInfo p LEFT JOIN (SELECT PointID,ImagePath,MAX(CreateTime) "
            "AS CreateTime FROM SegmentImagesInfo GROUP BY PointID) s ON p.ID = s.PointID WHERE SegmentID = ?",
            (self.segment_id,))
        Points = self.cursor.fetchall()
        # print(Points)
        self.pos_to_id = {index + 1: list(value) for index, value in enumerate(Points)}
        if not self.pos_to_id:
            self.therapy_view.addNewPos()
            self.therapy_view.setPointLabel()
            self.cursor.execute('''INSERT INTO PointInfo (SegmentID,PointName)
            VALUES (?, ?)''',
                                (self.segment_id, 'P' + str(self.current_position)))
            self.point_id = str(self.cursor.lastrowid)
            util.db_conn.commit()
            with util.backup_db_conn:
                util.db_conn.backup(util.backup_db_conn)
            self.pos_to_id[self.current_position] = [self.point_id, 0, 0]
            return

        # print(self.pos_to_id)
        for key, value in self.pos_to_id.items():
            self.therapy_view.addNewPos()
            if value[2] == 1:
                self.therapy_view.setPosTherapied(key - 1)
            if value[3]:
                before, after = value[3].split(';')
                self.images[key][0] = before
                self.images[key][1] = after
            break

        self.point_id = self.pos_to_id[self.current_position][0]
        self.therapy_view.setPointLabel()
        self.therapy_view.setTherapyCountLabel(self.pos_to_id[self.current_position][1])

    def on_next_pos(self):
        new_flag = self.therapy_view.nextPos()
        self.current_position += 1
        if new_flag:
            self.cursor.execute('''INSERT INTO PointInfo (SegmentID,PointName)
            VALUES (?, ?)''',
                                (self.segment_id, 'P' + str(self.current_position)))
            self.point_id = str(self.cursor.lastrowid)
            util.db_conn.commit()
            with util.backup_db_conn:
                util.db_conn.backup(util.backup_db_conn)
            self.pos_to_id[self.current_position] = [self.point_id, 0, 0]
        self.point_id = self.pos_to_id[self.current_position][0]
        self.therapy_view.setPointLabel()
        self.on_next()
        self.therapy_view.setTherapyCountLabel(self.pos_to_id[self.current_position][1])
        util.getModuleWidget("VeinConfigTop").set_status_info(f'后位移{self.ui.robot_step.currentText[0]}mm', 'g')
        self.vein_view_timer.start(100)

    def on_next(self):
        # import random
        # self.ui.label_3.setText(f"{random.randint(-150, 150), random.randint(-150, 150)}")
        # pass
        print("on next called [py]")
        try:
            ret = util.getModuleWidget("RequestStatus").send_synchronize_cmd(f"UR, MoveToNextPose")
            if not ret:
                raise RuntimeError("MoveToNextPose returned False, cannot proceed forward.")

            # Proceed with the rest of the code if no error
            print("MoveToNextPose returned True, proceeding...")

        except RuntimeError as e:
            print(f"Error: {e}")

    def on_pre(self):
        # import random
        # self.ui.label_3.setText(f"{random.randint(-150, 150), random.randint(-150, 150)}")
        # pass
        print("on previous called [py]")
        try:
            ret = util.getModuleWidget("RequestStatus").send_synchronize_cmd(f"UR, MoveToPrevPose")
            if not ret:
                raise RuntimeError("MoveToPrevPose returned False, cannot proceed forward.")

            # Proceed with the rest of the code if no error
            print("MoveToPrevPose returned True, proceeding...")

        except RuntimeError as e:
            print(f"Error: {e}")

    def on_pre_pos(self):
        self.current_position -= 1
        if self.current_position < 1:
            self.current_position = 1
        self.therapy_view.prePos()
        self.therapy_view.setPointLabel()
        self.on_pre()
        self.point_id = self.pos_to_id[self.current_position][0]
        self.therapy_view.setTherapyCountLabel(self.pos_to_id[self.current_position][1])
        util.getModuleWidget("VeinConfigTop").set_status_info(f'前位移{self.ui.robot_step.currentText[0]}mm', 'g')
        self.vein_view_timer.start(100)

    def on_left_pos(self):
        util.getModuleWidget("VeinConfigTop").set_status_info(f'左位移{self.ui.robot_step.currentText[0]}mm', 'g')
        self.vein_view_timer.start(100)
        pass

    def on_right_pos(self):
        util.getModuleWidget("VeinConfigTop").set_status_info(f'右位移{self.ui.robot_step.currentText[0]}mm', 'g')
        self.vein_view_timer.start(100)
        pass
    

    def _on_modify_step(self, checked):
        if checked:
            self.ui.robot_step.setStyleSheet('''
                QComboBox {
                    background: #232428;
                    border-radius: 4px;
                    font: 20px;
                    border: 1px solid #699FC3
                    }
                QComboBox::down-arrow {
                    width: 10px;
                    height: 10px;
                    padding-left: 8px;
                }
            ''')
            self.ui.robot_step.setEnabled(True)
        else:
            self.ui.robot_step.setStyleSheet('''
                QComboBox {
                    background: transparent;
                    color: white;
                    font: 20px;
                }
                QComboBox::drop-down {
                    border: none;
                }
                QComboBox::down-arrow {
                    image: none;
                }
            ''')
            self.ui.robot_step.setEnabled(False)
            self.setStepValue()

    def setStepValue(self):
        print("set step value called [py]")
        try:
            ret = util.getModuleWidget("RequestStatus").send_synchronize_cmd(
                f"UR, SetStepValue, {int(self.ui.robot_step.currentText[0])}")
            if not ret:
                raise RuntimeError("SetStepValue returned False, cannot proceed forward.")

            # Proceed with the rest of the code if no error
            print("SetStepValue returned True, proceeding...")

        except RuntimeError as e:
            print(f"Error: {e}")


    def on_ctkSliderWidgetChanged1(self, value):
        # print("on ctk slider widgeet:",self.ui.ctkSliderWidget1.value)
        pass

    def on_ctkSliderWidgetChanged2(self, value):
        # print("on ctk slider widgeet:",self.ui.ctkSliderWidget2.value)
        pass

    def on_ctkSliderWidgetChanged3(self, value):
        # print("on ctk slider widgeet:",self.ui.ctkSliderWidget3.value)
        pass

    def on_ctkSliderWidgetChanged4(self, value):
        # print("on ctk slider widgeet:",self.ui.ctkSliderWidget4.value)
        pass

    def on_ctkSliderWidgetChanged5(self, value):
        # print("on ctk slider widgeet:",self.ui.ctkSliderWidget5.value)
        pass

    def on_ctkSliderWidgetChanged6(self, value):
        # print("on ctk slider widgeet:",self.ui.ctkSliderWidget6.value)
        pass

    def reuploadScript(self):
        # print("reuploading script [py]")
        util.getModuleWidget("RequestStatus").send_cmd("UR, ReuploadScript")
        if not self.IS_PROGRAM_RUNNING:
            util.singleShot(500, self.reuploadScript)
        print("pro run")

    def shellButton(self, argument):
        print("shell called")
        ret = util.getModuleWidget("RequestStatus").send_synchronize_cmd(f"UR, {argument}")
        if ret == "True":
            self.reuploadScript()

    @vtk.calldata_type(vtk.VTK_OBJECT)
    def OnReconnectEvent(self, caller, str_event, calldata):
        val = calldata.GetAttribute("value")
        if val == "UR":
            self.on_robot_arm_connect()

    def tickEvent(self, value):
        map_info = {}
        info_list_str = value.split("*V* ")
        for row in info_list_str:
            if row == "":
                continue
            key_value_pair_list = row.split("*U* ")
            if (len(key_value_pair_list) != 2):
                continue
            key = key_value_pair_list[0]
            value = key_value_pair_list[1]
            map_info[key] = value
        self.map_info = map_info
        self.ui.textEdit.clear()
        util.getModuleWidget("RDNDevice").check_map['robot'] = False
        if "connect_status" in map_info and map_info["connect_status"] == "-1":
            self.ui.L1.setText("未连接")
            self.ui.L1.setStyleSheet("color: red;")
        elif "connect_status" in map_info and map_info["connect_status"] == "0":
            self.ui.L1.setText("停止")
            self.ui.L1.setStyleSheet("color: yellow;")
            util.getModuleWidget("RDNDevice").check_map['robot'] = True
        elif "connect_status" in map_info and map_info["connect_status"] == "1":
            self.ui.L1.setText("暂停")
            self.ui.L1.setStyleSheet("color: yellow;")
            util.getModuleWidget("RDNDevice").check_map['robot'] = True
        elif "connect_status" in map_info and map_info["connect_status"] == "2":
            self.ui.L1.setText("急停")
            self.ui.L1.setStyleSheet("color: red;")
            util.getModuleWidget("RDNDevice").check_map['robot'] = True
        elif "connect_status" in map_info and map_info["connect_status"] == "3":
            self.ui.L1.setText("运行")
            self.ui.L1.setStyleSheet("color: green;")
            util.getModuleWidget("RDNDevice").check_map['robot'] = True
        elif "connect_status" in map_info and map_info["connect_status"] == "4":
            self.ui.L1.setText("报警")
            self.ui.L1.setStyleSheet("color: red;")
            util.getModuleWidget("RDNDevice").check_map['robot'] = True
        elif "connect_status" in map_info and map_info["connect_status"] == "5":
            self.ui.L1.setText("碰撞")
            self.ui.L1.setStyleSheet("color: red;")
            util.getModuleWidget("RDNDevice").check_map['robot'] = True
        else:
            self.ui.L1.setText("未连接")
            self.ui.L1.setStyleSheet("color: red;")

        if "flange_pos" in map_info:
            poslist = map_info["flange_pos"].split(",")
            posarray = []
            for pos in poslist:
                pos_float = round(float(pos), 1)
                posarray.append(pos_float)
            self.ui.textEdit.append("FPOS:" + " , ".join(map(str, posarray)))

        if "tcp_pos" in map_info:
            self.ui.textEdit.append("TPOS:" + map_info["tcp_pos"])
            util.global_data_map["tcp_pos"] = map_info["tcp_pos"]

        if "joint_positions" in map_info:
            util.global_data_map["joint_positions"] = map_info["joint_positions"]
            radian_list = map_info['joint_positions'].split(",")
            degree_list = [round(math.degrees(float(radian)), 2) for radian in radian_list]
            self.ui.slider1.value = degree_list[0]
            self.ui.slider2.value = degree_list[1]
            self.ui.slider3.value = degree_list[2]
            self.ui.slider4.value = degree_list[3]
            self.ui.slider5.value = degree_list[4]
            self.ui.slider6.value = degree_list[5]

        if "joint_velocities" in map_info:
            util.global_data_map["joint_velocities"] = map_info["joint_velocities"]

        if "IS_DIGITAL_TOOL_INPUT_0" in map_info and "IS_FREEDRIVE_STATE" in map_info:
            # print("both in map")
            if map_info["IS_DIGITAL_TOOL_INPUT_0"] == "1":
                # print("tool in 0 is 1")
                if map_info["IS_FREEDRIVE_STATE"] == "0":
                    print("caling fd [py]")
                    util.getModuleWidget("RequestStatus").send_cmd(f"UR, StartFreedriveMode")
                    util.getModuleWidget("VeinConfig").overlay_robot()
                    util.getModuleWidget("VeinTreat").overlay_robot()
            else:
                # print("tool in 0 is 0")
                if map_info["IS_FREEDRIVE_STATE"] == "1":
                    print("stopping fd [py]")
                    util.getModuleWidget("RequestStatus").send_cmd(f"UR, EndFreedriveMode")
                    util.getModuleWidget("VeinConfig").show_robot()
                    util.getModuleWidget("VeinTreat").show_robot()

        if "IS_NORMAL_MODE" in map_info and map_info["IS_NORMAL_MODE"] == "1":
            # print("[Safety Status] : Normal mode")
            self.EMERGENCY_STOPPED_RESET = 1
            self.PROTECTIVE_STOPPED_RESET = 1
        # if "IS_EMERGENCY_STOPPED" in map_info and map_info["IS_EMERGENCY_STOPPED"] == "1":
        #     print("[Safety Status] : Emergency stopped")
        #     if self.EMERGENCY_STOPPED_RESET == 1:
        #         msg = "Emergency Stop"
        #         btn_txt = "xxx"
        #         argument = "EnableRobotAfterEmergency"
        #         print("calling alert")
        #         print("finishing alert")
        #         self.EMERGENCY_STOPPED_RESET = 0
        if "IS_PROTECTIVE_STOPPED" in map_info and map_info["IS_PROTECTIVE_STOPPED"] == "1":
            print("[Safety Status] : Protective stopped")
            if self.PROTECTIVE_STOPPED_RESET == 1:
                msg = "Protective Stop"
                btn_txt = "xxx"
                argument = "EnableRobotAfterProtective"
                print("calling alert")
                util.getModuleWidget("JMessageBox").show_protective_stop('Protective Stop')
                print("finishing alert")
                self.PROTECTIVE_STOPPED_RESET = 0
        if "IS_PROGRAM_RUNNING" in map_info:
            self.IS_PROGRAM_RUNNING = 1 if map_info.get("IS_PROGRAM_RUNNING") == "1" else 0

        if "IS_DIGITAL_TOOL_INPUT_1" in map_info:
            util.global_data_map["IS_DIGITAL_TOOL_INPUT_1"] = map_info["IS_DIGITAL_TOOL_INPUT_1"]
            print(f'TI 1 : {map_info["IS_DIGITAL_TOOL_INPUT_1"]}')
            util.getModuleWidget("VeinTreat").update_debug_info(map_info["IS_DIGITAL_TOOL_INPUT_1"])

        if "distance_value" in map_info:
            try:
                print(f'd-dist : {map_info["distance_value"]}')
                dist_val = float(map_info["distance_value"])
                print(f"dist : {dist_val}")
                print(f'dist - margin : {dist_val - self.MARGIN}')
                print(f'dist + margin : {dist_val + self.MARGIN}')
            except Exception as e:
                print(f"An error occurred: {e}")
            if (dist_val < 200 or dist_val > 600):
                print("calling status with 1")
                util.getModuleWidget("VeinConfig").update_sport_status(1)
                util.getModuleWidget("VeinTreat").update_sport_status(1)
            elif (dist_val - self.MARGIN < 200 or dist_val + self.MARGIN > 600):
                print("calling status with 2")
                util.getModuleWidget("VeinConfig").update_sport_status(2)
                util.getModuleWidget("VeinTreat").update_sport_status(2)
            else:
                print("calling status with 0")
                util.getModuleWidget("VeinConfig").update_sport_status(0)
                util.getModuleWidget("VeinTreat").update_sport_status(0)

        if "virutal_output" in map_info:
            if map_info["virutal_output"] == "1":
                self.ui.textEdit.append("虚拟输出IO:打开")
            else:
                self.ui.textEdit.append("虚拟输出IO:关闭")

        if "tool_number" in map_info:
            self.ui.textEdit.append("工具ID:" + map_info["tool_number"])

        collapse_str = ""
        if "collapse_state" in map_info:
            if map_info["collapse_state"] == "1":
                collapse_str = "发生了碰撞"
            else:
                collapse_str = "未发生碰撞"

        if "collapse_sensitivity" in map_info:
            collapse_str = collapse_str + "->碰撞灵敏度：" + map_info["collapse_sensitivity"]
        self.ui.textEdit.append(collapse_str)

        if "speed" in map_info:
            self.ui.textEdit.append("速度：" + map_info["speed"])

        if "IS_DIGITAL_TOOL_INPUT_1" in map_info:
            util.global_data_map["IS_DIGITAL_TOOL_INPUT_1"] = map_info["IS_DIGITAL_TOOL_INPUT_1"]

        pass

    def on_robot_arm_self_check(self):
        widget = util.getModuleWidget("robotArm")
        if widget is None:
            util.showWarningText("没有加载robotArm模块")
            return
        widget.PushbtnOpenRobot()

    def on_set_speed(self):
        import random
        random_number = random.randint(10, 50)
        util.getModuleWidget("RequestStatus").send_cmd(f"UR, SetSpeed, {random_number}")

    def on_set_collapse_sensitivity(self):
        import random
        random_number = random.randint(10, 50)
        util.getModuleWidget("RequestStatus").send_cmd(f"UR, SetCollapseSensitivity, {random_number}")

    def on_clear_alarm(self):
        util.getModuleWidget("RequestStatus").send_cmd("UR, ClearAlarm")

    def on_set_tool(self):
        intval = self.ui.comboboxToolNum_2.currentIndex
        util.getModuleWidget("RequestStatus").send_cmd(f"UR, SetTool, {intval}")

    def on_btn_rotate(self):
        util.getModuleWidget("RequestStatus").send_cmd(
            "UR, Rotate, -115.941,-120.35,101.352,-84.631,46.454,-5.334, 0, 0, 0, 0")

    def on_robot_arm_connect(self):
        util.getModuleWidget("RequestStatus").send_cmd(f"UR, Connect, {self.ui.comboBox.currentText}, 30004")
        # util.getModuleWidget("RequestStatus").send_cmd("UR, Open")

    def on_robot_arm_disconnect(self):
        util.getModuleWidget("RequestStatus").send_cmd("UR, DisConnect")

    def start_move_up(self):
        util.getModuleWidget("RequestStatus").send_cmd("UR, StartMoveUp")

    def start_move_down(self):
        util.getModuleWidget("RequestStatus").send_cmd("UR, StartMoveDown")

    def start_move_right(self):
        util.getModuleWidget("RequestStatus").send_cmd("UR, StartMoveRight")

    def start_move_left(self):
        util.getModuleWidget("RequestStatus").send_cmd("UR, StartMoveLeft")

    def start_move_back(self):
        util.getModuleWidget("RequestStatus").send_cmd("UR, StartMoveBack")

    def start_move_front(self):
        util.getModuleWidget("RequestStatus").send_cmd("UR, StartMoveFront")

    def stop_move(self):
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
        util.getModuleWidget("RequestStatus").send_cmd("UR, StartRotateZPositive")

    def start_rotate_z_negative(self):
        util.getModuleWidget("RequestStatus").send_cmd("UR, StartRotateZNegative")

    def start_move_joint(self, jt, dir):
        print(f"Calling start move joint {jt} in {dir} : py")
        util.getModuleWidget("RequestStatus").send_cmd(f"UR, StartMoveJoint, {jt}, {dir}")

    # def stop_move_joint(self,jt):
    #   print(f"stop move joint {jt}")

    def start_move_joint_1_positive(self):
        print(f"start move joint - pos")
        # util.getModuleWidget("RequestStatus").send_cmd("UR, StartMoveJoint1Positive")

    def start_move_joint_1_negative(self):
        print(f"start move joint - neg")
        # util.getModuleWidget("RequestStatus").send_cmd("UR, StartMoveJoint1Negative")

    # 调用插件里的槽函数，获得位姿并通过观察者模式传递到主框架
    def get_robot_position(self):
        widget = util.getModuleWidget("robotArm")
        if widget is None:
            util.showWarningText("cann't load robotArm in on_robot_position.")
            return
        self.robot_pose = widget.PushbtnGetPoseOuter()
        # print('get tcp pose...')

    def on_robot_arm_stop(self):
        util.getModuleWidget("RequestStatus").send_cmd("UR, Stop")

    def on_robot_arm_initialize(self):
        widget = util.getModuleWidget("robotArm")
        if widget is None:
            util.showWarningText("没有加载robotArm模块")
            return
        widget.PushbtnConnect()  # 连接机械臂
        widget.PushbtnOpenRobot()  # 机械臂自检
        widget.PushbtnGetPoseOuter()  # 机械臂先获取一下点
        self.is_connected = True

    def on_robot_position(self):
        if self.index > len(self.robot_pos_list) - 1:
            print('robot move end in base eye calib.')
            self.index = 0
            return
        self.move_robot_to_random_position(self.robot_pos_list[self.index])
        self.index += 1

    # 移动到预定位置，输入6个关节角度并转成字符串
    def move_robot_to_random_position(self, random_pos, mode='pose'):
        if mode == 'joint':
            print("---------------------", random_pos)
            util.getModuleWidget("RequestStatus").send_cmd(f"UR, MoveByJoint, {random_pos}, 20")
        elif mode == 'pose':
            random_pos = "0.259, 0.306, 0.360, 3.148, -1.842, -0.161"
            util.getModuleWidget("RequestStatus").send_cmd(f"UR, MoveByTCP, {random_pos}, 20")
        else:
            print('mode input error in robot move.')

    # 移动到预定位置，直线运动
    def move2positionByLine(self, random_pos, mode='joint'):
        widget = util.getModuleWidget("robotArm")
        if widget is None:
            util.showWarningText("没有加载robotArm模块")
            return
        if mode == 'joint':
            # random_pos = "0,-90,0,-90,180,0"
            widget.PushbtnMovetoPosbyLineOuter(random_pos)
        elif mode == 'pose':
            widget.PushbtnMovetoPosebyLineOuter(random_pos)
        else:
            print('mode input error in robot move.')

    def sendCMD(self, cmd, params=None, id="1"):
        import json
        if (not params):
            params = []
        else:
            params = json.dumps(params)  # 转Json格式
        sendStr = "{{\"method\":\"{0}\",\"params\":{1},\"jsonrpc\":\"2.0\",\"id\":{2}}}".format(cmd, params, id) + "\n"
        # print(sendStr)
        try:
            self.sock.sendall(bytes(sendStr, "utf-8"))
            ret = self.sock.recv(1024)
            jdata = json.loads(str(ret, "utf-8"))
            if ("result" in jdata.keys()):
                return (True, json.loads(jdata["result"]), jdata["id"])
            elif ("error" in jdata.keys()):
                return (False, jdata["error"], jdata["id"])
            else:
                return (False, None, None)

        except Exception as e:
            return (False, None, None)

    def wait_stop(self):
        import time
        while True:
            time.sleep(0.05)
            ret1, result1, id1 = self.sendCMD("getRobotState")
            # print(ret1,result1)
            if (ret1):
                if result1 == 0 or result1 == 4:
                    break
            else:
                print("getRobotState failed")
                break

    def WaitBrakeOpen(self):
        import time
        brakeopen = [0, 0, 0, 0, 0, 0]
        # 获取伺服抱闸打开情况
        suc, brakeopen, id = self.sendCMD("get_servo_brake_off_status")
        b_sum = 0

        # brakeopen为6个轴 抱闸打开情况，打开为1，不然为0，全部打开为[1,1,1,1,1,1]
        for d in brakeopen:
            b_sum = b_sum + d

        while b_sum != 6:
            # 获取伺服抱闸打开情况
            suc, brakeopen, id = self.sendCMD("get_servo_brake_off_status")
            b_sum = 0
            for d in brakeopen:
                b_sum = b_sum + d
            time.sleep(0.1)
            # 等待6个轴全部打开

    def openRobot(self):
        import time
        suc, rb_state, id = self.sendCMD("getRobotState")
        # 停止状态 0，暂停状态 1，急停状态 2，运行状态 3，报警状态 4，碰撞状态 5
        print('机器人状态：', rb_state)
        # 获取虚拟输出 IO 状态（初始化状态）参数： addr：虚拟 IO 地址，范围：int [400,1535]

        # m473:1表示初始化状态，0表示完成初始化状态
        suc, rb_ini_state, id = self.sendCMD("getVirtualOutput", {"addr": 473})
        if rb_state == 4 or rb_ini_state == 1:
            # 清除报警
            suc, result, id = self.sendCMD("clearAlarm")
            # 获取伺服抱闸打开情况
            self.WaitBrakeOpen()

        # 获取同步状态
        suc, Motorstatus, id = self.sendCMD("getMotorStatus")
        if Motorstatus == 0:
            # 同步伺服编码器数据
            suc, syncMotorStatus, id = self.sendCMD("syncMotorStatus")
        # 设置伺服使能状态
        suc, servostatus, id = self.sendCMD("set_servo_status", {"status": 1})
        # 获取精确状态
        suc, rb_calib, id = self.sendCMD("getVirtualOutput", {"addr": 472})
        # m472为0表示未校准状态，1表示完成校准

        if rb_calib == 0:
            # 编码器零位校准
            suc, result, id = self.sendCMD("calibrate_encoder_zero_position")
            suc, rb_calib, id = self.sendCMD("getVirtualOutput", {"addr": 472})
            while rb_calib == 0:
                suc, rb_calib, id = self.sendCMD("getVirtualOutput", {"addr": 472})
                time.sleep(0.1)

            print("编码器校准成功")

    def setRobotSpeed(self, speed):
        # 修改机械臂的速度
        suc, result, id = self.sendCMD("setSpeed", {"value": speed})

    def moveByJoint(self, pos):
        suc, result, id = self.sendCMD("moveByJoint", {"targetPos": pos, "speed": 20, "acc": 20, "dec": 20})

    def on_instrument_check(self):
        import socket, time
        import json
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.sock.connect(("172.30.38.11", 8055))
        except OSError as e:
            self.sock = self.sock

        self.openRobot()
        print("OPEN------------------------------------------------")
        self.setRobotSpeed(20)
        print("Robot Speed Set Done! ------------------------------")
