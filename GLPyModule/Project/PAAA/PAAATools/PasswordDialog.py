from pynput import mouse
import qt
import slicer.util as util
import os
import ctypes
import threading


class PasswordDialog(qt.QDialog):
    def __init__(self, parent=None):
        super().__init__()
        self.setWindowFlags(qt.Qt.FramelessWindowHint | qt.Qt.Dialog)
        self.setModal(True)
        self.setGeometry(parent.geometry)

        layout = qt.QVBoxLayout()
        layout.setAlignment(qt.Qt.AlignCenter)

        self.password_input = qt.QLineEdit(self)
        self.password_input.setEchoMode(qt.QLineEdit.Password)
        self.password_input.setPlaceholderText('请输入登录密码')
        layout.addWidget(self.password_input)

        self.submit_button = qt.QPushButton('确认', self)
        self.submit_button.clicked.connect(self.check_password)
        layout.addWidget(self.submit_button)

        self.setLayout(layout)

    def check_password(self):
        if self.password_input.text == util.user_password:
            self.accept()
        else:
            self.password_input.clear()
            self.password_input.setPlaceholderText('密码不正确，请重新输入！')

    def closeEvent(self, event):
        event.ignore()  # 忽略关闭事件

    def keyPressEvent(self, event):
        if event.key() in (qt.Qt.Key_Return, qt.Qt.Key_Enter):
            self.submit_button.click()  # 将 Enter 键事件视为点击确认按钮
            return
        elif event.key() == qt.Qt.Key_Escape:
            event.ignore()  # 忽略Esc键
            return


class InputMonitor:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(InputMonitor, cls).__new__(cls)
        return cls._instance

    def __init__(self, dll_path='./input_monitor.dll'):
        if hasattr(self, 'initialized') and self.initialized:
            return
        self.activity = ctypes.c_int(0)
        self.monitor_lib = ctypes.CDLL(
            os.path.join(util.mainWindow().GetProjectBasePath(), "Resources", "input_monitor.dll"))
        self.monitor_lib.MonitorInput.argtypes = [ctypes.POINTER(ctypes.c_int)]
        self.thread = threading.Thread(target=self._monitor)
        self.thread.daemon = True
        self.initialized = True

    def _monitor(self):
        self.monitor_lib.MonitorInput(ctypes.byref(self.activity))

    def start(self):
        if not self.thread.is_alive():
            self.thread.start()

    def get_activity(self):
        return self.activity.value

    def reset_activity(self):
        self.activity.value = 0


class PopupDialog:
    def __init__(self):
        self.monitor = InputMonitor()
        self.monitor.start()

        # 启动定时器检查活动状态
        self.timer = qt.QTimer()
        self.timer.timeout.connect(self.check_activity)
        self.timer.start(1000)

        self.inactivity_timer = 0
        self.lock_time = 10

    def check_activity(self):
        activity = self.monitor.get_activity()
        print(f"activity {activity}")
        if activity == 0:
            self.inactivity_timer += 1
        else:
            self.inactivity_timer = 0
            self.monitor.reset_activity()

        if self.inactivity_timer >= self.lock_time:
            self.show_password_dialog()

    def show_password_dialog(self):
        dialog = PasswordDialog(util.mainWindow())
        dialog.exec_()
