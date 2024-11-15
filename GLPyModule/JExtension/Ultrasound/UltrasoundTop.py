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
# UltrasoundTop
#

class UltrasoundTop(ScriptedLoadableModule):
  def __init__(self, parent):
    ScriptedLoadableModule.__init__(self, parent)
    self.parent.title = "UltrasoundTop"  # TODO: make this more human readable by adding spaces
    self.parent.categories = ["RDN"]  # TODO: set categories (folders where the module shows up in the module selector)
    self.parent.dependencies = []  # TODO: add here list of module names that this module requires
    self.parent.contributors = ["jia ze yu"]  # TODO: replace with "Firstname Lastname (Organization)"
    # TODO: update with short description of the module and a link to online module documentation
    self.parent.helpText = """

"""
    # TODO: replace with organization, grant and thanks
    self.parent.acknowledgementText = """
1142[]
"""



#
# UltrasoundTopWidget
#

class UltrasoundTopWidget(JBaseExtensionWidget):
  module_index = 0
  moduleName = ""
  init_once_flag = False
  image_module = 7
  title_list =      ["系统自检", "患者数据", "机械臂准备", "水循环", "水囊准备", "水循环移除", "机械臂移除", "超声检查", "定位", "运动监测", "治疗", "管理员", "工程师"]
  sub_title_list =  ["设备初始化中", "填写患者信息", "", "", "", "", "", "治疗前检查", "", "", "", "", ""]
  btn_text_list =   ["登录 >", "开始治疗 >", "下一步 >", "下一步 >", "下一步 >", "下一步 >", "下一步 >", "定位 >", "进入治疗 >", "开始治疗 >", "结束治疗 >", "退出登录 >", "退出登录 >"]
  def setup(self):
    super().setup()
    print("UltrasoundTopWidget setup")
    util.layout_panel("middle_left").connect('moduleAdded(QString)',self.onModuleAdded)

  def onModuleAdded(self,module_name):
    self.moduleName = module_name
    if module_name == "JPCCS":
      self.module_index  = 1
    if module_name == "UltrasoundEpack":
      self.module_index = 2
    if module_name == "UltrasoundWater":
      self.module_index = 3
    if module_name == "UltrasoundBalloon":
      self.module_index = 4
    if module_name == "UltrasoundWaterRemove":
      self.module_index = 5
    if module_name == "UltrasoundEpackRemove":
      self.module_index = 6
    elif module_name == "UltrasoundImage":
      self.module_index = self.image_module
    elif module_name == "UltrasoundPositioning":
      self.module_index = self.image_module + 1
    elif module_name == "UltrasoundLaserPositioning":
      self.module_index = self.image_module + 2
    elif module_name == "UltrasoundTreat":
      self.module_index = self.image_module + 3
    elif module_name == "JAdministrator":
      self.module_index = self.image_module + 4
    elif module_name == "JEngineer":
      self.module_index = self.image_module + 5
    elif module_name == "UltrasoundCheckUp":
      self.module_index = 0
    self.set_top_info()

  def enter(self):
    self.init_once()
    self.addEvent(True)
    
  def init_once(self):
    if self.init_once_flag == True:
      return
    self.init_once_flag = True
    menu = qt.QMenu("", self.ui.btn_end)
    self.ui.btn_end.setPopupMode(qt.QToolButton.InstantPopup)
    action_new_segment = qt.QAction('新节段', menu)
    action_new_vein = qt.QAction('新血管', menu)
    action_new_patient = qt.QAction('新病患', menu)
    action_shut_down = qt.QAction('结束治疗', menu)
    action_new_segment.connect('triggered()', self.go_to_segment)
    action_new_vein.connect('triggered()', self.go_to_vein)
    action_new_patient.connect('triggered()', self.go_to_patient)
    action_shut_down.connect('triggered()', self.go_to_patient_direct)
    menu.addAction(action_new_segment)
    menu.addAction(action_new_vein)
    menu.addAction(action_new_patient)
    menu.addAction(action_shut_down)
    self.ui.btn_end.setMenu(menu)
    pass

  def go_to_segment(self):
    util.send_event_str(util.SetPage, 8)
    pass

  def go_to_vein(self):
    util.send_event_str(util.SetPage, 7)
    pass

  def go_to_patient(self):
    util.save_global_value('water_remove_next', 3)
    util.send_event_str(util.SetPage, 102)
    pass

  def go_to_patient_direct(self):
    util.save_global_value('water_remove_next', 3)
    util.send_event_str(util.SetPage, 3)
    pass

  def shut_down(self):    
    if self.module_index == 1:
      is_water_pack = util.get_global_value('water_pack', False)
      #是否加载水循环
      if is_water_pack:
        util.save_global_value('water_remove_next', 103)
        util.send_event_str(util.SetPage, 102)
      else:
        #是否加载机械臂
        is_arm_pack = util.get_global_value('arm_pack', False)
        if is_arm_pack:
          util.send_event_str(util.SetPage, 103)
        else:
          util.shut_down()
    else:
      util.shut_down()

  def exit(self):    
    self.addEvent(False)

  def addEvent(self,bool_val):
    self.add_button_event("btn_next", 'clicked()', self.on_next_click, bool_val)
    self.add_button_event("btn_reload", 'clicked()', self.on_reload_click, bool_val)
    self.add_button_event("btn_shutdown", 'clicked()', self.shut_down, bool_val)
    pass

  def on_shutdown_click(self):
    util.shut_down()

  def on_reload_click(self):
    slicer.util.reloadScriptedModule(self.moduleName)
    #slicer.util.reloadScriptedModule('UltrasoundSetting')

  def on_next_click(self):
    print(self.module_index, self.image_module)
    if self.module_index == 5:
      water_remove_next = util.get_global_value("water_remove_next", 103)
      print('water_remove_next', water_remove_next)
      util.send_event_str(util.SetPage, water_remove_next)
    elif self.module_index < self.image_module+3:
      util.send_event_str(util.GotoNextPage)
    else:
      util.send_event_str(util.SetPage, 2)

  def add_button_event(self, btn_name, operate_type, callback_func, is_connect):
    if hasattr(self.ui, btn_name) == False:
      return
    button = getattr(self.ui, btn_name)
    if is_connect == True:
      button.connect(operate_type, callback_func)
    else:
      button.disconnect(operate_type, callback_func)    

  def set_top_info(self):
    print('set_top_info', self.module_index, self.title_list[self.module_index])
    if self.module_index == 0:
      self.ui.btn_next.hide()
      self.ui.btn_end.hide()
    elif self.module_index == 5:
      self.ui.btn_next.show()
      self.ui.btn_end.hide()
    elif self.module_index == 6:
      self.ui.btn_next.hide()
      self.ui.btn_end.hide()
    elif self.module_index < self.image_module + 3:
      self.ui.btn_next.show()
      self.ui.btn_end.hide()
    elif self.module_index > self.image_module + 3:
      self.ui.btn_next.show()
      self.ui.btn_end.hide()
    else:
      self.ui.btn_next.hide()
      self.ui.btn_end.show()
      self.ui.btn_shutdown.hide()
    #在任何 情况都隐藏关机
    self.ui.btn_shutdown.hide()
    if self.module_index == 1 or self.module_index == 6:
      self.ui.btn_shutdown.show()
    if self.module_index >= len(self.title_list):
      return
    self.ui.lbl_title.setText(self.title_list[self.module_index])
    self.ui.lbl_title2.setText(self.sub_title_list[self.module_index])
    self.ui.btn_next.setText(self.btn_text_list[self.module_index])
    