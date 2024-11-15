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
# UltrasoundPositioning
#

class UltrasoundPositioning(ScriptedLoadableModule):

  def __init__(self, parent):
    ScriptedLoadableModule.__init__(self, parent)
    self.parent.title = "UltrasoundPositioning"  # TODO: make this more human readable by adding spaces
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
# UltrasoundPositioningWidget
#

class UltrasoundPositioningWidget(JBaseExtensionWidget):
  init_once_flag = False
  def setup(self):
    super().setup()
    print("UltrasoundPositioningWidget setup")
    
  def enter(self):
    self.init_once()
    self.addEvent(True)
    self.init_setting()
    
  def init_once(self):
    if self.init_once_flag == True:
      return
    self.init_once_flag = True
    util.getModuleWidget("UltrasoundSetting").set_pressure_range(1, 10, 12, 20)
    util.singleShot(10,self.init_later)
    util.getModuleWidget("UltrasoundSetting").set_current_pressure_value(15.2)
    pass

  def init_setting(self):    
    widget = util.getModuleWidget("UltrasoundSetting").ui.tabWidget
    util.addWidget2(self.ui.widget_setting, widget)
    util.getModuleWidget("UltrasoundSetting").hide_top_view()

  def init_later(self):
    pass

  def exit(self):    
    self.addEvent(False)

  def addEvent(self,bool_val):
    util.getModuleWidget("UltrasoundSetting").addEvent(bool_val)
    pass

  def add_button_event(self, btn_name, operate_type, callback_func, is_connect):
    if hasattr(self.ui, btn_name) == False:
      return
    button = getattr(self.ui, btn_name)
    if is_connect == True:
      button.connect(operate_type, callback_func)
    else:
      button.disconnect(operate_type, callback_func)   
  
  