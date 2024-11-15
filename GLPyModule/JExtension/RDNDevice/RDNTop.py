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
# RDNTop
#

class RDNTop(ScriptedLoadableModule):

  def __init__(self, parent):
    ScriptedLoadableModule.__init__(self, parent)
    self.parent.title = "RDNTop"  # TODO: make this more human readable by adding spaces
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
# JSegmentAirwayWidget
#

class RDNTopWidget(JBaseExtensionWidget):

  def setup(self):
    super().setup()
    self.ui.tabWidget.tabBar().hide()
    self.ui.btn_close.connect('clicked()',self.on_shutup)
    util.singleShot(100,self.init_later)
  
  def on_shutup(self):
    res = util.messageBox("确定要关闭系统吗",windowTitle="提示")
    if res == 0:
      return
    print("is closing system")
    import subprocess
    subprocess.call('shutdown /s /t 1')
  
  def init_later(self):
    from RDNTool.ConnectInfo import ConnectInfo
    info = ConnectInfo()
    util.addWidget2(self.ui.widget_2,info.uiWidget)
  
  

 