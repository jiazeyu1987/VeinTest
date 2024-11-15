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
# UltrasoundBottom
#

class UltrasoundBottom(ScriptedLoadableModule):

  def __init__(self, parent):
    ScriptedLoadableModule.__init__(self, parent)
    self.parent.title = "UltrasoundBottom"  # TODO: make this more human readable by adding spaces
    self.parent.categories = ["RDN"]  # TODO: set categories (folders where the module shows up in the module selector)
    self.parent.dependencies = []  # TODO: add here list of module names that this module requires
    self.parent.contributors = ["jia ze yu"]  # TODO: replace with "Firstname Lastname (Organization)"
    # TODO: update with short description of the module and a link to online module documentation
    self.parent.helpText = """

"""
    # TODO: replace with organization, grant and thanks
    self.parent.acknowledgementText = """

"""



#
# UltrasoundBottomWidget
#

class UltrasoundBottomWidget(JBaseExtensionWidget):
  init_once_flag = False
  def setup(self):
    super().setup()
    print("UltrasoundBottomWidget setup")
    util.layout_panel("middle_left").connect('moduleAdded(QString)',self.onModuleAdded)

  def onModuleAdded(self,module_name):
    print("UltrasoundBottom onModuleAdded2",module_name)
    self.ui.btn_pre.hide()
    self.ui.btn_next.hide()
    self.ui.btn_patient.hide()
    if module_name == "UltrasoundPositioning":
      self.ui.btn_pre.setText("< 超声检查")
      self.ui.btn_pre.show()
    elif module_name == "UltrasoundLaserPositioning":
      self.module_index = 3
      self.ui.btn_pre.setText("< 定位")
      self.ui.btn_pre.show()
    elif module_name == "UltrasoundEpack" or module_name == "UltrasoundWater" or module_name == "UltrasoundBalloon":
      self.ui.btn_patient.show()
      pass
    elif module_name == "JPCCS":
      self.ui.btn_pre.setText("< 返回登录")
      self.ui.btn_pre.show()
    else:
      pass

  def enter(self):
    self.init_once()
    self.addEvent(True)
    
  def init_once(self):
    if self.init_once_flag == True:
      return
    self.init_once_flag = True
    pass

  def exit(self):    
    self.addEvent(False)

  def addEvent(self,bool_val):
    self.add_button_event("btn_next", 'clicked()', self.on_next_click, bool_val)
    self.add_button_event("btn_pre", 'clicked()', self.on_pre_click, bool_val)
    self.add_button_event("btn_patient", 'clicked()', self.on_patient_click, bool_val)
    pass

  def on_next_click(self):
    util.send_event_str(util.GotoNextPage)

  def on_pre_click(self):
    util.send_event_str(util.GotoLastPage)

  def on_patient_click(self):
    util.send_event_str(util.SetPage, 3)

  def add_button_event(self, btn_name, operate_type, callback_func, is_connect):
    if hasattr(self.ui, btn_name) == False:
      return
    button = getattr(self.ui, btn_name)
    if is_connect == True:
      button.connect(operate_type, callback_func)
    else:
      button.disconnect(operate_type, callback_func)    