import time

from transitions import Machine
import qt
import slicer
from slicer import util
import os


class WaterBladderWaterStateMachine:
    states = [
        'idle',
        'one_step',
        'two_step_1',
        'two_step_2',
        'three_step',
        'four_step',
        'five_step_1',
        'five_step_2',
        'six_step',
        'seven_step',
    ]

    def __init__(self, parent):
        self.high_pressure = None
        self.low_pressure = None
        self.oxy_pressure = None
        self.parent = parent
        self.machine = Machine(model=self, states=WaterBladderWaterStateMachine.states, initial='idle')
        transitions = [
            {'trigger': 'start', 'source': 'idle', 'dest': 'one_step', 'after': 'one_step'},
            {'trigger': 'finish_one_step', 'source': 'one_step', 'dest': 'two_step_1', 'after': 'two_step_1'},
            {'trigger': 'finish_two_step_1', 'source': 'two_step_1', 'dest': 'two_step_2', 'after': 'two_step_2'},
            {'trigger': 'finish_two_step_2', 'source': 'two_step_2', 'dest': 'three_step', 'after': 'three_step'},
            {'trigger': 'finish_three_step', 'source': 'three_step', 'dest': 'four_step', 'after': 'four_step'},
            {'trigger': 'finish_four_step', 'source': 'four_step', 'dest': 'five_step_1', 'after': 'five_step_1'},
            {'trigger': 'finish_five_step_1', 'source': 'five_step_1', 'dest': 'five_step_2', 'after': 'five_step_2'},
            {'trigger': 'finish_five_step_2', 'source': 'five_step_2', 'dest': 'six_step', 'after': 'six_step'},
            {'trigger': 'finish_six_step', 'source': 'six_step', 'dest': 'seven_step', 'after': 'seven_step'},
            {'trigger': 'stop', 'source': self.states, 'dest': 'idle', 'after': 'on_stop'},
        ]
        self.machine.add_transitions(transitions)

        self.timer = qt.QTimer()
        self.timer.timeout.connect(self.check_conditions)

        self.max_durations = {
            'one_step': float('inf'),
            'two_step_1': 5,
            'two_step_2': 40,
            'three_step': 30,
            'four_step': 40,
            'five_step_1': float('inf'),
            'five_step_2': 10,
            'six_step': float('inf'),
            'seven_step': float('inf'),
        }

        self.start_time = None
        self.max_duration = 0

        self.state_actions = {
            'one_step': (self.initial_press_set, self.finish_one_step),
            'two_step_1': (lambda: False, self.finish_two_step_1),
            'two_step_2': (lambda: False, self.finish_two_step_2),
            'three_step': (lambda: False, self.finish_three_step),
            'four_step': (lambda: False, self.finish_four_step),
            'five_step_1': (self.check_oxygen, self.finish_five_step_1),
            'five_step_2': (lambda: False, self.finish_five_step_2),
            'six_step': (self.check_pressure, self.finish_six_step),
            'seven_step': (None, None),
        }

    def on_start(self, status, duration):
        self.parent.update_status(status)
        self.start_time = qt.QTime.currentTime()
        self.max_duration = duration
        if not self.timer.isActive():
            self.timer.start(100)

    def one_step(self):
        util.getModuleWidget("JWaterControl").add_pressure(0)
        self.on_start("水囊正在鼓起", self.max_durations['one_step'])

    def two_step_1(self):
        util.getModuleWidget("JWaterControl").on_set_cacuum_speed_inner(100)
        self.on_start("真空泵开启中", self.max_durations['two_step_1'])

    def two_step_2(self):
        util.getModuleWidget("JWaterControl").on_fill_water(0)
        self.on_start("水囊上水中", self.max_durations['two_step_2'])

    def three_step(self):
        util.getModuleWidget("JWaterControl").open_valve_power()
        util.getModuleWidget("JWaterControl").sub_pressure(0, 0)
        self.on_start("制冷单元上水中", self.max_durations['three_step'])

    def four_step(self):
        util.getModuleWidget("JWaterControl").close_valve_power()
        util.getModuleWidget("JWaterControl").on_fill_water(0)
        self.on_start("水囊空气排出中", self.max_durations['four_step'])

    def five_step_1(self):
        util.getModuleWidget("JWaterControl").on_fill_water(0)
        self.on_start("除氧中", self.max_durations['five_step_1'])

    def five_step_2(self):
        util.getModuleWidget("JWaterControl").on_fill_water(0)
        self.on_start("除氧中", self.max_durations['five_step_2'])

    def six_step(self):
        print("i am six steps")
        if util.WaterBladderConfig['press_value'] > 8:
            util.getModuleWidget("JWaterControl").sub_pressure(0, 0)
            self.high_pressure = True
            self.low_pressure = False
        elif util.WaterBladderConfig['press_value'] < 2:
            util.getModuleWidget("JWaterControl").add_pressure(0)
            self.low_pressure = True
            self.high_pressure = False
        self.on_start("水压调节中", self.max_durations['six_step'])

    def seven_step(self):
        util.getModuleWidget("JWaterControl").open_valve_power()
        util.getModuleWidget("JWaterControl").sub_pressure(0, 0)
        self.parent.start_water_temp_timer()
        self.on_start("内循环中", self.max_durations['seven_step'])

    def on_stop(self):
        print("Process stopped.")
        self.timer.stop()

    def check_conditions(self):
        current_time = qt.QTime.currentTime()
        elapsed_time = self.start_time.secsTo(current_time)

        check_condition, finish_action = self.state_actions.get(self.state, (lambda: False, lambda: None))
        if finish_action is None:
            self.timer.stop()
            return
        if check_condition() or elapsed_time >= self.max_duration:
            self.timer.stop()
            finish_action()

    def initial_press_set(self):
        return 7 <= util.WaterBladderConfig['press_value']

    def check_oxygen(self):
        if util.WaterBladderConfig['oxygen_concentration'] < 4:
            return True
        if self.check_oxygen_pressure():
            print(f"oxygen pressure {util.WaterBladderConfig['press_value']}")
            util.getModuleWidget("JWaterControl").on_fill_water(0)
        return False

    def check_oxygen_pressure(self):
        if util.WaterBladderConfig['press_value'] < 3:
            print(f"add pressure {util.WaterBladderConfig['press_value']}")
            if self.oxy_pressure:
                return False
            util.getModuleWidget("JWaterControl").add_pressure(0)
            return False
        if util.WaterBladderConfig['press_value'] > 8:
            print(f"exclude oxygen")
            self.oxy_pressure = None
            return True
        return False

    def check_pressure(self):
        if util.WaterBladderConfig['press_value'] > 8:
            if self.high_pressure:
                return False
            util.getModuleWidget("JWaterControl").sub_pressure(0, 0)
            self.high_pressure = True
            self.low_pressure = False
            return False
        elif util.WaterBladderConfig['press_value'] < 2:
            if self.low_pressure:
                return False
            util.getModuleWidget("JWaterControl").add_pressure(0)
            self.low_pressure = True
            self.high_pressure = False
            return False
        self.low_pressure = None
        self.high_pressure = None
        return True


class WaterBladderReleaseStateMachine:
    states = [
        'idle',
        'one_step',
        'two_step',
        'three_step',
    ]

    def __init__(self, parent):
        self.parent = parent
        self.machine = Machine(model=self, states=WaterBladderReleaseStateMachine.states, initial='idle')
        transitions = [
            {'trigger': 'start', 'source': 'idle', 'dest': 'one_step', 'after': 'one_step'},
            {'trigger': 'finish_one_step', 'source': 'one_step', 'dest': 'two_step', 'after': 'two_step'},
            {'trigger': 'finish_two_step', 'source': 'two_step', 'dest': 'three_step', 'after': 'three_step'},
            {'trigger': 'stop', 'source': self.states, 'dest': 'idle', 'after': 'on_stop'},
        ]
        self.machine.add_transitions(transitions)

        self.timer = qt.QTimer()
        self.timer.timeout.connect(self.check_conditions)

        self.max_durations = {
            'one_step': 30,
            'two_step': 30,
            'three_step': float('inf'),
        }

        self.start_time = None
        self.max_duration = 0

        self.state_actions = {
            'one_step': (lambda: False, self.finish_one_step),
            'two_step': (lambda: False, self.finish_two_step),
        }

    def on_start(self, status, duration):
        self.parent.update_status(status)
        self.start_time = qt.QTime.currentTime()
        self.max_duration = duration
        if not self.timer.isActive():
            self.timer.start(100)

    def one_step(self):
        util.getModuleWidget("JWaterControl").close_valve_power()
        util.getModuleWidget("JWaterControl").on_set_compressor_inner(0)
        util.getModuleWidget("JWaterControl").on_set_cacuum_speed_inner(0)
        util.getModuleWidget("JWaterControl").on_drain_water(0)
        self.on_start("结束治疗", self.max_durations['one_step'])

    def two_step(self):
        util.getModuleWidget("JWaterControl").open_valve_power()
        util.getModuleWidget("JWaterControl").sub_pressure(17, 0)
        self.on_start("排空制冷单元的水", self.max_durations['two_step'])

    def three_step(self):
        util.getModuleWidget("JWaterControl").close_valve_power()
        util.getModuleWidget("JWaterControl").on_drain_water(0)
        self.on_start("排空水囊的水", self.max_durations['three_step'])

    def on_stop(self):
        print("Process stopped.")
        self.timer.stop()

    def check_conditions(self):
        current_time = qt.QTime.currentTime()
        elapsed_time = self.start_time.secsTo(current_time)

        check_condition, finish_action = self.state_actions.get(self.state, (lambda: False, lambda: None))
        if finish_action is None:
            self.timer.stop()
            return
        if check_condition() or elapsed_time >= self.max_duration:
            self.timer.stop()
            finish_action()


class WaterBladder:
    def __init__(self):
        print("water blader initialized")
        # 获取当前文件的绝对路径
        current_file_path = os.path.abspath(__file__)
        # 获取当前文件所在目录的上一层目录
        parent_directory = os.path.dirname(os.path.dirname(current_file_path))
        # 其他插件也会用到这个弹窗，所以不能通过parent加载ui文件
        self.uiWidget = slicer.util.loadUI(parent_directory + '/Resources/UI/WaterBladder.ui')
        self.uiWidget.setWindowFlags(qt.Qt.FramelessWindowHint)
        self.ui = util.childWidgetVariables(self.uiWidget)

        self._init_ui()
        self.water_state_machine = WaterBladderWaterStateMachine(self)
        self.release_state_machine = WaterBladderReleaseStateMachine(self)

    def _init_ui(self):
        self.uiWidget.setWindowTitle('水囊设置')
        self.ui.btn_auto_water.clicked.connect(self.auto_water)
        self.ui.btn_auto_release.clicked.connect(self.auto_release)
        self.ui.btn_stop_water.clicked.connect(self.stop_water)
        self.ui.btn_fill_water.toggled.connect(self.fill_water)
        self.ui.btn_release_water.toggled.connect(self.release_water)
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
        self.update_data_timer = qt.QTimer()
        self.update_data_timer.timeout.connect(self.update_data)
        self.update_data_timer.start(500)

        self.check_temp_timer = qt.QTimer()
        self.check_temp_timer.timeout.connect(self.check_water_bladder_temp)
        self.compressor_close = True

        self.ui.btn_fill_water.setEnabled(False)
        self.ui.btn_release_water.setEnabled(False)

    def auto_water(self) -> None:
        self.ui.btn_auto_water.text = "正在上水"
        self.ui.btn_auto_water.setEnabled(False)
        self.ui.btn_auto_release.setEnabled(False)
        self.ui.btn_fill_water.setEnabled(False)
        self.ui.btn_release_water.setEnabled(False)
        self.ui.btn_stop_water.setChecked(False)
        self.ui.btn_stop_water.setEnabled(True)
        self.water_state_machine.start()

    def auto_release(self) -> None:
        self.ui.btn_auto_release.text = "正在排水"
        self.ui.btn_auto_water.setEnabled(False)
        self.ui.btn_auto_release.setEnabled(False)
        self.ui.btn_fill_water.setEnabled(False)
        self.ui.btn_release_water.setEnabled(False)
        self.ui.btn_stop_water.setChecked(False)
        self.ui.btn_stop_water.setEnabled(True)
        util.getModuleWidget("VeinTreat").disabled_pressure_btn(False)
        self.release_state_machine.start()
        if self.check_temp_timer.isActive():
            self.check_temp_timer.stop()

    def stop_water(self) -> None:
        util.getModuleWidget("JWaterControl").on_set_compressor_inner(0)
        util.getModuleWidget("JWaterControl").on_set_cacuum_speed_inner(0)
        util.getModuleWidget("JWaterControl").close_valve_power()
        util.getModuleWidget("JWaterControl").on_stop()
        util.getModuleWidget("VeinTreat").disabled_pressure_btn(False)
        self.ui.btn_stop_water.setChecked(True)
        self.ui.btn_stop_water.setEnabled(False)
        self.ui.btn_auto_water.text = "自动上水"
        self.ui.btn_auto_release.text = "自动排水"
        self.ui.btn_auto_water.setEnabled(True)
        self.ui.btn_auto_release.setEnabled(True)
        self.ui.btn_fill_water.setEnabled(True)
        self.ui.btn_fill_water.setChecked(False)
        self.ui.btn_release_water.setEnabled(True)
        self.ui.btn_release_water.setChecked(False)
        self.ui.label_water_status.text = ""
        self.water_state_machine.stop()
        self.release_state_machine.stop()
        if self.check_temp_timer.isActive():
            self.check_temp_timer.stop()

    def fill_water(self, checked):
        if not checked:
            self.ui.btn_release_water.setEnabled(True)
            util.getModuleWidget("JWaterControl").on_stop()
            return
        self.ui.btn_release_water.setEnabled(False)
        self.ui.btn_auto_water.setEnabled(False)
        self.ui.btn_auto_release.setEnabled(False)
        self.ui.btn_stop_water.setChecked(False)
        self.ui.btn_stop_water.setEnabled(True)
        self.ui.label_water_status.text = "水囊手动上水中"
        util.getModuleWidget("JWaterControl").on_fill_water(4)

    def release_water(self, checked):
        if not checked:
            self.ui.btn_fill_water.setEnabled(True)
            util.getModuleWidget("JWaterControl").on_stop()
            return
        self.ui.btn_fill_water.setEnabled(False)
        self.ui.btn_auto_water.setEnabled(False)
        self.ui.btn_auto_release.setEnabled(False)
        self.ui.btn_stop_water.setChecked(False)
        self.ui.btn_stop_water.setEnabled(True)
        self.ui.label_water_status.text = "水囊手动排水中"
        util.getModuleWidget("JWaterControl").on_drain_water(4)

    def update_status(self, status):
        self.ui.label_water_status.text = status

    def update_data(self):
        self.temp = util.WaterBladderConfig['water_bladder_temp']
        self.pressure = util.WaterBladderConfig['press_value']
        self.oxygen = util.WaterBladderConfig['oxygen_concentration']
        self.compressor_status = util.WaterBladderConfig['compressor_status']
        self.compressor_speed = util.WaterBladderConfig['compressor_speed']
        self.compressor_current = util.WaterBladderConfig['compressor_current']
        self.ui.label_info.setText(
            f"水温：{self.temp:.2f}\n水压：{self.pressure:.2f}kpa\n氧浓度：{self.oxygen:.2f}\n压缩机状态：{self.compressor_status}\n压缩机速度：{self.compressor_speed}\n压缩机电流：{self.compressor_current}")

    def start_water_temp_timer(self):
        util.getModuleWidget("VeinTreat").disabled_pressure_btn(True)
        util.global_data_map['water_is_completed'] = True
        if util.global_data_map['water_is_completed'] and util.global_data_map['init_position_is_clicked']:
            util.getModuleWidget("VeinTreat").disabled_about_treat_btn(True)
        if not self.check_temp_timer.isActive():
            self.check_temp_timer.start(500)

    def check_water_bladder_temp(self):
        # print(
        #     f"curent temperature {util.WaterBladderConfig['water_bladder_temp']} and compressor flag is {self.compressor_close}")
        if util.WaterBladderConfig['water_bladder_temp'] > 18 and self.compressor_close:
            util.getModuleWidget("JWaterControl").open_colding_fan()
            time.sleep(0.1)
            util.getModuleWidget("JWaterControl").on_set_compressor_inner(3000)
            self.compressor_close = False
        elif util.WaterBladderConfig['water_bladder_temp'] < 14 and not self.compressor_close:
            util.getModuleWidget("JWaterControl").on_set_compressor_inner(0)
            self.compressor_close = True

    def show(self, index=0):
        self.ui.tabWidget.setCurrentIndex(index)
        self.uiWidget.show()
        self.uiWidget.raise_()
        self.uiWidget.activateWindow()

    def hide(self):
        self.uiWidget.hide()
