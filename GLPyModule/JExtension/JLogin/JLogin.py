import imp
import ctypes
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

import uuid
import hashlib
import datetime
from HttpLib.HttpProtocols import *

from PAAATools.PasswordDialog import PopupDialog

target_date = datetime.date(2024, 3, 30)  # 截止时间
current_date = datetime.date.today()  # 当前时间
warning_date = 15


def getMachineCode():  # 机器码显示内容

    mac = util.mainWindow().GetVolumeID()
    combined_string = '0000' + mac
    md5_hash = hashlib.md5(combined_string.encode()).hexdigest()[:10]
    return md5_hash


def getAccess(key):  # 验证，秘钥正确返回1，错误返回0
    realkey = hashlib.md5(getMachineCode().encode()).hexdigest()[:6]
    print(realkey)
    if key == realkey and target_date > current_date:
        return 1
    else:
        return 0


#
# JLogin
#

class JLogin(ScriptedLoadableModule):

    def __init__(self, parent):
        ScriptedLoadableModule.__init__(self, parent)
        self.parent.title = "JLogin"  # TODO: make this more human readable by adding spaces
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
# JLoginWidget
#

class JLoginWidget(JBaseExtensionWidget):
    registered_usernames = []
    conn = None
    cursor = None
    permission = 1
    username = ""
    usbkey_inserted = True
    host = "http://www.3dbrainview.com:58888/client-api"

    account_list = ['rpadministrator', 'rpengineer']
    password_list = ['rpadmin1239', 'rpengin1239']
    jump_list = [100, 101]

    def setup(self):
        ScriptedLoadableModuleWidget.setup(self)
        login_style = util.get_from_PAAA("login_style", default="0")
        self.login_type = int(login_style)
        if int(login_style) == 0:
            login_style_project = util.getjson2("Global", "login_style", default_value="0")
            self.use_login_style(login_style_project)
        else:
            self.use_login_style(login_style)

        dll_path = self.resourcePathEx('libhasp.dll')
        print("test", dll_path)
        self.libhasp = ctypes.CDLL(dll_path)

        vendor_code_str = (
            "yfVhlDvndoqHdycGVilnL14HoBA254RHwF0Zzm0yZg2ho9Fjlzqx6jBQ0gr+Wy5YSZzQwvkdFfvgweUD"
            "IMhNTnBbEtr4grBBHt0EJO8Mz8ujCh6Sn9Iw17dOomRVjs6MPaYntW1trPHvCUU0eSaQca4If0S4yT9t"
            "JgbvVCyjuVJtxdAt1SbeAh3llHqGbSjS+tl+N0LUMqoLCnpNMqXuogQWiPmBOkohrgX8U539bqDCe6Rj"
            "PWL6X7KnPpvkBI6JnyfUETPglMeGEkBtubzpKDlKNw1rsasDBNFa8a4CTEG3+MfOafVtp0m8kwSaVbMj"
            "fN6FwizrKumwIuzZTpXVNfWk3O+eU1euop6r0AOIjUnaTWWXnuEdgDwkPaJs2qa/CO/4ifUlapEpEF4g"
            "9Oazj3l5evz06inMHCbVr5TiUparyzaarvX4G2zxRKrYbNO+nYHNz1q2CbMUPI0lL3mDANhtoAxlykGC"
            "jo87VpL2oe1DMtH9Wk88tx8yAsOkjCptPMAR5lNMebfyG1X0taRjsQKlI4+YLlGKEBgZJ1d2Z+rN/7Wl"
            "XbiLEJ1vSZ9Cy7m+Inhz1ALSi4OAV5CL5AXps7/6Q0iAomrxdsTJ9CjMjPuF0W4SU3R9CLDRK+7OwM4N"
            "p9Q1Js1BdgU15IHEwRklkAsmgdwWWS1KXhiuQj9bHVSgAU56Eni8xBtS8vH/TgLkSnEAtGpad3InMC5D"
            "g8wigilyF23pF9YgYm/y+fxLdYOse++I8tKKW1l+UrSNtbXB4gr6tjTGHjvsDl1Eyzbo0+H3rI01INHn"
            "NgEXVdTf7A6Z6NER1Ur6o20bOgHLDNkWHUkHNMLrWIEHldvQlWcGT10h89R8uIiVXJnQGmvxnnWza9jW"
            "O4GJt/NamsT9mO9Ckc6StuFNhTUU5wVoh7Y4W/eiqKMcnu0I0s2aVrJuwWiWUubhEG/pd2iRUafO1jXQ"
            "0tva7rOzY3m9BBi//TfjHw=="
        )

        # 将字符串转换为 c_ubyte 数组
        vendor_code_bytes = bytearray(map(ord, vendor_code_str))
        self.c_vendor_code = (ctypes.c_ubyte * len(vendor_code_bytes)).from_buffer(vendor_code_bytes)

        self.ui.tabWidget.tabBar().hide()
        self.ui.r_user_auth.setCurrentIndex(1)
        self.init_database()
        self.load_settings()
        qt.QWidget.setTabOrder(self.ui.r_username, self.ui.r_password_1)
        qt.QWidget.setTabOrder(self.ui.r_password_1, self.ui.r_password_2)
        qt.QWidget.setTabOrder(self.ui.r_password_2, self.ui.BtnDoRegister)
        qt.QWidget.setTabOrder(self.ui.l_username, self.ui.l_password)
        qt.QWidget.setTabOrder(self.ui.l_password, self.ui.BtnDoLogin)
        login_auth = util.getjson("login_auth", "0")
        if login_auth != 1 and hasattr(self.ui, 'pushButton'):
            self.ui.pushButton.setVisible(False)
        login_disclaimer = util.getjson("login_disclaimer", "0")
        print("login_disclaimer:", login_disclaimer)
        if login_disclaimer == "2":
            self.ui.pushButton_2.setVisible(True)
            # self.ui.label_11.setVisible(True)
        else:
            self.ui.pushButton_2.setVisible(False)
            # self.ui.label_11.setVisible(False)
        login_agreement = util.getjson("login_agreement", "0")
        login_privacy = util.getjson("login_privacy", "0")
        self.login_agreement = login_agreement
        self.login_privacy = login_privacy
        if login_agreement == "2" and login_privacy == "2":
            pass
        elif login_agreement == "2":
            self.ui.btnPrivacyPolicy.hide()
            self.ui.label_9.hide()
        elif login_privacy == "2":
            self.ui.btnUserAgreement.hide()
            self.ui.label_9.hide()
        else:
            self.ui.btnPrivacyPolicy.hide()
            self.ui.btnUserAgreement.hide()
            if self.ui.checkUserAgreement:
                self.ui.checkUserAgreement.hide()
            self.ui.label_9.hide()

    def use_login_style(self, style):
        print("use_login_style", style)
        util.mainWindow().setNeedConfirm(False)
        if int(style) == 0 or int(style) == 1:
            uiWidget = slicer.util.loadUI(self.resourcePath('UI/JLoginOrigin.ui'))
            self.layout.addWidget(uiWidget)
            self.ui = slicer.util.childWidgetVariables(uiWidget)
            uiWidget.setMRMLScene(slicer.mrmlScene)
            self.uiWidget = uiWidget
        elif int(style) == 2:
            uiWidget = slicer.util.loadUI(self.resourcePath('UI/JLoginBai.ui'))
            self.layout.addWidget(uiWidget)
            self.ui = slicer.util.childWidgetVariables(uiWidget)
            uiWidget.setMRMLScene(slicer.mrmlScene)
            self.uiWidget = uiWidget
            self.add_bai_style()
        elif int(style) == 3:
            uiWidget = slicer.util.loadUI(self.resourcePath('UI/JLogin3.ui'))
            self.layout.addWidget(uiWidget)
            self.ui = slicer.util.childWidgetVariables(uiWidget)
            uiWidget.setMRMLScene(slicer.mrmlScene)
            self.uiWidget = uiWidget
            self.set_style3()
        elif int(style) == 4:
            uiWidget = slicer.util.loadUI(self.resourcePath('UI/JLogin4.ui'))
            self.layout.addWidget(uiWidget)
            self.ui = slicer.util.childWidgetVariables(uiWidget)
            uiWidget.setMRMLScene(slicer.mrmlScene)
            self.uiWidget = uiWidget
            self.set_style4()
        elif int(style) == 5:
            uiWidget = slicer.util.loadUI(self.resourcePath('UI/JLogin5.ui'))
            self.layout.addWidget(uiWidget)
            self.ui = slicer.util.childWidgetVariables(uiWidget)
            uiWidget.setMRMLScene(slicer.mrmlScene)
            self.uiWidget = uiWidget
            self.set_style5()
        else:
            raise Exception("暂时不支持", int(style))
        self.ui.btnUserAgreement.setCursor(qt.QCursor(qt.Qt.PointingHandCursor))
        self.ui.btnPrivacyPolicy.setCursor(qt.QCursor(qt.Qt.PointingHandCursor))

    def set_style3(self):
        pass

    def set_style4(self):
        bg_img = self.resourcePathEx('Image/bg.png')
        style_str = "QWidget#tab_login{border-image: url(" + bg_img + ");}"
        self.ui.tab_login.setStyleSheet(style_str)

    def set_style5(self):
        bg_img = self.resourcePathEx('Image/bg.png')
        style_str = "QWidget#tab_login{border-image: url(" + bg_img + ");}"
        self.ui.tab_login.setStyleSheet(style_str)
        style_str = "QWidget#tab{border-image: url(" + bg_img + ");}"
        self.ui.tab.setStyleSheet(style_str)
        use_keyboard = util.getjson2("Global", "use_keyboard", default_value="0")
        self.ui.l_username.setVirtualKeyBoardState(use_keyboard == "2")
        self.ui.BtnReturnToRegister.hide()
        # #self.usbkey_inserted = False
        # self.set_label_style_sheet(self.ui.lblInsertUsbkeyIcon, "login_icon_key1")
        # self.timer = qt.QTimer()
        # self.timer.setInterval(1000)
        # self.timer.connect('timeout()', self.usbkey_verification)
        # self.timer.start()
        util.mainWindow().setNeedConfirm(False)
        error_des = util.get_error_info()
        if error_des != "":
            self.ui.tabWidget.setCurrentIndex(2)
            self.ui.lbl_error_info.setText(error_des)
        else:
            self.ui.tabWidget.setCurrentIndex(0)

    def add_bai_style(self):
        util.add_pixelmap_to_label(self.resourcePath('Icons/bg.jpg'), self.ui.label_7)
        util.add_pixelmap_to_label(self.resourcePath('Icons/inputUsernameNone.png'), self.ui.lblUser)
        util.add_pixelmap_to_label(self.resourcePath('Icons/inputPasswordNone.png'), self.ui.lblPassword)
        self.ui.btnUserAgreement.connect("clicked()", self.on_click_agreement)
        self.ui.btnPrivacyPolicy.connect("clicked()", self.on_click_privacy)

    def usbkey_verification(self):
        # result = self.libhasp.usbkey_verification(self.c_vendor_code)
        # if result != 0:
        #   return
        # self.timer.stop()
        # self.set_label_style_sheet(self.ui.lblInsertUsbkeyIcon, "login_icon_key2")
        # self.ui.labelInsertUsbkey.setText("密钥已插入")
        # self.usbkey_inserted = True
        return

    def set_label_style_sheet(self, lbl, image_name):
        img_path = self.resourcePathEx(f'Image/{image_name}.png')
        style_str = "border-image: url(" + img_path + ");"
        print(style_str)
        lbl.setStyleSheet(style_str)

    def on_click_privacy(self):
        agreement_file = "text/privacy.txt";
        if self.login_type == 2:
            agreement_file = "text/privacy2.txt";
        elif self.login_type == 3:
            agreement_file = "text/privacy3.txt";
        file_path = self.resourcePath(agreement_file)
        self._message_box_path(file_path, "隐私条款")

    def on_click_agreement(self):
        agreement_file = "text/agreement.txt";
        if self.login_type == 2:
            agreement_file = "text/agreement2.txt";
        elif self.login_type == 3:
            agreement_file = "text/agreement3.txt";
        file_path = self.resourcePath(agreement_file)
        self._message_box_path(file_path, "服务协议")

    def _message_box_path(self, file_path, title):
        content = "empty content"
        with open(file_path, "r") as file:
            content = file.read()

        # icon_path = self.resourcePath('Icons/ticon.png')
        # pixelmap = qt.QPixmap(icon_path)
        msg_box = qt.QMessageBox()
        # dialog.SetTitle("服务协议")
        msg_box.setWindowTitle(title)
        # msg_box.setIconPixmap(pixelmap)
        text_widget = qt.QWidget()
        text_layout = qt.QVBoxLayout(text_widget)

        scroll_area = qt.QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(qt.Qt.ScrollBarAlwaysOff)

        text_label = qt.QLabel()
        text_label.setWordWrap(True)

        scroll_area.setWidget(text_label)

        text_layout.addWidget(scroll_area)
        text_widget.setLayout(text_layout)

        msg_box.layout().addWidget(text_widget)
        text_widget.setFixedSize(600, 800)
        msg_box.setFixedSize(600, 800)
        text_label.setText(content)
        msg_box.exec()

    def enter(self):
        super().enter()
        skip = util.get_from_PAAA("skip_login") == "2"
        if skip:
            util.singleShot(110, lambda: self.ui.BtnDoLogin.animateClick(10))

    def init_database(self):
        import sqlite3
        dbpath = os.path.join(util.mainWindow().GetProjectBasePath(), "Resources", "user_data.db")
        # 创建数据库连接
        self.conn = sqlite3.connect(dbpath)
        self.cursor = self.conn.cursor()

        # 创建用户表格
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            password TEXT NOT NULL,
            permission INTEGER DEFAULT 0,
            registration_time TEXT,
            last_login_time TEXT,
            md5 TEXT
        )
    ''')
        self.conn.commit()

        self.cursor.execute('''CREATE TABLE IF NOT EXISTS settings (
                      id INTEGER PRIMARY KEY AUTOINCREMENT,
                      username TEXT NOT NULL UNIQUE,
                      password TEXT NOT NULL,
                      remember_password INTEGER,
                      show_password INTEGER,
                      agree_protocol BOOLEAN
                      )''')

        # 提交更改并关闭连接
        self.conn.commit()
        self.register_admin_and_engineer()

    def register_admin_and_engineer(self):
        for i in range(2):
            account = self.account_list[i]
            password = self.password_list[i]
            self.cursor.execute('SELECT * FROM users WHERE username = ?', (account,))
            user_data = self.cursor.fetchone()
            if user_data:
                continue
            self.register_user(account, password)

    def load_settings(self):
        self.cursor.execute('''SELECT * FROM settings LIMIT 1''')
        result = self.cursor.fetchone()
        if result:
            id, username, password, remember_password, show_password, agree_protocol = result
            print(id, username, password, remember_password, show_password)
            if remember_password:
                self.ui.l_password.setText(password)
            self.ui.l_username.setText(username)
            self.ui.l_cb_remember_password.setChecked(remember_password)
            self.ui.l_cb_show_password.setChecked(show_password)
            self.ui.l_cb_show_agree.setChecked(agree_protocol)
            self.on_show_password(show_password)
            if hasattr(self.ui, 'checkUserAgreement'):
                self.ui.checkUserAgreement.setChecked(True)

        else:
            pass

    def addEvent(self, boolVal):
        self.add_button_event('BtnDoActivate', 'clicked()', self.do_activate, boolVal)
        self.add_button_event('BtnDoLogin', 'clicked()', self.on_do_login, boolVal)
        self.add_button_event('BtnDoModifyPassword', 'clicked()', self.on_modify_password, boolVal)
        self.add_button_event('BtnDoRegister', 'clicked()', self.on_do_register, boolVal)
        self.add_button_event('BtnReturnToRegister', 'clicked()', self.on_register, boolVal)
        self.add_button_event('BtnReturnToLogin', 'clicked()', self.on_return_to_login, boolVal)
        self.add_button_event('BtnReturnToLogin_2', 'clicked()', self.on_return_to_login, boolVal)
        self.add_button_event('BtnReturnToLogin_3', 'clicked()', self.on_return_to_login, boolVal)

        self.add_button_event('btnPrivacyPolicy', 'clicked()', self.on_click_privacy, boolVal)
        self.add_button_event('btnUserAgreement', 'clicked()', self.on_click_agreement, boolVal)
        self.add_button_event('btnPrivacyPolicy', 'clicked()', self.on_click_privacy, boolVal)

        self.add_button_event('log_export', 'clicked()', self.on_log_export, boolVal)

        self.add_button_event('pushButton', 'clicked()', self.on_activate, boolVal)
        self.add_button_event('pushButton_2', 'clicked()', self.on_claimer, boolVal)
        self.add_button_event('btn_shutdown', 'clicked()', self.shut_down, boolVal)

        self.add_button_event('l_cb_remember_password', 'toggled(bool)', self.on_remember_password, boolVal)
        self.add_button_event('l_cb_show_agree', 'toggled(bool)', self.on_show_agree, boolVal)
        self.add_button_event('l_cb_show_password', 'toggled(bool)', self.on_show_password, boolVal)

    def on_focus_user(self):
        self.ui.l_username.setFocus()
        util.show_osk()

    def on_focus_password(self):
        self.ui.l_password.setFocus()
        util.show_osk()

    def add_button_event(self, btn_name, operate_type, callback_func, is_connect=True):
        if hasattr(self.ui, btn_name) == False:
            return
        button = getattr(self.ui, btn_name)
        if is_connect == True:
            button.connect(operate_type, callback_func)
        else:
            button.disconnect(operate_type, callback_func)

    def on_claimer(self):
        util.messageBox2(
            "免责声明\n\n1.本软件目前仍处于测试阶段，不应被视为一个完全稳定的产品。\n\n2.使用者在使用此软件进行医疗手术或其他医疗操作之前，应当进行充分的评估和审查，以确定其适用性和安全性。\n\n3.我们不对因使用或依赖本软件而导致的任何直接、间接、特殊、偶然或结果性损害（包括但不限于人身伤害、无法进行手术、手术失败或其他任何损失）承担责任。\n\n4.使用者应当理解并接受所有与使用此软件相关的风险，并同意自行承担这些风险。\n\n5.使用本软件表示您已阅读、理解并同意本免责声明的所有条款。",
            title="免责声明")

    def copy_logs(self, source_folder, destination_folder):
        import shutil
        # 确保目标文件夹存在，如果不存在就创建
        if not os.path.exists(destination_folder):
            os.makedirs(destination_folder)

        # 获取源文件夹中所有.log文件的列表
        log_files = [f for f in os.listdir(source_folder) if f.endswith('.log')]

        # 遍历.log文件并复制到目标文件夹
        for log_file in log_files:
            source_path = os.path.join(source_folder, log_file)
            destination_path = os.path.join(destination_folder, log_file)
            shutil.copy2(source_path, destination_path)  # 使用shutil.copy2以保留文件元数据（

    def on_log_export(self):
        logpath = util.getLogPath()
        dicomDataDir = "D:/"
        if True:
            res_path, result = util.show_file_dialog(2)
            if result == 0:
                return
            else:
                dicomDataDir = res_path
        self.copy_logs(logpath, dicomDataDir)
        util.showWarningText("导出成功")

    def on_activate(self):
        self.ui.tabWidget.setCurrentIndex(2)
        self.ui.r_username_2.setText(getMachineCode())

    def do_activate(self):
        text = self.ui.r_password_4.text.strip()
        val = getAccess(text)
        if val == 1:
            self.ui.tabWidget.setCurrentIndex(0)
            util.showWarningText("激活成功")
            util.save_to_PAAA("md5", text)
        else:
            util.showWarningText("激活码错误或者激活码已经失效")

    def on_show_agree(self, boolval):
        pass

    def on_show_password(self, boolva):
        if not boolva:
            self.ui.l_password.setEchoMode(qt.QLineEdit.Password)
        else:
            self.ui.l_password.setEchoMode(qt.QLineEdit.Normal)

    def on_remember_password(self, boolva):
        pass

    def show_error(self, text):
        self.ui.r_error_text.setText(text)
        self.ui.r_error_text_2.setText(text)
        if hasattr(self.ui, 'r_error_text_4'):
            self.ui.r_error_text_4.setText(text)

    def is_valid_password(self, password, username):
        import re
        # 长度限制：密码最小长度为8，最大长度为20
        # if len(password) < 8 or len(password) > 20:
        #   self.show_error("密码限制在8到20个字符之内")
        #   return False

        # # 复杂性要求：密码应包含至少一个大写字母、一个小写字母、一个数字和一个特殊字符
        # if not re.search(r"[A-Z]", password) or \
        #     not re.search(r"[a-z]", password) or \
        #     not re.search(r"\d", password) or \
        #     not re.search(r"[!@#$%^&*]", password):
        #     self.show_error("密码应包含至少一个大写字母、一个小写字母、一个数字和一个特殊字符")
        #     return False

        # # 禁止常见密码
        # if password.lower() in self.password_blacklist:
        #     return False

        # 不允许用户名作为密码
        # if username.lower() in password.lower():
        #   self.show_error("不允许用户名作为密码")
        #   return False

        # # 不允许连续字符
        # for i in range(len(password) - 1):
        #     if ord(password[i]) == ord(password[i + 1]) - 1 or ord(password[i]) == ord(password[i + 1]) + 1:
        #       self.show_error("不允许连续字符作为密码")
        #       return False

        return True

    def is_valid_username(self, username):
        limit_type = util.getjson2("Global", "username_limit", default_value="0")
        print("limit_type", limit_type)
        if limit_type != "2":
            return True
        # 长度限制：设置用户名最小和最大长度为6和20
        if len(username) < 6 or len(username) > 20:
            self.show_error("用户名限制在4到20个字符之内")
            return False

        # 字符限制：用户名只能包含字母、数字和下划线
        if not username.isalnum():
            self.show_error("用户名只能包含字母、数字")
            return False

        # # 禁止纯数字或纯字母用户名
        if username.isdigit() or username.isalpha():
            self.show_error("用户名不能是纯字母或者数字")
            return False

        # 敏感词过滤：检查用户名中是否包含敏感词
        sensitive_words = ["admin", "root", "password", "123456"]
        if any(word in username.lower() for word in sensitive_words):
            self.show_error("用户名不能包含敏感词")
            return False

        # 唯一性检查：确保用户名在系统中是唯一的
        if username.lower() in self.registered_usernames:
            self.show_error("已注册过该用户")
            return False

        return True

    def on_login_success(self):
        self.show_error("")
        # util.mainWindow().setWindowTitle((self.username))
        util.username = self.username

        login_auth = util.getjson("login_auth", 0)
        if login_auth == 1:
            md5 = util.get_from_PAAA("md5", "").strip()
            if md5 == "":
                util.showWarningText("请先激活软件")
                return
            res = getAccess(md5)
            if res == 0:
                util.showWarningText("当前试用版本已失效，请联系管理员")
                return
            delta = target_date - current_date
            days_difference = delta.days
            if days_difference < warning_date:
                util.showWarningText("试用版本将过期，请联系管理员，避免影响后续正常使用")
        elif login_auth == 2:
            user_name = self.ui.l_username.text.strip()
            password1 = self.ui.l_password.text.strip()
            self.httpNet = HttpNetwork(self.host)
            flag, message = self.httpNet.Login2Server(user_name, password1)
            if not flag:
                util.showWarningText(message)
                return
        else:
            pass

        # dicomBrowser = slicer.modules.dicom.widgetRepresentation().self().browserWidget.dicomBrowser
        # dicomDatabase = dicomBrowser.database()
        # sql_directory = os.path.join(util.mainWindow().GetProjectBasePath(), "Resources", "Database",
        #                              util.username).replace('\\', '/')
        # if not os.path.exists(sql_directory):
        #     os.makedirs(sql_directory)
        # sql_directory = os.path.join(sql_directory, "ctkDICOM.sql").replace('\\', '/')
        # dicomDatabase.openDatabase(sql_directory)

        # 查询"users"表中的第一行数据
        self.cursor.execute('''SELECT * FROM settings LIMIT 1''')
        result = self.cursor.fetchone()

        username = self.ui.l_username.text
        password = self.ui.l_password.text
        remember_password = self.ui.l_cb_remember_password.checked
        show_password = self.ui.l_cb_show_password.checked
        agree_protocol = self.ui.l_cb_show_agree.checked
        # 如果查询结果不为空，则更新第一行数据
        if result:
            self.cursor.execute('''UPDATE settings
                          SET username=?, password=?, remember_password=?, show_password=?, agree_protocol=?
                          WHERE id=?''',
                                (username, password, remember_password, show_password, agree_protocol, result[0]))
        else:
            # 否则，插入一条新的数据
            self.cursor.execute('''INSERT INTO settings (username, password, remember_password, show_password, agree_protocol)
                          VALUES (?, ?, ?, ?, ?)''',
                                (username, password, remember_password, show_password, agree_protocol))

        self.conn.commit()

        util.user_password = password
        # _ = PopupDialog()  # 鼠标键盘监控
        self.set_ultrasound_info()
        for i in range(len(self.account_list)):
            account = self.account_list[i]
            if account != self.username:
                continue
            util.send_event_str(util.SetPage, self.jump_list[i])
            return
        util.send_event_str(util.GotoNextPage, "1")

    def set_ultrasound_info(self):
        util.getModuleWidget("RequestStatus").send_cmd(f"UltraImage, SetActivateProbe, L40")
        # probe_info = \
        #     util.getModuleWidget("RequestStatus").send_synchronize_cmd(f"UltraImage, GetInitProbe").split(",")[0].split(
        #         "=")[1]
        # print(f"probe_info {probe_info}")
        # util.getModuleWidget("RequestStatus").send_cmd(f"UltraImage, SetActivateProbe, {probe_info}")
        util.global_data_map['UltraSoundSettingPanel'].set_probes("L40")
        util.global_data_map['UltraSoundSettingPanel'].on_ctkSliderWidgetChanged(3)
        util.getModuleWidget("RequestStatus").send_cmd(f"UltraImage, SetGapMax, 3")
        # util.getModuleWidget("RequestStatus").send_cmd(f"UltraImage, SetLiveGain, {int(100)}")
        # util.getModuleWidget("RequestStatus").send_cmd(f"UltraImage, SetDepth, {16}")
        # util.getModuleWidget("RequestStatus").send_cmd(f"UltraImage, setDebugMode, SaveToBin")
        # util.getModuleWidget("RequestStatus").send_cmd(f"UltraImage, setDebugMode, SaveToPng")
        # util.getModuleWidget("RequestStatus").send_cmd(f"UltraImage, setDebugMode, SaveToPng2")

        # util.getModuleWidget("RequestStatus").send_cmd(f"UltraImage, CaculateBModeFPS")
        # util.getModuleWidget("RequestStatus").send_cmd(f"UltraImage, CaculateTModeFPS")
        # util.getModuleWidget("RequestStatus").send_cmd(f"UltraImage, CaculatePDIModeFPS")
        util.getModuleWidget("RequestStatus").send_cmd(f"UltraImage, SaveToBinFlag")

    def on_do_login(self):
        if self.usbkey_inserted == False:
            util.showWarningText("请插入密钥")
            return False
        user_name = self.ui.l_username.text
        password1 = self.ui.l_password.text

        if len(user_name) == 0 or len(password1) == 0:
            util.showWarningText("用户名或者密码为空")
            return False

        if not self.is_valid_username(user_name):
            util.showWarningText("用户名非法")
            return False

        if not self.ui.l_cb_show_agree.checked:
            util.showWarningText("请先同意免责声明")
            return False

        error_info_tmp = ""
        if self.login_agreement == "2" and self.login_privacy == "2":
            error_info_tmp = "请阅读并同意服务协议和隐私政策"
        elif self.login_agreement == "2":
            error_info_tmp = "请阅读并同意服务协议"
        elif self.login_privacy == "2":
            error_info_tmp = "请阅读并同意隐私政策"
        if error_info_tmp != "" and not self.ui.checkUserAgreement.checked:
            util.showWarningText(error_info_tmp)
            return False
        # 查询用户信息
        self.cursor.execute(
            'SELECT id, username, password, permission, registration_time, last_login_time, md5 FROM users WHERE username = ?',
            (user_name,))
        user_data = self.cursor.fetchone()

        if user_data:
            # 管理员

            # 用户名存在，验证密码
            _, self.username, stored_password, self.permission, registration_time, last_login_time, md5 = user_data
            if stored_password == password1:
                if int(user_data[3]) == 0:
                    self.show_error("")
                    self.ui.tabWidget.setCurrentIndex(3)
                else:
                    login_info = [self.username, stored_password, str(self.permission), registration_time,
                                  last_login_time]
                    md5_value = util.get_md5_value(login_info)
                    self.show_error("")
                    if md5 != md5_value:
                        self.show_error("md5验证失败,数据被篡改")
                        return False
                    else:
                        from datetime import datetime
                        login_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        login_info[4] = login_time
                        md5_value = util.get_md5_value(login_info)
                        self.cursor.execute('UPDATE users set last_login_time=?, md5=? WHERE username = ?',
                                            (login_time, md5_value, user_name))
                        self.on_login_success()
                        return True
            else:
                self.show_error("密码错误,请重新输入")
                return False
        else:
            # 用户名不存在
            self.show_error("当前用户不存在")
            return False

    def on_modify_password(self):
        user_name = self.ui.r_username_3.text
        password1 = self.ui.r_password_5.text
        password2 = self.ui.r_password_3.text
        if user_name == "":
            self.show_error("请输入用户名")
            return
        if not self.is_valid_username(user_name):
            return
        if password1 == "":
            self.show_error("请输入密码")
            return
        if password2 == "":
            self.show_error("请输入重复密码")
            return
        if password1 != password2:
            self.show_error("两次输入的密码不一样")
            return
        if not self.is_valid_password(password1, user_name):
            return
        if not self.modify_user(user_name, password1):
            return
        self.show_error("")
        util.showWarningText("修改成功")
        self.ui.tabWidget.setCurrentIndex(0)

    def on_do_register(self):
        user_name = self.ui.r_username.text
        password1 = self.ui.r_password_1.text
        password2 = self.ui.r_password_2.text
        if user_name == "":
            self.show_error("请输入用户名")
            return
        if not self.is_valid_username(user_name):
            return
        if password1 == "":
            self.show_error("请输入密码")
            return
        if password2 == "":
            self.show_error("请输入重复密码")
            return
        if password1 != password2:
            self.show_error("两次输入的密码不一样")
            return
        if not self.is_valid_username(user_name):
            self.show_error("用户名非法")
            return
        if not self.is_valid_password(password1, user_name):
            return
        if not self.register_user(user_name, password1):
            return
        self.show_error("")
        util.showWarningText("注册成功")
        self.on_return_to_login()

    def modify_user(self, new_username, new_password):
        from datetime import datetime
        self.cursor.execute(
            'SELECT id, username, password, permission, registration_time, last_login_time, md5 FROM users WHERE username = ?',
            (new_username,))
        user_data = self.cursor.fetchone()

        if user_data:
            # 用户名存在，验证密码
            _, old_username, old_password, tmp_ermission, registration_time, last_login_time, md5 = user_data
            if stored_password == password1:
                if int(user_data[3]) == 0:
                    self.show_error("")
                    self.ui.tabWidget.setCurrentIndex(3)
                else:
                    login_info = [old_username, old_password, str(tmp_ermission), registration_time, last_login_time]
                    md5_value = util.get_md5_value(login_info)
                    self.show_error("")
                    if md5 != md5_value:
                        self.show_error("md5验证失败,数据被篡改")
                        return False
                    else:
                        login_info[1] = new_password
                        md5_value = util.get_md5_value(login_info)
                        self.cursor.execute('UPDATE users set password=?, md5=? WHERE username = ?',
                                            (password, md5_value, user_name))
                        return True
            else:
                self.show_error("密码错误,请重新输入")
                return False
        else:
            # 用户名不存在
            self.show_error("当前用户不存在")
            return False
        return False

    def register_user(self, username, password):
        from datetime import datetime
        # 检查用户名是否已经存在
        self.cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
        existing_user = self.cursor.fetchone()

        if existing_user:
            self.show_error("用户名已经存在")
            return False

        # 获取当前时间作为注册时间
        registration_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # 插入新用户信息
        sign_up_list = [username, password, str(self.ui.r_user_auth.currentIndex), registration_time, registration_time]
        md5_value = util.get_md5_value(sign_up_list)
        self.cursor.execute(
            'INSERT INTO users (username, password, permission, registration_time, last_login_time, md5) VALUES (?, ?, ?, ?, ?, ?)',
            (username, password, self.ui.r_user_auth.currentIndex, registration_time, registration_time, md5_value))
        res = self.conn.commit()
        print("User registered successfully.", res)
        return True

    def on_register(self):
        self.ui.tabWidget.setCurrentIndex(1)

    def on_return_to_login(self):
        self.ui.tabWidget.setCurrentIndex(0)

    def shut_down(self):
        util.shut_down()
