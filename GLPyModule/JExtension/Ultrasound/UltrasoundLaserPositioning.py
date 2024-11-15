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
# UltrasoundLaserPositioning
#

class UltrasoundLaserPositioning(ScriptedLoadableModule):

  def __init__(self, parent):
    ScriptedLoadableModule.__init__(self, parent)
    self.parent.title = "UltrasoundLaserPositioning"  # TODO: make this more human readable by adding spaces
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
# UltrasoundLaserPositioningWidget
#

class UltrasoundLaserPositioningWidget(JBaseExtensionWidget):
  timer = None
  check_sequence = ['robot','ndi']
  check_index = 0
  check_map = {}
  old_waring_txt = ""
  warning_label = None
  def setup(self):
    super().setup()
    print("UltrasoundLaserPositioningWidget setup")
    bg_img = self.resourcePathEx('Image/info.png')
    style_str = "border-image: url("+bg_img +");"                     
    self.ui.lbl_info.setStyleSheet(style_str)