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
from qt import QPoint
import slicer.util as util
import SlicerWizard.Utilities as su 
import numpy as np
from Base.JBaseExtension import JBaseExtensionWidget
#
# JSpeButton
#
class JSpeButton(ScriptedLoadableModule):

  def __init__(self, parent):
    ScriptedLoadableModule.__init__(self, parent)
    self.parent.title = "JSpeButton"  # TODO: make this more human readable by adding spaces
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
# 调用例子
# btn = util.getModuleWidget("JSpeButton")
# util.addWidget2(self.ui.widget_test, btn.uiWidget)
#
class JSpeButtonWidget(JBaseExtensionWidget):
  def setup(self):
    super().setup()
    self.ui.btn.connect('clicked()',self.start_jump)
    self.old_xpos = self.ui.lbl_cover.pos.x()
    self.tick_event = slicer.mrmlScene.AddObserver(util.TickJump, self.tick_jump)

  def start_jump(self):
    util.getModule("Tick").start_thread(1)

  def tick_jump(self,caller,str_event):
    pos = self.ui.lbl_cover.pos
    if pos.x() + 5 > 0:
      util.getModule("Tick").pause_thread()
      self.ui.lbl_cover.move(self.old_xpos, pos.y())
      return
    self.ui.lbl_cover.move(pos.x()+5, pos.y())