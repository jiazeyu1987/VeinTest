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
# UltrasoundEpack
#

class EpackItem:
  ui = None
  def __init__(self, in_ui, des, content) -> None:
    self.ui = in_ui
    self.ui.lbl_info.setText(des) 
    self.ui.lbl_content.setText(content)  
    self.ui.lbl_content.wordWrap = True
    self.ui.lbl_content.hide() 
    
    if content == "":
      self.ui.btn_detail.hide()
    self.ui.btn_detail.connect('toggled(bool)', self.on_detail_click)
  
  def on_detail_click(self, state):
    if state:
      self.ui.lbl_content.show()
    else:
      self.ui.lbl_content.hide()
    
class UltrasoundEpack(ScriptedLoadableModule):

  def __init__(self, parent):
    ScriptedLoadableModule.__init__(self, parent)
    self.parent.title = "UltrasoundEpack"  # TODO: make this more human readable by adding spaces
    self.parent.categories = ["RDN"]  # TODO: set categories (folders where the module shows up in the module selector)
    self.parent.dependencies = []  # TODO: add here list of module names that this module requires
    self.parent.contributors = ["jia ze yu"]  # TODO: replace with "Firstname Lastname (Organization)"
    # TODO: update with short description of the module and a link to online module documentation
    self.parent.helpText = """

"""
    # TODO: replace with organization, grant and thanks
    self.parent.acknowledgementText = """

"""

class UltrasoundEpackWidget(JBaseExtensionWidget):
  init_once_flag = False
  title_list = ['1. 萨芬撒地方撒旦法师打发斯蒂芬', '2. 阿斯顿发送到发送到发送到发斯蒂芬', '3. ad发顺丰达是打发士大夫撒阿斯顿发送到', '2. 阿斯顿发送到发送到发送到发斯蒂芬', '3. ad发顺丰达是打发士大夫撒阿斯顿发送到', '2. 阿斯顿发送到发送到发送到发斯蒂芬', '3. ad发顺丰达是打发士大夫撒阿斯顿发送到', '2. 阿斯顿发送到发送到发送到发斯蒂芬', '3. ad发顺丰达是打发士大夫撒阿斯顿发送到']
  content_list = ['', '', '萨芬撒地方撒旦法师打发斯蒂芬萨芬撒地方撒旦法师打发斯蒂芬萨芬撒地方撒旦法师打发斯蒂芬萨芬撒地方撒旦法师打发斯蒂芬萨芬撒地方撒旦法师打发斯蒂芬萨芬撒地方撒旦法师打发斯蒂芬', '', '萨芬撒地方撒旦法师打发斯蒂芬萨芬撒地方撒旦法师打发斯蒂芬萨芬撒地方撒旦法师打发斯蒂芬萨芬撒地方撒旦法师打发斯蒂芬萨芬撒地方撒旦法师打发斯蒂芬萨芬撒地方撒旦法师打发斯蒂芬萨芬撒地方撒旦法师打发斯蒂芬萨芬撒地方撒旦法师打发斯蒂芬萨芬撒地方撒旦法师打发斯蒂芬萨芬撒地方撒旦法师打发斯蒂芬萨芬撒地方撒旦法师打发斯蒂芬萨芬撒地方撒旦法师打发斯蒂芬萨芬撒地方撒旦法师打发斯蒂芬', '', '萨芬撒地方撒旦法师打发斯蒂芬萨芬撒地方撒旦法师打发斯蒂芬萨芬撒地方撒旦法师打发斯蒂芬萨芬撒地方撒旦法师打发斯蒂芬萨芬撒地方撒旦法师打发斯蒂芬萨芬撒地方撒旦法师打发斯蒂芬', '', '萨芬撒地方撒旦法师打发斯蒂芬萨芬撒地方撒旦法师打发斯蒂芬萨芬撒地方撒旦法师打发斯蒂芬萨芬撒地方撒旦法师打发斯蒂芬萨芬撒地方撒旦法师打发斯蒂芬萨芬撒地方撒旦法师打发斯蒂芬萨芬撒地方撒旦法师打发斯蒂芬萨芬撒地方撒旦法师打发斯蒂芬萨芬撒地方撒旦法师打发斯蒂芬萨芬撒地方撒旦法师打发斯蒂芬萨芬撒地方撒旦法师打发斯蒂芬萨芬撒地方撒旦法师打发斯蒂芬萨芬撒地方撒旦法师打发斯蒂芬']
  def setup(self):
    super().setup()
    print("UltrasoundEpackWidget setup")

  def enter(self):
    self.init_once()
    self.addEvent(True)    
    util.save_global_value("arm_pack", True)
    
  def init_once(self):
    if self.init_once_flag == True:
      return
    self.init_once_flag = True
    print("init_once")
    self.set_label_style_sheet(self.ui.lbl_bg, "1")
    util.singleShot(10,self.init_later)

  def init_later(self):
    self.init_epack_list()
    pass

  def init_epack_list(self):
    for i in range(len(self.title_list)):
      template1 = slicer.util.loadUI(self.resourcePath("UI/EpackItem.ui"))
      template1ui = slicer.util.childWidgetVariables(template1)
      template = EpackItem(template1ui, self.title_list[i], self.content_list[i])
      util.addWidget2(self.ui.widget_content, template1)
    self.ui.widget_content.layout().addStretch(1)

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

