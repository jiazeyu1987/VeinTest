import qt, slicer
from slicer.ScriptedLoadableModule import *
from slicer.util import VTKObservationMixin
import slicer.util as util
import os
import sqlite3
from datetime import datetime


class WidgetEventFilter(qt.QObject):
    completed = qt.Signal()
    print("WidgetEventFilter initialized")

    def eventFilter(self, source, event):
        if event.type() == qt.QEvent.Close and util.global_data_map['is_closed_water']:
            print("is closed water event")
            qt.QTimer.singleShot(0, self.completed.emit)
            return True
        return False


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

        self.water_bladder = util.global_data_map['WaterBladder']
        self.event_filter = WidgetEventFilter()
        self.event_filter.completed.connect(self.complete_treat)
        self.water_bladder.uiWidget.installEventFilter(self.event_filter)

        # 定义固定的样式
        self.base_style = """
              QPushButton {{
              border: 2px solid black; /* 设置边框样式、宽度和颜色 */
              border-radius: 30px;      /* 设置圆角半径为按钮宽度或高度的一半 */
              background-color: {color};
          }}
      """

        # 初始化状态
        self.blinking = False
        self.blink_state = False
        self.blink_color = None

        # 创建一个定时器用于控制闪烁
        self.timer = qt.QTimer()
        self.timer.timeout.connect(self.toggle_blink)
        # 更新初始状态
        self.update_indicator(0)
        self.ui.btn_water_bladder.setStyleSheet(self.base_style.format(color="gray"))
        self.ui.btn_water_bladder.clicked.connect(self.show_water_bladder)
        self.ui.btn_complete_treat.clicked.connect(self.complete_treat)
        self.ui.pushButton.clicked.connect(self.save)

        database_path = os.path.join(util.mainWindow().GetProjectBasePath(), "Resources", "Database", "client",
                                     "ctkDICOM.sql")
        # 连接到数据库
        self.conn = sqlite3.connect(database_path)
        # 创建一个游标对象，用于执行 SQL 语句
        self.cursor = self.conn.cursor()

        self.ui.label_hospital.text = "XXXX Hospital"
        self.ui.label_hospital.setStyleSheet("font-size: 24px;")

        self.ui.label_name.setStyleSheet("font-size: 24px;")
        self.ui.label_info.setStyleSheet("font-size: 24px;")
        self.ui.label_datetime.setStyleSheet("font-size: 24px;")
        self.time_timer = qt.QTimer()
        self.time_timer.timeout.connect(self.show_time)
        self.time_timer.start(1000)

        self.clear_timer = qt.QTimer()
        self.clear_timer.setSingleShot(True)  # 设置为单次触发
        self.clear_timer.timeout.connect(self.clear_text)
        self.show_time()

    def enter(self):
        self.ui.label_name.text = util.global_data_map["patientName"]

    def save(self):
        util.getModuleWidget("JMeasure").on_save()

    def show_water_bladder(self, flag=False) -> None:
        util.global_data_map['is_closed_water'] = flag
        print("show water bladder treatment")
        self.water_bladder.show(1)

    def complete_treat(self) -> None:
        print("complete treatment")
        print(util.global_data_map['is_closed_water'])
        curr_page = util.global_data_map['page']
        if curr_page == 5 and not util.global_data_map['has_treat']:
            util.send_event_str(util.SetPage, 4)
            return
        self.ui.btn_complete_treat.setChecked(True)
        self.ui.btn_complete_treat.setStyleSheet("background-color: darkgray;")
        # 显示确认对话框
        reply = qt.QMessageBox()
        reply.setStandardButtons(qt.QMessageBox.Ok | qt.QMessageBox.Cancel)
        reply.setWindowTitle("确认")
        reply.resize(400, 400)
        if curr_page == 4:
            reply.setText("请确认治疗已全部完成且水囊已自动排水")
            # 创建按钮
            ok_button = reply.button(qt.QMessageBox.Ok)
            ok_button.setText("确认")
            handle_water = reply.button(qt.QMessageBox.Cancel)
            handle_water.setText("水处理")
            handle_water.clicked.connect(lambda: self.show_water_bladder(True))
            if not util.global_data_map['is_closed_water']:
                ok_button.setEnabled(False)
            result = reply.exec_()
            if result == qt.QMessageBox.Ok:
                self.ui.btn_complete_treat.setChecked(False)
                self.ui.btn_complete_treat.setStyleSheet("background-color: #1765AD;")
                # 患者管理界面
                vein_id = util.global_data_map["patientID"]
                self.cursor.execute(f'UPDATE PatientInfo SET IsTreated = ? WHERE ID = ?', (1, vein_id,))
                self.conn.commit()
                util.send_event_str(util.SetPage, 3)

        elif curr_page == 5:
            reply.setText("请确认当前segment已治疗完成")
            reply.setStandardButtons(qt.QMessageBox.Ok | qt.QMessageBox.Cancel)
            reply.button(qt.QMessageBox.Ok).setText("确认")
            reply.button(qt.QMessageBox.Cancel).setText("返回")

            result = reply.exec_()
            if result == qt.QMessageBox.Ok:
                self.ui.btn_complete_treat.setChecked(False)
                self.ui.btn_complete_treat.setStyleSheet("background-color: #1765AD;")
                # 治疗配置界面
                segment_id = util.global_data_map["segmentID"]
                self.cursor.execute("UPDATE SegmentInfo SET IsTreated = ? WHERE ID=?", (1, segment_id))
                self.conn.commit()
                util.send_event_str(util.SetPage, 4)

        self.ui.btn_complete_treat.setChecked(False)
        self.ui.btn_complete_treat.setStyleSheet("background-color: #1765AD;")

    def update_indicator(self, state) -> None:
        self.stop_blinking()
        if state == 0:
            self.ui.btn_water_bladder.setStyleSheet(self.base_style.format(color="green"))
        elif state == 1:
            self.start_blinking("yellow")
        elif state == 2:
            self.start_blinking("red")
        elif state == 3:
            self.ui.btn_water_bladder.setStyleSheet(self.base_style.format(color="blue"))

    def start_blinking(self, color):
        self.blinking = True
        self.blink_color = color
        self.timer.start(300)  # 每500毫秒切换一次

    def stop_blinking(self):
        self.blinking = False
        self.timer.stop()
        self.ui.btn_water_bladder.setStyleSheet(self.base_style.format(color="gray"))

    def toggle_blink(self):
        if self.blinking:
            if self.blink_state:
                self.ui.btn_water_bladder.setStyleSheet(self.base_style.format(color=self.blink_color))
            else:
                self.ui.btn_water_bladder.setStyleSheet(self.base_style.format(color="gray"))
            self.blink_state = not self.blink_state

    def show_time(self):
        self.ui.label_datetime.text = datetime.now().strftime("%Y/%m/%d %H:%M:%S")

    def set_status_info(self, info):
        self.ui.label_info.text = info
        self.clear_timer.start(3000)

    def clear_text(self):
        self.ui.label_info.text = ""
