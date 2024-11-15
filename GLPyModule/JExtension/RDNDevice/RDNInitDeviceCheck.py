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
# RDNInitDeviceCheck
#

class RDNInitDeviceCheck(ScriptedLoadableModule):

  def __init__(self, parent):
    ScriptedLoadableModule.__init__(self, parent)
    self.parent.title = "RDNInitDeviceCheck"  # TODO: make this more human readable by adding spaces
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

class RDNInitDeviceCheckWidget(JBaseExtensionWidget):

  def setup(self):
    super().setup()
    self.ui.tabWidget.tabBar().hide()
    self.ui.pushButton.connect('clicked()',self.on_next)
    util.singleShot(100,self.init_later)
  
  def init_later(self):
    import SampleData

  
  def on_next(self):
    util.send_event_str(util.GotoNextPage)
  
  

 