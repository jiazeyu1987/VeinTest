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
# UltrasoundControl
#

class UltrasoundControl(ScriptedLoadableModule):

  def __init__(self, parent):
    ScriptedLoadableModule.__init__(self, parent)
    self.parent.title = "UltrasoundControl"  # TODO: make this more human readable by adding spaces
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
# UltrasoundControlWidget
#

class UltrasoundControlWidget(JBaseExtensionWidget):

  def setup(self):
    super().setup()
    self.ui.btn_left.connect('clicked()',self.on_left_click)
    self.ui.btn_right.connect('clicked()',self.on_right_click)
    self.ui.btn_up.connect('clicked()',self.on_up_click)
    self.ui.btn_down.connect('clicked()',self.on_down_click)
    self.ui.btn_left2.connect('clicked()',self.on_left2_click)
    self.ui.btn_right2.connect('clicked()',self.on_right2_click)
    self.ui.btn_left_up.connect('clicked()',self.on_left_up_click)
    self.ui.btn_right_down.connect('clicked()',self.on_right_down_click)
  
  def on_left_click(self):
    print("on_left_click")
    pass
  
  def on_right_click(self):
    pass
  
  def on_up_click(self):
    pass
  
  def on_down_click(self):
    pass
  
  def on_left2_click(self):
    pass
  
  def on_right2_click(self):
    pass
  
  def on_left_up_click(self):
    pass
  
  def on_right_down_click(self):
    pass