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
#
# JMessageBox
#
class JMessageUI(qt.QDialog,ScriptedLoadableModuleWidget):
  def __init__(self, parent=None):
    super(JMessageUI, self).__init__()
    self.setWindowFlag(qt.Qt.FramelessWindowHint)
    self.setAttribute(qt.Qt.WA_TranslucentBackground)  # 使窗口透明
    
    # 设置对话框为全屏
    #self.showFullScreen()
    self.module_path = os.path.dirname(slicer.util.modulePath("JMessageBox"))
    print(self.module_path)
    uiWidget = slicer.util.loadUI(self.module_path + '/Resources/UI/JMessageUI.ui')
    slicer.util.addWidget2(self, uiWidget)
    self.ui = slicer.util.childWidgetVariables(uiWidget)
    self.ui.btnOK.connect("clicked()",self.accept)
    self.ui.btnOK2.connect("clicked()",lambda:self.done(2))
    self.ui.btnCancel.connect("clicked()",self.reject)

  # 设置弹框的信息
  # type 0:询问框3按钮;1:询问框2按钮;2:提示框;3:警示框;4:错误框
  def set_dialog_info(self, title, content, type, btnList):
    self.ui.lblTitle.setText(title)
    self.ui.lblMainMsg.setText(content)
    self.ui.btnOK.setText(btnList[0])
    icon_path = self.module_path + '/Resources/image/icon_question.png'
    self.ui.btnOK2.hide()
    self.ui.btnCancel.hide()
    if type == 0:
      self.ui.btnOK2.setText(btnList[1])
      self.ui.btnCancel.setText(btnList[2])
      self.ui.btnOK2.show()
      self.ui.btnCancel.show()
    elif type == 1:
      self.ui.btnCancel.setText(btnList[1])
      self.ui.btnCancel.show()
    elif type == 2:
      icon_path = self.module_path + '/Resources/image/icon_info.png'
      pass
    elif type == 3:
      icon_path = self.module_path + '/Resources/image/icon_warning.png'
      pass
    elif type == 4:
      icon_path = self.module_path + '/Resources/image/icon_error.png'
      pass
    test_str = "border-image: url("+icon_path +");"
    print(test_str)
    self.ui.lblIcon.setStyleSheet(test_str)
    
class JPopWindow(qt.QDialog,ScriptedLoadableModuleWidget):
  def __init__(self, parent=None):
    super(JPopWindow, self).__init__()
    self.setWindowFlag(qt.Qt.FramelessWindowHint)
    self.setAttribute(qt.Qt.WA_TranslucentBackground)  # 使窗口透明
    
    # 设置对话框为全屏
    #self.showFullScreen()
    self.module_path = os.path.dirname(slicer.util.modulePath("JMessageBox"))
    print(self.module_path)
    uiWidget = slicer.util.loadUI(self.module_path + '/Resources/UI/JPopWindow.ui')
    slicer.util.addWidget2(self, uiWidget)
    self.ui = slicer.util.childWidgetVariables(uiWidget)
    self.ui.btnClose.connect("clicked()",self.accept)

  def set_info(self, title, content):
    self.ui.lblTitle.setText(title)
    self.ui.lblMainMsg.setText(content)
    self.ui.lblMainMsg.show()

  def set_module(self, title, module_name):
    self.ui.lblMainMsg.hide()
    self.ui.lblTitle.setText(title)
    panel = slicer.qSlicerModulePanel()
    panel.setModuleManager(slicer.app.moduleManager())    
    slicer.util.addWidget2(self.ui.container, panel)
    panel.setModule(module_name)   

class JChangePassword(qt.QDialog,ScriptedLoadableModuleWidget):
  user_id = 0
  user_info = []
  def __init__(self, parent=None):
    super(JChangePassword, self).__init__()
    self.setWindowFlag(qt.Qt.FramelessWindowHint)
    self.setAttribute(qt.Qt.WA_TranslucentBackground)  # 使窗口透明
    
    # 设置对话框为全屏
    #self.showFullScreen()
    self.module_path = os.path.dirname(slicer.util.modulePath("JMessageBox"))
    print(self.module_path)
    uiWidget = slicer.util.loadUI(self.module_path + '/Resources/UI/JChangePassword.ui')
    slicer.util.addWidget2(self, uiWidget)
    self.ui = slicer.util.childWidgetVariables(uiWidget)
    self.ui.btnClose.connect("clicked()",self.reject)
    self.ui.btnChange.connect("clicked()",self.on_change)

  def on_change(self):
    passwd = self.ui.lblPwd.text
    passwd2 = self.ui.lblPwd2.text
    if passwd == "":
      util.getModuleWidget("JMessageBox").show_infomation('提示', '密码为空', 0)
      return
    if passwd != passwd2:
      util.getModuleWidget("JMessageBox").show_infomation('提示', '两次密码不一致', 0)
      return
    print(self.user_id, self.user_info)
    self.user_info[1] = passwd
    print(self.user_info)
    self.accept()

  def set_user_id(self, userid, userInfo):
    print("set user id: ", userid)
    self.user_id = userid
    self.user_info = userInfo

class JRegisterAccount(qt.QDialog,ScriptedLoadableModuleWidget):
  user_id = 0
  user_info = []
  def __init__(self, parent=None):
    super(JRegisterAccount, self).__init__()
    self.setWindowFlag(qt.Qt.FramelessWindowHint)
    self.setAttribute(qt.Qt.WA_TranslucentBackground)  # 使窗口透明
    
    # 设置对话框为全屏
    #self.showFullScreen()
    self.module_path = os.path.dirname(slicer.util.modulePath("JMessageBox"))
    print(self.module_path)
    uiWidget = slicer.util.loadUI(self.module_path + '/Resources/UI/JRegisterAccount.ui')
    slicer.util.addWidget2(self, uiWidget)
    self.ui = slicer.util.childWidgetVariables(uiWidget)
    self.ui.btnClose.connect("clicked()",self.reject)
    self.ui.btnChange.connect("clicked()",self.on_change)

  def on_change(self):
    account = self.ui.lblAccount.text
    passwd = self.ui.lblPwd.text
    passwd2 = self.ui.lblPwd2.text
    if passwd == "" or account == "" or passwd2 == "":
      util.getModuleWidget("JMessageBox").show_infomation('提示', '所有信息不得为空', 0)
      return
    if passwd != passwd2:
      util.getModuleWidget("JMessageBox").show_infomation('提示', '两次密码不一致', 0)
      return
    self.user_info[0] = account
    self.user_info[1] = passwd
    self.accept()

  def set_user_id(self, userInfo):
    self.user_info = userInfo

class JMessageBox(ScriptedLoadableModule):

  def __init__(self, parent):
    ScriptedLoadableModule.__init__(self, parent)
    self.parent.title = "JMessageBox"  # TODO: make this more human readable by adding spaces
    self.parent.categories = ["JPlugins"]  # TODO: set categories (folders where the module shows up in the module selector)
    self.parent.dependencies = []  # TODO: add here list of module names that this module requires
    self.parent.contributors = ["jia ze yu"]  # TODO: replace with "Firstname Lastname (Organization)"
    # TODO: update with short description of the module and a link to online module documentation
    self.parent.helpText = """

"""
    # TODO: replace with organization, grant and thanks
    self.parent.acknowledgementText = """

"""



#
# JMessageBoxWidget
#

class JMessageBoxWidget(JBaseExtensionWidget):
  module_name = ""
  def setup(self):
    super().setup()
    #适用于两个选项的询问框
  def show_question(self,title,content,btnDes=['是','否']):
    dialog = JMessageUI(slicer.util.mainWindow())
    dialog.set_dialog_info(title, content, 1, btnDes)
    result = dialog.exec_()
    return result
   

  #适用于三个选项的询问框
  def show_question2(self,title,content,btnDes):    
    dialog = JMessageUI(slicer.util.mainWindow())
    dialog.set_dialog_info(title, content, 0, btnDes)
    result = dialog.exec_()
    return result

  #适用于提示信息
  #type 类型 0:提示,1:警示,2:错误
  def show_infomation(self,title,content,dialog_type,btnDes=["好"]): 
    dialog = JMessageUI(slicer.util.mainWindow())
    dialog.set_dialog_info(title, content, dialog_type+2, btnDes)
    result = dialog.exec_()
    return result

  #适用于有大量的文字要显示
  #title 标题, file_path 文本路径
  def show_pop_window(self, title, file_path):
    content = "empty content"
    with open(file_path, "r") as file:
       content = file.read()
    dialog = JPopWindow(slicer.util.mainWindow())
    dialog.set_info(title, content)    
    result = dialog.exec_()
    return result

  #适用于加载模块
  #title 标题, modulename 模块名称
  def on_popup_modulepanel_dialog(self, title, modulename):
    self.module_name = modulename
    dialog = JPopWindow(slicer.util.mainWindow())
    dialog.set_module(title, modulename)    
    result = dialog.exec_()
    util.getModuleWidget(modulename).addEvent(False)
    return result

  #修改密码
  def show_change_password(self, user_id, user_info):
    dialog = JChangePassword(slicer.util.mainWindow())
    dialog.set_user_id(user_id, user_info)
    result = dialog.exec_()
    return result

  #注册账号
  def show_register_account(self, user_info):
    dialog = JRegisterAccount(slicer.util.mainWindow())
    dialog.set_user_id(user_info)
    result = dialog.exec_()
    return result

