from gc import is_tracked

import subprocess
from collections import defaultdict

import slicer
import vtk
from slicer.ScriptedLoadableModule import *
from slicer.util import VTKObservationMixin
from TreatTools.EditDialog import EditDialog
from TreatTools.ProgressButton import ProgressButton
from TreatTools.LineWidget import LineWidget
from RDNTool.UltraSoundSettingPanel import UltraSoundSettingPanel
import qt
from datetime import datetime
import os
import math
import numpy as np
import sqlite3


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


class CompareDialog:
    def __init__(self, img_before=None, img_after=None):
        self.module_path = os.path.dirname(slicer.util.modulePath("VeinTreat"))
        self.uiWidget = slicer.util.loadUI(self.module_path + '/Resources/UI/CompareDialog.ui')
        self.uiWidget.setWindowFlag(qt.Qt.FramelessWindowHint | qt.Qt.Tool | qt.Qt.WindowStaysOnTopHint)

        self.ui = slicer.util.childWidgetVariables(self.uiWidget)

        self.img_before = img_before
        self.img_after = img_after

        self._init_ui()

    def _init_ui(self):
        self.ui.btn_close.setIcon(qt.QIcon(self.module_path + '/Resources/Icons/close.png'))
        self.ui.btn_close.setIconSize(qt.QSize(42, 42))
        self.ui.btn_close.setStyleSheet('''
            border: none;
            background: transparent;
        ''')
        self.ui.btn_close.clicked.connect(self._on_reject)

        self.ui.img_before.setStyleSheet('''
            background: #000000;
            border-radius: 0px 0px 0px 0px;
        ''')
        self.ui.img_after.setStyleSheet('''
            background: #000000;
            border-radius: 0px 0px 0px 0px;
        ''')
        # print(self.img_before, self.img_after)
        if self.img_before:
            self.ui.img_before.setPixmap(qt.QPixmap(self.img_before).scaled(760, 748))
            self.ui.img_after.setPixmap(qt.QPixmap(self.img_after).scaled(760, 748))

    def exec_(self):
        return self.uiWidget.exec_()

    def _on_reject(self):
        self.uiWidget.reject()

    def _on_accept(self):
        self.uiWidget.accept()


#
# VeinConfig
#


class VeinTreat(ScriptedLoadableModule):
    """Uses ScriptedLoadableModule base class, available at:
    https://github.com/Slicer/Slicer/blob/main/Base/Python/slicer/ScriptedLoadableModule.py
    """

    def __init__(self, parent):
        ScriptedLoadableModule.__init__(self, parent)
        self.parent.title = "VeinTreat"  # TODO: make this more human readable by adding spaces
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


#
# LineIntensityProfileWidget
#


class VeinTreatWidget(ScriptedLoadableModuleWidget, VTKObservationMixin):
    """Uses ScriptedLoadableModuleWidget base class, available at:
    https://github.com/Slicer/Slicer/blob/main/Base/Python/slicer/ScriptedLoadableModule.py
    """

    def __init__(self, parent=None) -> None:
        """Called when the user opens the module the first time and the widget is initialized."""
        ScriptedLoadableModuleWidget.__init__(self, parent)
        VTKObservationMixin.__init__(self)  # needed for parameter node observation

    def setup(self) -> None:
        """Called when the user opens the module the first time and the widget is initialized."""
        ScriptedLoadableModuleWidget.setup(self)

        # Load widget from .ui file (created by Qt Designer).
        # Additional widgets can be instantiated manually and added to self.layout.
        self.uiWidget = slicer.util.loadUI(self.resourcePath("UI/VeinTreat.ui"))
        self.layout.addWidget(self.uiWidget)
        self.ui = slicer.util.childWidgetVariables(self.uiWidget)

        # Set scene in MRML widgets. Make sure that in Qt designer the top-level qMRMLWidget's
        # "mrmlSceneChanged(vtkMRMLScene*)" signal in is connected to each MRML widget's.
        # "setMRMLScene(vtkMRMLScene*)" slot.
        self.uiWidget.setMRMLScene(slicer.mrmlScene)

        self._init_ui()

    def enter(self):
        util.global_data_map['has_treat'] = False
        self.segment_id = util.global_data_map["segmentID"]
        self.ui.robot_step.setEnabled(False)
        self.ui.robot_step.setCurrentIndex(0)
        self.images.clear()
        self.init_extra_database()
        self.params = [0, 0, 0, 0, 0]
        self.treat_power = 0
        self.width = 0
        self.circle = 0
        self.cool_time = 0
        self.total_time = 0
        self.on_feedback()
        self.timer_feedback.start(1000)
        self.show_ultra()
        self.scrcpy_timer.start(200)
        self.setStepValue()

    def exit(self):
        util.removeFromParent2(util.ultra_container)
        self.timer_feedback.stop()

    def show_ultra_info(self):
        self.ui.ultra_info.show()

    def show_ultra(self):
        if util.ultra_container:
            self.ui.ultra_info.hide()
            util.removeFromParent2(util.ultra_container)
            util.addWidget2(self.ui.ultra_widget, util.ultra_container)
            self.scrcpy_timer.stop()

    def _init_ui(self):
        return
        self.images_path = os.path.join(util.get_project_base_path(), "Resources", "Images").replace("\\", "/")
        self.treat_images_path = os.path.join(util.get_project_base_path(), "Resources", "treat_images").replace("\\",
                                                                                                                 "/")
        self.current_position = 0
        self.params = [0, 0, 0, 0, 0]
        self.images = defaultdict(lambda: [None] * 2)
        self.ui.VeinTreat_overlay.setStyleSheet("background-color: rgba(0, 0, 0, 80);")
        self.show_treat()
        self.ui.stop_treat.setStyleSheet(util.button2_style.format("32"))

        self.ui.frame0.setStyleSheet('''
            border: 2px solid #000000;  
        ''')
        self.ui.frame1.setStyleSheet('''
            border: 2px solid #000000;   
        ''')

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

        self.ui.vein_view.setStyleSheet(util.button2_style.format("32"))
        self.ui.vein_view.clicked.connect(self._changeView)
        self.vein_view_timer = qt.QTimer()
        self.vein_view_timer.timeout.connect(self._check_change_view_done)

        self.ui.btn_sub_pressure.setStyleSheet(util.button2_style.format("32"))
        self.ui.btn_sub_pressure.toggled.connect(self.on_sub_pressure)
        self.ui.btn_add_pressure.setStyleSheet(util.button2_style.format("32"))
        self.ui.btn_add_pressure.toggled.connect(self.on_add_pressure)

        self.ui.widget_robot_overlay.setStyleSheet("background-color: rgba(0, 0, 0, 80);")
        self.show_robot()

        self.ui.btn_compare.setStyleSheet(util.button2_style.format("32"))
        self.ui.btn_compare.clicked.connect(self.show_compare_dialog)

        # self.ui.efficacy_test.setStyleSheet(util.button2_style.format("32"))

        self.ui.text_setting.setReadOnly(True)
        self.ui.text_feedback.setReadOnly(True)

        self.settings_columns = ['功率', '突发宽度', '突发周期', '治疗时间', '冷却时间']
        self.ui.parameter_config.setStyleSheet(util.button2_style.format("32"))
        self.ui.parameter_config.clicked.connect(self._on_param_config)
        self.on_settings()

        self.feedback_columns = [('电压', 'V'), ('电流', 'A'), ('功率', 'W')]
        self.UG_params = [0, 0, 0]
        self.timer_feedback = qt.QTimer()
        self.timer_feedback.timeout.connect(self.on_feedback)

        self.ui.widget_3.setStyleSheet('''
            border-radius: 0px 0px 0px 0px;
            border: 1px solid #3D4144;
        ''')
        self.ui.widget_4.setStyleSheet('''
            border-radius: 0px 0px 0px 0px;
            border: 1px solid #3D4144;
        ''')
        self.ui.text_setting.setStyleSheet('''
            border: none; 
        ''')
        self.ui.text_feedback.setStyleSheet('''
            border: none;
        ''')

        self.update_sport_status(0)
        self.update_debug_info('1')

        self.btn_treat = ProgressButton()
        util.addWidget2(self.ui.widget_treatment, self.btn_treat)
        self.btn_treat.setEnabled(False)
        self.ui.safe_lock.setIcon(qt.QIcon(self.resourcePath('Icons/lock.png')))
        self.ui.safe_lock.setStyleSheet('''
            background: transparent;
            border: none;
        ''')
        self.ui.safe_lock.setIconSize(qt.QSize(48, 48))
        self.ui.safe_lock.toggled.connect(self._on_unlock_treat)
        self.ui.stop_treat.clicked.connect(lambda: self.btn_treat.stop_treat())

        self.ui.btn_screen.setStyleSheet(util.button2_style.format("32"))
        self.ui.btn_screen.clicked.connect(self.on_test_save_picture)

        self.scrcpy_timer = qt.QTimer()
        self.scrcpy_timer.timeout.connect(self.show_ultra)

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
            self.cursor.execute('''INSERT INTO PointInfo (SegmentID,PointName)
            VALUES (?, ?)''',
                                (self.segment_id, 'P' + str(self.current_position)))
            self.point_id = str(self.cursor.lastrowid)
            util.db_conn.commit()
            with util.backup_db_conn:
                util.db_conn.backup(util.backup_db_conn)
            self.pos_to_id[self.current_position] = [self.point_id, 0, 0]
            return


        self.point_id = self.pos_to_id[self.current_position][0]

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

    def show_compare_dialog(self):
        if self.current_position in self.images:
            dialog = CompareDialog(self.images[self.current_position][0],
                                   self.images[self.current_position][1])
        else:
            dialog = CompareDialog()
        dialog.exec_()

    def on_test_save_picture(self):
        timestamp = datetime.now().strftime("%Y_%m_%d-%H_%M_%S")

        file_path = '/'.join([self.treat_images_path, f"P{self.current_position}-{timestamp}.png"])
        result = subprocess.run(util.screenshot_command, stdout=subprocess.PIPE)
        with open(file_path, 'wb') as f:
            f.write(result.stdout)

        util.getModuleWidget("VeinConfigTop").set_status_info('疗效监测截图成功', 'y')

    def save_normal_picture(self):
        timestamp = datetime.now().strftime("%Y_%m_%d-%H_%M_%S")

        file_path = '/'.join([self.images_path, f"P{self.current_position}-{timestamp}.png"])
        result = subprocess.run(util.screenshot_command, stdout=subprocess.PIPE)
        with open(file_path, 'wb') as f:
            f.write(result.stdout)
        self.cursor.execute('''INSERT INTO SegmentImagesInfo (PointID, ImagePath,TreatPower,Width,Circle,CoolTime,TotalTime,TotalEnergy,CreateTime,ModifyTime)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', (
            self.point_id, file_path, self.treat_power, self.width, self.circle, self.cool_time, self.total_time,
            self.treat_power * self.total_time, timestamp, timestamp))
        util.db_conn.commit()
        with util.backup_db_conn:
            util.db_conn.backup(util.backup_db_conn)

        util.getModuleWidget("VeinConfigTop").set_status_info("截图成功", 'y')

    def save_treatment_picture(self, flag):
        return
        period = 'after'
        info = '治疗后截图'
        timestamp = datetime.now().strftime("%Y_%m_%d-%H_%M_%S")
        if not flag:
            period = 'before'
            info = '治疗前截图'
            self.create_time = timestamp

        file_path = '/'.join([self.images_path, f"P{self.current_position}-{timestamp}-{period}.png"])
        result = subprocess.run(util.screenshot_command, stdout=subprocess.PIPE)
        with open(file_path, 'wb') as f:
            f.write(result.stdout)

        self.images[self.current_position][flag] = file_path

        if flag:
            image_path = ';'.join(self.images[self.current_position])
            self.cursor.execute('''INSERT INTO SegmentImagesInfo (PointID, ImagePath,TreatPower,Width,Circle,CoolTime,TotalTime,TotalEnergy,flag,CreateTime,ModifyTime)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', (
                self.point_id, image_path, self.treat_power, self.width, self.circle, self.cool_time, self.total_time,
                self.treat_power * self.total_time, 1, self.create_time, timestamp))
            util.db_conn.commit()
            with util.backup_db_conn:
                util.db_conn.backup(util.backup_db_conn)

        util.getModuleWidget("VeinConfigTop").set_status_info(info, 'y')

    def on_next_pos(self):
        self.current_position += 1

    def on_pre_pos(self):
        self.current_position -= 1
       

    def on_left_pos(self):
        util.getModuleWidget("VeinConfigTop").set_status_info(f'左位移{self.ui.robot_step.currentText[0]}mm', 'g')
        self.vein_view_timer.start(100)
        pass

    def on_right_pos(self):
        util.getModuleWidget("VeinConfigTop").set_status_info(f'右位移{self.ui.robot_step.currentText[0]}mm', 'g')
        self.vein_view_timer.start(100)
        pass

    def update_point_status(self):
        self.cursor.execute('''UPDATE PointInfo SET Count = Count + 1,IsTreated = ? WHERE ID = ?''', (1, self.point_id))
        # print(self.pos_to_id)
        self.pos_to_id[self.current_position][1] += 1

    def disabled_pressure_btn(self, flag):
        self.ui.btn_add_pressure.setEnabled(flag)
        self.ui.btn_sub_pressure.setEnabled(flag)
        self.ui.safe_lock.setEnabled(flag)

    def on_add_pressure(self, checked):
        if not checked:
            util.getModuleWidget("JWaterControl").open_valve_power()
            util.getModuleWidget("JWaterControl").sub_pressure(0, 4)
            util.getModuleWidget("VeinConfigTop").set_status_info("内循环中", 'g')
            self.ui.btn_sub_pressure.setEnabled(True)
            util.getModuleWidget("VeinConfigTop").clear_status_info()
            return
        self.ui.btn_sub_pressure.setEnabled(False)
        util.getModuleWidget("VeinConfigTop").set_status_info('水囊加水中', 'g')
        util.getModuleWidget("JWaterControl").add_pressure()

    def on_sub_pressure(self, checked):
        if not checked:
            util.getModuleWidget("JWaterControl").open_valve_power()
            util.getModuleWidget("JWaterControl").sub_pressure(0, 4)
            util.getModuleWidget("VeinConfigTop").set_status_info("内循环中", 'g')
            self.ui.btn_add_pressure.setEnabled(True)
            util.getModuleWidget("VeinConfigTop").clear_status_info()
            return
        self.ui.btn_add_pressure.setEnabled(False)
        util.getModuleWidget("VeinConfigTop").set_status_info('水囊去水中', 'g')
        util.getModuleWidget("JWaterControl").close_valve_power()
        util.getModuleWidget("JWaterControl").sub_pressure()

    def update_sport_status(self, status):
        if status == 0:
            self.ui.sport_status.setStyleSheet('''
                background: #3CC181;
                border-radius: 16px;
            ''')
            self.ui.dis_info.setText("区间内")
        elif status == 1:
            self.ui.sport_status.setStyleSheet('''
                background: #E2B134;
                border-radius: 16px;
            ''')
            self.ui.dis_info.setText("超出区间")
        elif status == 2:
            self.ui.sport_status.setStyleSheet('''
                background: #FF513A;
                border-radius: 16px;
            ''')
            self.ui.dis_info.setText("超出量程")

    def update_debug_info(self, status):
        if status == '0':
            self.ui.debug_info.setText('TIc1 : 0')
        else:
            self.ui.debug_info.setText('TI1 ： 1')

    def _on_unlock_treat(self, checked):
        if checked:
            if self.ui.dis_info.text == "区间内":
                print("unlocked")
                self.ui.safe_lock.setIcon(qt.QIcon(self.resourcePath('Icons/unlock.png')))
                self.btn_treat.setEnabled(True)
            else:
                print("unlocked failed")
        else:
            self.ui.safe_lock.setIcon(qt.QIcon(self.resourcePath('Icons/lock.png')))
            self.btn_treat.setEnabled(False)

    def _on_param_config(self):
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

    def on_settings(self):
        detail_info = f'''
                    <span style="font-size: 28px;">设置</span>
                '''
        for (key, value) in zip(self.settings_columns, self.params):
            detail_info += f'''<p>{key}：{value}</p>'''
        self.ui.text_setting.setText(detail_info)

    def on_feedback(self):
        AC_voltage = util.parameter_config['AC_voltage']
        AC_current = util.parameter_config['AC_current']
        AC_power = round(AC_voltage * AC_current, 2)
        self.UG_params = [AC_voltage, AC_current, AC_power]
        detail_info = f'''
                    <span style="font-size: 28px;">反馈</span>
                '''
        for (key, value) in zip(self.feedback_columns, self.UG_params):
            detail_info += f'''<p>{key[0]}：{value}{key[1]}</p>'''
        self.ui.text_feedback.setText(detail_info)

    def on_stop(self):
        util.getModuleWidget("JWaterControl").on_stop()

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

    def _changeView(self):
        # print("change view called [py]")
        try:
            util.getModuleWidget("VeinConfigTop").set_status_info('治疗头位姿调整中', 'g')
            util.getModuleWidget("RequestStatus").send_cmd(f"UR, ChangeView, 1")
            self.vein_view_timer.start(500)
            # print("ChangeView returned, proceeding...")
        except RuntimeError as e:
            print(f"Error: {e}")

    def _check_change_view_done(self):
        if util.getModuleWidget("RequestStatus").send_synchronize_cmd(f"UR, IsRobotSteady") == "True":
            self.vein_view_timer.stop()
            util.getModuleWidget("VeinConfigTop").clear_status_info()
        return

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

    def on_start_treat(self):
        self.btn_treat.setEnabled(True)

    def on_start_compare(self):
        self.ui.safe_lock.setChecked(False)
        self.ui.btn_compare.setEnabled(True)

    def overlay_robot(self):
        self.ui.widget_robot_overlay.show()

    def show_robot(self):
        self.ui.widget_robot_overlay.hide()

    def overlay_treat(self):
        return
        self.ui.VeinTreat_overlay.show()

    def show_treat(self):
        return
        self.ui.VeinTreat_overlay.hide()
