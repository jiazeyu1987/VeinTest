import qt
import slicer.util as util


class ProgressButton(qt.QPushButton):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.delay_duration = 1
        self.cooldown_duration = 5
        self.healing_duration = 4
        self.total_duration = self.delay_duration + self.cooldown_duration + self.healing_duration
        self.delay_ratio = self.delay_duration / self.total_duration * 100
        self.cooldown_ratio = (self.delay_duration + self.cooldown_duration) / self.total_duration * 100
        self.progress_ratio = 100 / self.total_duration / 10

        self.progress = 0
        self.is_running = False
        self.is_treating = False
        self.timer = qt.QTimer(self)
        self.timer.timeout.connect(self.update_progress)

        self.setFixedSize(360, 64)
        self.clicked.connect(self.start_progress)
        self.setText('治疗')

    def set_duration(self, cooldown_duration, healing_duration):
        self.cooldown_duration = float(cooldown_duration)
        self.healing_duration = float(healing_duration)
        self.total_duration = self.delay_duration + self.cooldown_duration + self.healing_duration
        self.delay_ratio = self.delay_duration / self.total_duration * 100
        self.cooldown_ratio = (self.delay_duration + self.cooldown_duration) / self.total_duration * 100
        self.progress_ratio = 100 / self.total_duration / 10

    def start_progress(self):
        if not self.is_running:
            util.getModuleWidget("VeinTreat").save_treatment_picture(0)
            util.getModuleWidget("VeinTreat").overlay_treat()
            util.getModuleWidget("RequestStatus").send_synchronize_cmd(f"UR, ModbusSetMargin")
            self.is_running = True
            self.timer.start(100)

    def update_progress(self):
        self.progress += self.progress_ratio
        #util.getModuleWidget("VeinConfigTop").set_status_info('高能量发射中', 'y')
        if self.progress >= 100:
            # util.getModuleWidget("VeinTreat").save_treatment_picture(1)
            # util.getModuleWidget("VeinTreat").update_point_status()
            # util.getModuleWidget("VeinTreat").on_start_compare()
            # util.getModuleWidget("VeinTreat").show_treat()
            self.timer.stop()
            self.is_running = False
            self.is_treating = False
            self.progress = 0
            self.setText('治疗')
            #util.getModuleWidget("VeinConfigTop").clear_status_info()
        self.update()

    def stop_treat(self):
        # util.getModuleWidget("VeinTreat").save_treatment_picture(1)
        # util.getModuleWidget("VeinTreat").on_start_compare()
        # util.getModuleWidget("VeinTreat").show_treat()
        self.timer.stop()
        self.is_running = False
        self.is_treating = False
        self.progress = 0
        self.setText('治疗')

    def paintEvent(self):
        painter = qt.QPainter(self)
        painter.setRenderHint(qt.QPainter.Antialiasing)

        button_rect = self.rect
        brush = qt.QBrush(qt.QColor('#004381'))
        if self.isEnabled():
            brush = qt.QBrush(qt.QColor('#2075F5'))
        painter.setBrush(brush)
        painter.setPen(qt.Qt.NoPen)
        painter.drawRoundedRect(button_rect, 32, 32)
        if self.is_running:
            if self.progress < self.delay_ratio:
                color = qt.QColor('#FC833F')
                self.setText('准备中')
            elif self.progress < self.cooldown_ratio:
                color = qt.QColor('#FCC73F')
                self.setText('冷却中')
            else:
                color = qt.QColor('#26AF4C')
                self.setText('治疗中')
                if not self.is_treating:
                    util.getModuleWidget("RequestStatus").send_cmd(f"UltrasoundGenerator, Send, 0, StartGenerator, 85")
                    self.is_treating = True

            painter.setBrush(color)
            painter.setPen(qt.Qt.NoPen)

            rect = qt.QRect(0, 0, self.width * self.progress // 100, self.height)
            painter.drawRoundedRect(rect, 32, 32)

        painter.setPen(qt.Qt.white)
        painter.drawText(self.rect, qt.Qt.AlignCenter, self.text)

        painter.end()
