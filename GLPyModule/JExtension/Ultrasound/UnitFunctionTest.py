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
import win32process
import win32gui
#
# UnitFunctionTest
#

class UnitFunctionTest(ScriptedLoadableModule):

  def __init__(self, parent):
    ScriptedLoadableModule.__init__(self, parent)
    self.parent.title = "UnitFunctionTest"  # TODO: make this more human readable by adding spaces
    self.parent.categories = ["JPlugins"]  # TODO: set categories (folders where the module shows up in the module selector)
    self.parent.dependencies = []  # TODO: add here list of module names that this module requires
    self.parent.contributors = ["jia ze yu"]  # TODO: replace with "Firstname Lastname (Organization)"
    # TODO: update with short description of the module and a link to online module documentation
    self.parent.helpText = """

"""
    # TODO: replace with organization, grant and thanks
    self.parent.acknowledgementText = """

"""

class CustomDialog(qt.QDialog):
  main_ui = None
  infoWidget = None
  def __init__(self, main, parent=None):
    super().__init__(parent)
    self.setWindowFlags(qt.Qt.WindowStaysOnTopHint)
    self.setAttribute(qt.Qt.WA_TranslucentBackground)  # 背景透明
    self.setAttribute(qt.Qt.WA_DeleteOnClose)  # 关闭时销毁
    self.setModal(False)

    self.module_path = os.path.dirname(slicer.util.modulePath("UnitFunctionTest"))
    print("dialog path:",self.module_path + '/Resources/UI/CustomDialog.ui')
    uiWidget = slicer.util.loadUI(self.module_path + '/Resources/UI/CustomDialog.ui')
    slicer.util.addWidget2(self, uiWidget)
    self.ui = slicer.util.childWidgetVariables(uiWidget)
    self.start_pos = None  # 记录鼠标初始位置
    width = 550
    height = 1000

    self.setFixedHeight(height)
    self.setFixedWidth(width)



#
# UnitFunctionTestWidget
#

class UnitFunctionTestWidget(JBaseExtensionWidget):
  dialog = None
  def setup(self):
    super().setup()
    self.ui.tabWidget.tabBar().hide()
    self.ui.tabWidget.setCurrentIndex(0)
    panel = slicer.qSlicerModulePanel()
    panel.setModuleManager(slicer.app.moduleManager())
    slicer.util.addWidget2(self.ui.widget_4, panel)
    panel.setModule("JWaterControl")

    panel = slicer.qSlicerModulePanel()
    panel.setModuleManager(slicer.app.moduleManager())
    slicer.util.addWidget2(self.ui.widget_5, panel)
    panel.setModule("JUltrasoundGenerator")

    panel = slicer.qSlicerModulePanel()
    panel.setModuleManager(slicer.app.moduleManager())
    slicer.util.addWidget2(self.ui.widget_6, panel)
    panel.setModule("JURRobotArm")

    panel = slicer.qSlicerModulePanel()
    panel.setModuleManager(slicer.app.moduleManager())
    slicer.util.addWidget2(self.ui.widget_7, panel)
    panel.setModule("JPowerControl")
    
    self.ui.btn_power.connect('toggled(bool)',self.on_power)
    self.ui.btn_robot.connect('toggled(bool)',self.on_robot)
    self.ui.btn_ultrasound.connect('toggled(bool)',self.on_ultrasound)
    self.ui.btn_water.connect('toggled(bool)',self.on_water)
    self.ui.btn_siduoke.connect('toggled(bool)',self.on_siduoke)
    
    self.ui.pushButton.connect('clicked()',self.on_connect)

    self.scrcpy_timer = qt.QTimer()
    self.scrcpy_timer.timeout.connect(self.startUltrasound)

    self.check_timer = qt.QTimer()
    self.check_timer.timeout.connect(self.findUltrasound)
    
    self.taskID = None
    self.handle = None
    self.ultra_process = None

    

    self.scrcpy_timer2 = qt.QTimer()
    self.scrcpy_timer2.timeout.connect(self.show_ultra)
    
    self.count = 0
    

  def ondd(self,val):
    print("XXXXXXXXXXXXAAAAAAAA")
    self.stop_check_scrcpy()


  def start_check_scrcpy(self):
        print("start_check_scrcpy")
        self.dialog = CustomDialog(self)
        self.dialog.connect("finished(int)",self.ondd)
        self.dialog.show()
        self.scrcpy_timer.start(100)
        
        self.scrcpy_timer2.start(100)
  
  def kill_process_by_name(self,process_name):
    import subprocess
    try:
        # 使用 taskkill 强制结束目标进程
        subprocess.run(f"taskkill /f /im {process_name}", shell=True, check=True)
        print(f"Process {process_name} has been killed.")
    except subprocess.CalledProcessError as e:
        print(f"Failed to kill process {process_name}. Error: {e}")

  def stop_check_scrcpy(self):
      print("stop_check_scrcpy")
      self.scrcpy_timer.stop()
      self.kill_process_by_name("scrcpy.exe")
      return
      process = qt.QProcess()
      process.start("taskkill.exe", ["scrcpy.exe"])
      process.waitForFinished()


  def show_ultra(self):
      if util.ultra_container:
          util.removeFromParent2(util.ultra_container)
          util.addWidget2(self.dialog.ui.widget, util.ultra_container)
          self.scrcpy_timer2.stop()

  def startUltrasound(self):
      if self.ultra_process is None or self.ultra_process.state() == qt.QProcess.NotRunning:
          print("start ultrasound2")
          util.ultra_container = None
          self.handle = None
          self.ultra_process = qt.QProcess()
          self.ultra_process.start('scrcpy.exe', util.scrcpy_command)
          self.taskID = self.ultra_process.processId()
          # print(f"taskID is {self.taskID}")
          self.check_timer.start(300)

  def findUltrasound(self):
      
      if not self.taskID:
          print("error---")
          return

      def get_all_hwnd(hwnd, mouse):
          if win32gui.IsWindow(hwnd) and win32gui.IsWindowEnabled(hwnd) and win32gui.IsWindowVisible(hwnd):
              _, window_pid = win32process.GetWindowThreadProcessId(hwnd)
              # print(window_pid, self.taskID)
              if window_pid == self.taskID:
                  self.handle = hwnd
                  window = qt.QWindow.fromWinId(self.handle)
                  util.ultra_container = qt.QWidget.createWindowContainer(window)
                  # print(f"Found window handle: {self.handle}")
                  # print(f"Window title: {win32gui.GetWindowText(hwnd)}")
                  self.check_timer.stop()
                  return False
          return True

      win32gui.EnumWindows(get_all_hwnd, 0)



  def on_robot(self,val):
    if val:
      self.ui.btn_power.setChecked(False)
      self.ui.btn_ultrasound.setChecked(False)
      self.ui.btn_water.setChecked(False)
      self.ui.btn_siduoke.setChecked(False)
      self.ui.tabWidget.setCurrentIndex(2)

  def on_power(self,val):
    if val:
      self.ui.btn_ultrasound.setChecked(False)
      self.ui.btn_water.setChecked(False)
      self.ui.btn_robot.setChecked(False)
      self.ui.btn_siduoke.setChecked(False)
      self.ui.tabWidget.setCurrentIndex(3)

  def on_ultrasound(self,val):
    if val:
      self.ui.btn_power.setChecked(False)
      self.ui.btn_water.setChecked(False)
      self.ui.btn_robot.setChecked(False)
      self.ui.btn_siduoke.setChecked(False)
      self.ui.tabWidget.setCurrentIndex(1)

  def on_water(self,val):
    if val:
      self.ui.btn_power.setChecked(False)
      self.ui.btn_ultrasound.setChecked(False)
      self.ui.btn_robot.setChecked(False)
      self.ui.btn_siduoke.setChecked(False)
      self.ui.tabWidget.setCurrentIndex(0)

  def on_siduoke(self,val):
    if val:
      
      self.ui.btn_power.setChecked(False)
      self.ui.btn_ultrasound.setChecked(False)
      self.ui.btn_robot.setChecked(False)
      self.ui.btn_water.setChecked(False)
      self.ui.tabWidget.setCurrentIndex(4)

  def on_connect(self):
    # self.stop_check_scrcpy()
    self.start_check_scrcpy()