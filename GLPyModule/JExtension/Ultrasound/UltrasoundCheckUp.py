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
from qt import QPropertyAnimation
#
# UltrasoundCheckUp
#

class UltrasoundCheckUp(ScriptedLoadableModule):

  def __init__(self, parent):
    ScriptedLoadableModule.__init__(self, parent)
    self.parent.title = "UltrasoundCheckUp"  # TODO: make this more human readable by adding spaces
    self.parent.categories = ["RDN"]  # TODO: set categories (folders where the module shows up in the module selector)
    self.parent.dependencies = []  # TODO: add here list of module names that this module requires
    self.parent.contributors = ["jia ze yu"]  # TODO: replace with "Firstname Lastname (Organization)"
    # TODO: update with short description of the module and a link to online module documentation
    self.parent.helpText = """

"""
    # TODO: replace with organization, grant and thanks
    self.parent.acknowledgementText = """

"""

class CheckUpItem:
  ui = None
  timer = None
  img_ani_list = []
  img_success = ""
  img_failed = ""
  current_idx = 1
  des = ""
  def __init__(self, in_ui, des, ani_list, success_img, failed_img) -> None:
    self.ui = in_ui
    self.ui.lbl_des.setText(des)
    self.des = des
    self.timer = qt.QTimer()
    self.timer.setInterval(200)
    self.timer.connect('timeout()', self.set_ani)
    self.img_ani_list = ani_list
    self.img_success = success_img
    self.img_failed = failed_img
    self.ui.btnGetSolution.connect('clicked()', self.get_solutions)
    self.set_state(2)

  def get_solutions(self):
    scriptedModulesPath = os.path.dirname(slicer.util.modulePath("UltrasoundCheckUp"))
    file_path =  scriptedModulesPath + '/Resources/Info/' + self.des + '.txt'
    util.getModuleWidget("JMessageBox").show_pop_window('解决方案', file_path)
    print(file_path)

  def set_state(self, state):
    if state == 0:
      self.set_state_icon(self.img_ani_list[self.current_idx])
      self.timer.start()
      return
    self.timer.stop()
    self.ui.btnGetSolution.hide()
    image_path = self.img_success
    if state == 2:
      image_path = self.img_failed
      self.ui.btnGetSolution.show()
    self.set_state_icon(image_path)

  def set_state_icon(self, img_path):
    style_str = "border-image: url("+img_path +");"           
    self.ui.lbl_state_icon.setStyleSheet(style_str)

  def set_ani(self):
    self.current_idx = self.current_idx + 1
    if self.current_idx > len(self.img_ani_list):
      self.current_idx = 1
    self.set_state_icon(self.img_ani_list[self.current_idx])
    pass
#
# UltrasoundCheckUpWidget
#

class UltrasoundCheckUpWidget(JBaseExtensionWidget):
  old_xpos = 0
  init_once_flag = False
  check_item_list = []
  check_des_list = ['设备通电', '超声设备初始化', 'vtu检测通过', '电机校准']
  def setup(self):
    super().setup()
    print("UltrasoundCheckUpWidget setup")

  def enter(self):
    self.init_once()
    self.addEvent(True)
    
  def init_once(self):
    if self.init_once_flag == True:
      return
    self.init_once_flag = True
    print("init_once")
    self.set_label_style_sheet(self.ui.lbl_bg, "1")
    util.singleShot(10,self.init_later)

  def auto_next_step(self):
    util.send_event_str(util.SetPage, 2)

  def init_later(self):
    self.init_check_list()

    state_list = [1, 1, 1, 1]
    self.set_check_state(state_list)
    pass

  def init_check_list(self):
    self.ui.list_items.setSpacing(12)
    ani_list = []
    width_of_list = self.ui.list_items.width
    for i in range(4):
      img_path1 = self.resourcePathEx(f'Image/ani_test{i}.png')
      ani_list.append(img_path1)
    success_img = self.resourcePathEx('Image/icon_normal.png')
    failed_img = self.resourcePathEx('Image/icon_unnormal.png')
    for des in self.check_des_list:
      template1 = slicer.util.loadUI(self.resourcePath("UI/CheckUpItem.ui"))
      template1ui = slicer.util.childWidgetVariables(template1)
      template = CheckUpItem(template1ui, des, ani_list, success_img, failed_img)
      item = qt.QListWidgetItem(self.ui.list_items)
      item.setSizeHint(qt.QSize(width_of_list-30, 130))
      self.ui.list_items.setItemWidget(item, template1)
      self.ui.list_items.addItem(item)
      self.check_item_list.append(template)
    pass

  def set_check_state(self, state_list):
    is_auto_login = True
    item_len = len(self.check_item_list)
    if item_len != len(state_list):
      return
    for i in range(item_len):
      state = state_list[i]
      if state == 2:
        is_auto_login = False
      self.check_item_list[i].set_state(state)
    if is_auto_login:
      util.singleShot(2000,self.auto_next_step)

  def exit(self):    
    self.addEvent(False)

  def addEvent(self,bool_val):
    pass

  def add_button_event(self, btn_name, operate_type, callback_func, is_connect):
    if hasattr(self.ui, btn_name) == False:
      return
    button = getattr(self.ui, btn_name)
    if is_connect == True:
      button.connect(operate_type, callback_func)
    else:
      button.disconnect(operate_type, callback_func)  

  def set_label_style_sheet(self, lbl, image_name):
    img_path = self.resourcePathEx(f'Image/{image_name}.png')
    style_str = "border-image: url("+img_path +");"              
    lbl.setStyleSheet(style_str)

