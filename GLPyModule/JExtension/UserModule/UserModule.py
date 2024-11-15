import slicer
from slicer.ScriptedLoadableModule import *
from slicer.util import VTKObservationMixin
import requests
import concurrent.futures
from datetime import datetime


class UserModule(ScriptedLoadableModule):
    """Uses ScriptedLoadableModule base class, available at:
    https://github.com/Slicer/Slicer/blob/main/Base/Python/slicer/ScriptedLoadableModule.py
    """

    def __init__(self, parent):
        ScriptedLoadableModule.__init__(self, parent)
        self.parent.title = "UserModule"  # TODO: make this more human readable by adding spaces
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


class UserModuleWidget(ScriptedLoadableModuleWidget, VTKObservationMixin):
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
        self.uiWidget = slicer.util.loadUI(self.resourcePath("UI/UserDialog.ui"))
        self.layout.addWidget(self.uiWidget)
        self.ui = slicer.util.childWidgetVariables(self.uiWidget)

        # Set scene in MRML widgets. Make sure that in Qt designer the top-level qMRMLWidget's
        # "mrmlSceneChanged(vtkMRMLScene*)" signal in is connected to each MRML widget's.
        # "setMRMLScene(vtkMRMLScene*)" slot.
        self.uiWidget.setMRMLScene(slicer.mrmlScene)

        self._init_ui()
        self.server_address = None
        self.executor = concurrent.futures.ThreadPoolExecutor()
        self.session = requests.Session()  # 用于保持会话

    def _init_ui(self):
        self.ui.btn_set_server.clicked.connect(self.set_server)
        self.ui.btn_register.clicked.connect(self.start_register)
        self.ui.btn_login.clicked.connect(self.start_login)
        self.ui.btn_add_vip.clicked.connect(self.start_add_vip)

    def set_server(self):
        self.server_address = self.ui.edit_server_info.text
        self.ui.text_response.append(
            self.color_text(datetime.now().strftime('%Y-%m-%d %H:%M:%S'), 'green') + f" :{self.server_address}")

    def start_register(self):
        self.run_async(self.register)

    def start_login(self):
        self.run_async(self.login)

    def start_add_vip(self):
        self.run_async(self.add_vip)

    def run_async(self, func):
        self.executor.submit(func)

    def register(self):
        print("Starting register")
        username = self.ui.edit_username.text
        password = self.ui.edit_password.text
        realname = self.ui.edit_real_name.text
        role = self.ui.edit_role_ids.text
        data = {
            "username": username,
            "password": password,
            "realName": realname,
            "roleIds": role
        }
        url = "/system/passport/register"
        self.async_task(url, data)

    def login(self):
        print("Starting login")
        username = self.ui.edit_login_username.text
        password = self.ui.edit_login_password.text
        data = {
            "username": username,
            "password": password
        }
        url = "/system/passport/login"
        self.async_task(url, data)

    def add_vip(self):
        print("Starting addVIP")
        data = {}
        url = "/system/passport/add_vip"
        self.async_task(url, data)

    def concat_msg(self, response):
        message = ""
        for key, value in response.items():
            if key == "success":
                continue
            message += str(value)
        return message

    def color_text(self, text, color='red'):
        colored_text = f'<span style="color:{color};font-weight:bold;">{text}</span>'
        return colored_text

    def async_task(self, url, data):
        message = None
        try:
            response = self.session.post(self.server_address + url, data=data)
            response_json = response.json()
            print(response_json)
            message = self.concat_msg(response_json)
            message = self.color_text(datetime.now().strftime('%Y-%m-%d %H:%M:%S'), 'green') + f": {message}"
        except requests.exceptions.RequestException as e:
            message = self.color_text(datetime.now().strftime('%Y-%m-%d %H:%M:%S'), 'red') + f": {e}"
        finally:
            self.ui.text_response.append(message)
