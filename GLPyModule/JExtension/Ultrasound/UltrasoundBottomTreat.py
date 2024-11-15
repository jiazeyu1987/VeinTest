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
# UltrasoundBottomTreat
#

class UltrasoundBottomTreat(ScriptedLoadableModule):

  def __init__(self, parent):
    ScriptedLoadableModule.__init__(self, parent)
    self.parent.title = "UltrasoundBottomTreat"  # TODO: make this more human readable by adding spaces
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
# UltrasoundBottomTreatWidget
#

class UltrasoundBottomTreatWidget(JBaseExtensionWidget):
  init_once_flag = False
  def setup(self):
    super().setup()
    print("UltrasoundBottomTreatWidget setup")

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
    self.add_button_event('btn_pulse', 'clicked()', self.treat_start, bool_val)
    pass

  def treat_start(self):
    util.send_event_str(util.UltrasoundStartTreat, "1")

  def add_button_event(self, btn_name, operate_type, callback_func, is_connect):
    if hasattr(self.ui, btn_name) == False:
      return
    button = getattr(self.ui, btn_name)
    if is_connect == True:
      button.connect(operate_type, callback_func)
    else:
      button.disconnect(operate_type, callback_func)    