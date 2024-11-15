import os

import slicer
from slicer import util
from apscheduler.schedulers.qt import QtScheduler
from datetime import datetime, timedelta
import qt
import uuid


class Task:
    def __init__(self, name, actions=None, condition_function=None, max_duration_s=None):
        self.name = name
        self.actions = actions or []
        self.condition_function = condition_function
        self.is_active = True
        self.start_time = None
        self.max_duration = max_duration_s
        self.stop_flag = False

    def start(self, scheduler, job_id):
        self.start_time = datetime.now()
        self.is_active = True
        self.stop_flag = False
        if self.max_duration:
            scheduler.add_job(self.complete, 'date', run_date=self.start_time + timedelta(seconds=self.max_duration),
                              id=job_id)

    def complete(self):
        self.is_active = False

    def check_condition(self):
        if self.condition_function and self.condition_function():
            return True
        return False

    def execute(self):
        if self.stop_flag or not self.is_active:
            return
        for action_info in self.actions:
            action, condition, flag, params = action_info
            if (condition is None or condition()) and not flag:
                if params:
                    action(*params)
                else:
                    action()
                action_info[2] = True
                break

        if self.check_condition():
            self.complete()

    def reset(self):
        self.is_active = True
        self.stop_flag = True
        self.start_time = None
        for action_info in self.actions:
            action_info[2] = False


class Command:
    def __init__(self, name, scheduler):
        self.name = name
        self.tasks = []
        self.current_task_index = 0
        self.scheduler = scheduler
        self.is_running = False

    def add_task(self, task):
        self.tasks.append(task)

    def execute(self):
        if self.current_task_index < len(self.tasks):
            current_task = self.tasks[self.current_task_index]
            current_task.execute()
            if not current_task.is_active:
                self.current_task_index += 1
                if self.current_task_index < len(self.tasks):
                    unique_task_id = f"{self.name}_task_{self.current_task_index}_{uuid.uuid4()}"
                    self.tasks[self.current_task_index].start(self.scheduler, unique_task_id)
                else:
                    self.is_running = False
                    self.scheduler.remove_job(self.name)

    def start(self):
        if not self.is_running:
            self.is_running = True
            self.current_task_index = 0
            if self.tasks:
                unique_task_id = f"{self.name}_task_{self.current_task_index}_{uuid.uuid4()}"
                self.tasks[0].start(self.scheduler, unique_task_id)
                self.scheduler.add_job(self.execute, 'interval', seconds=0.1, id=self.name)

    def reset(self):
        if self.is_running:
            self.is_running = False
            self.scheduler.remove_job(self.name)
        for task in self.tasks:
            task.reset()
        self.current_task_index = 0


class WaterBladder:
    def __init__(self):
        print("water blader initialized")
        # 获取当前文件的绝对路径
        current_file_path = os.path.abspath(__file__)
        # 获取当前文件所在目录的上一层目录
        parent_directory = os.path.dirname(os.path.dirname(current_file_path))
        # 其他插件也会用到这个弹窗，所以不能通过parent加载ui文件
        self.uiWidget = slicer.util.loadUI(parent_directory + '/Resources/UI/WaterBladder.ui')
        self.ui = util.childWidgetVariables(self.uiWidget)

        self._init_ui()

    def _init_ui(self):
        self.uiWidget.setWindowTitle('水囊设置')
        self.ui.btn_auto_water.clicked.connect(self.auto_water)
        self.ui.btn_auto_release.clicked.connect(self.auto_release)
        self.ui.btn_stop_water.clicked.connect(self.stop_water)
        self.ui.btn_fill_water.toggled.connect(self._add_pressure)
        self.ui.btn_release_water.toggled.connect(self._sub_pressure)
        self.ui.label_water_status.setStyleSheet("color: red;")
        self.ui.btn_fill_water.setStyleSheet('''
            QPushButton:checked {
                background-color: lightgreen;
            }
        ''')
        self.ui.btn_release_water.setStyleSheet('''
            QPushButton:checked {
                background-color: lightgreen;
            }
        ''')

        self.update_data()

        # 创建调度器
        self.scheduler = QtScheduler()
        self.scheduler.start()

        # 创建命令
        self.command1 = self.create_command('fill_water', [
            ('step1', [[self.before_one_step, None, False, None]], self.check_press_status_water, None),
            ('step2_1', [[self.before_two_step_1, None, False, None]], None, 5),
            ('step2_2', [[self.before_two_step_2, None, False, ("水囊上水中",)]], None, 40),
            ('step3', [[self.before_three_step, None, False, None]], None, 30),
            ('step4', [[self.before_four_step, None, False, None]], None, 40),
            ('step5_1', [[self.before_two_step_2, None, False, ("除氧中",)]], self.check_oxygen, None),
            ('step5_2', [[self.before_two_step_2, None, False, ("除氧中",)]], None, 10),
            ('step6',
             [[self._add_pressure, self.check_press_status_low, False, None],
              [self._sub_pressure, self.check_press_status_high, False, None]],
             self.check_press_status_mid, None),
            ('step7', [[self.before_five_step, None, False, None]], self.check_water_bladder_temp_low, 30)
        ])
        self.command2 = self.create_command('release_water', [
            ('step1', [[self.after_one_step, None, False, None]], None, 30),
            ('step2', [[self.after_two_step, None, False, None]], None, 30),
            ('step3', [[self.after_three_step, None, False, None]], None, 30)
        ])

        self.water_bladder_timer = qt.QTimer()
        self.water_bladder_timer.timeout.connect(self.check_water_bladder_temp_high)

        self.update_data_timer = qt.QTimer()
        self.update_data_timer.timeout.connect(self.update_data)
        self.update_data_timer.start(100)

    def create_command(self, cmd_name, task_specs):
        command = Command(cmd_name, self.scheduler)
        for name, actions, condition, duration in task_specs:
            command.add_task(Task(name, actions, condition, duration))
        return command

    def execute_command1(self):
        self.command1.reset()
        self.command1.start()

    def execute_command2(self):
        self.command2.reset()
        self.command2.start()

    def auto_water(self) -> None:
        self.ui.btn_auto_water.text = "正在上水"
        self.ui.btn_auto_water.setEnabled(False)
        self.ui.btn_auto_release.setEnabled(False)
        self.ui.btn_stop_water.setChecked(False)
        self.ui.btn_stop_water.setEnabled(True)
        self.execute_command1()

    def auto_release(self) -> None:
        self.ui.btn_auto_release.text = "正在排水"
        self.ui.btn_auto_water.setEnabled(False)
        self.ui.btn_auto_release.setEnabled(False)
        self.ui.btn_stop_water.setChecked(False)
        self.ui.btn_stop_water.setEnabled(True)
        self.execute_command2()

    def before_one_step(self):
        self.ui.label_water_status.text = "水囊正在鼓起"
        util.getModuleWidget("JWaterControl").add_pressure(2)

    def before_two_step_1(self):
        self.ui.label_water_status.text = "真空泵开启中"
        util.getModuleWidget("JWaterControl").on_set_cacuum_speed_inner(100)

    def before_two_step_2(self, text):
        self.ui.label_water_status.text = text
        util.getModuleWidget("JWaterControl").on_fill_water(0)

    def before_three_step(self):
        self.ui.label_water_status.text = "制冷单元上水中"
        util.getModuleWidget("JWaterControl").open_valve_power()
        util.getModuleWidget("JWaterControl").sub_pressure(0, 0)

    def before_four_step(self):
        self.ui.label_water_status.text = "水囊空气排出中"
        util.getModuleWidget("JWaterControl").close_valve_power()
        util.getModuleWidget("JWaterControl").on_fill_water(0)

    def before_five_step(self):
        self.ui.label_water_status.text = "内循环中"
        util.getModuleWidget("JWaterControl").open_valve_power()
        util.getModuleWidget("JWaterControl").sub_pressure(0, 4)
        util.getModuleWidget("JWaterControl").on_set_compressor_inner(3000)

    def after_one_step(self):
        self.ui.label_water_status.text = "结束治疗"
        util.getModuleWidget("JWaterControl").close_valve_power()
        util.getModuleWidget("JWaterControl").on_set_compressor_inner(0)
        util.getModuleWidget("JWaterControl").on_set_cacuum_speed_inner(0)
        util.getModuleWidget("JWaterControl").on_drain_water(0)

    def after_two_step(self):
        self.ui.label_water_status.text = "排空制冷单元的水"
        util.getModuleWidget("JWaterControl").open_valve_power()
        util.getModuleWidget("JWaterControl").sub_pressure(17, 0)

    def after_three_step(self):
        self.ui.label_water_status.text = "排空水囊的水"
        util.getModuleWidget("JWaterControl").close_valve_power()
        util.getModuleWidget("JWaterControl").on_drain_water(0)

    def _add_pressure(self, checked):
        if not checked:
            self.ui.btn_release_water.setEnabled(True)
            self.before_five_step()
            return
        self.ui.btn_release_water.setEnabled(False)
        self.ui.btn_auto_water.setEnabled(False)
        self.ui.btn_stop_water.setChecked(False)
        self.ui.btn_stop_water.setEnabled(True)
        self.ui.label_water_status.text = "水囊加压中"
        water_pump_direction = 0
        water_pump_speed = 5
        water_pump_status = 90
        util.getModuleWidget("RequestStatus").send_cmd(
            f"WaterControl, Send, 0, SetWaterPump, {water_pump_direction}, {water_pump_speed}, {water_pump_status}")

    def _sub_pressure(self, checked):
        if not checked:
            self.ui.btn_fill_water.setEnabled(True)
            self.before_five_step()
            return
        self.ui.btn_fill_water.setEnabled(False)
        self.ui.btn_auto_water.setEnabled(False)
        self.ui.btn_stop_water.setChecked(False)
        self.ui.btn_stop_water.setEnabled(True)
        util.getModuleWidget("JWaterControl").close_valve_power()
        self.ui.label_water_status.text = "水囊减压中"
        water_pump_direction = 0
        water_pump_speed = 5
        water_pump_status = 165
        util.getModuleWidget("RequestStatus").send_cmd(
            f"WaterControl, Send, 0, SetWaterPump, {water_pump_direction}, {water_pump_speed}, {water_pump_status}")

    def check_oxygen(self):
        print("check oxygen")
        return True

    def check_press_status_high(self):
        if util.WaterBladderConfig['press_value'] > 40:
            return True
        return False

    def check_press_status_mid(self):
        if 30 <= util.WaterBladderConfig['press_value'] <= 40:
            util.getModuleWidget("VeinConfigTop").update_indicator(1)
            return True
        return False

    def check_press_status_water(self):
        if 25 <= util.WaterBladderConfig['press_value'] <= 30:
            return True
        return False

    def check_press_status_low(self):
        if util.WaterBladderConfig['press_value'] < 35:
            return True
        return False

    def check_water_bladder_temp_low(self):
        if util.WaterBladderConfig['water_bladder_temp'] <= 11:
            self.ui.label_water_status.text = "内循环中"
            util.getModuleWidget("JWaterControl").on_set_compressor_inner(0)

            util.getModuleWidget("VeinConfigTop").update_indicator(0)
            self.water_bladder_timer.start(1000)
            return True
        return False

    def check_water_bladder_temp_high(self):
        if util.WaterBladderConfig['water_bladder_temp'] > 11:
            util.getModuleWidget("JWaterControl").on_set_compressor_inner(3000)
            self.water_bladder_timer.stop()
            self.decrease_temp()

    def decrease_temp(self):
        if util.WaterBladderConfig['water_bladder_temp'] > 11:
            qt.QTimer.singleShot(500, self.decrease_temp)
        else:
            self.water_bladder_timer.start(1000)
            util.getModuleWidget("JWaterControl").on_set_compressor_inner(0)

    def update_data(self):
        self.temp = util.WaterBladderConfig['water_bladder_temp']
        self.pressure = util.WaterBladderConfig['press_value']
        self.oxygen = util.WaterBladderConfig['oxygen_concentration']
        self.ui.label_info.text = f"水温：{self.temp:.2f}" + "\n" + f"水压：{self.pressure:.2f}kpa" + "\n" + f"氧浓度：{self.oxygen:.2f}"

    def stop_water(self) -> None:
        self.command1.reset()
        self.command2.reset()
        util.getModuleWidget("JWaterControl").on_set_compressor_inner(0)
        util.getModuleWidget("JWaterControl").on_set_cacuum_speed_inner(0)
        util.getModuleWidget("JWaterControl").on_stop()
        self.ui.btn_stop_water.setChecked(True)
        self.ui.btn_stop_water.setEnabled(False)
        self.ui.btn_auto_water.text = "自动上水"
        self.ui.btn_auto_release.text = "自动排水"
        self.ui.btn_auto_water.setEnabled(True)
        self.ui.btn_auto_release.setEnabled(True)
        self.ui.btn_fill_water.setEnabled(True)
        self.ui.btn_release_water.setEnabled(True)
        self.ui.label_water_status.text = ""

    def show(self, index=0):
        print("water bladder show")
        self.ui.tabWidget.setCurrentIndex(index)
        self.uiWidget.show()
        self.uiWidget.raise_()
        self.uiWidget.activateWindow()

    def hide(self):
        self.uiWidget.hide()
