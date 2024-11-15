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
#
# JBaseDump
#

class JBaseDump(ScriptedLoadableModule):

  def __init__(self, parent):
    ScriptedLoadableModule.__init__(self, parent)
    self.parent.title = "JBaseDump"  # TODO: make this more human readable by adding spaces
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
# JBaseDumpWidget
#

class JBaseDumpWidget(ScriptedLoadableModuleWidget, VTKObservationMixin):
  TagMaps = {}
  def __init__(self, parent=None):
    """
    Called when the user opens the module the first time and the widget is initialized.
    """
    ScriptedLoadableModuleWidget.__init__(self, parent)
    VTKObservationMixin.__init__(self)  # needed for parameter node observation
    self.logic = None

  def setup(self):
    """
    Called when the user opens the module the first time and the widget is initialized.
    """
    ScriptedLoadableModuleWidget.setup(self)

    # Load widget from .ui file (created by Qt Designer).
    # Additional widgets can be instantiated manually and added to self.layout.
    self.logic = JBaseDumpLogic()
    self.logic.setWidget(self)

    
    
    uiWidget = slicer.util.loadUI(self.resourcePath('UI/JBaseDump.ui'))
    self.layout.addWidget(uiWidget)
    self.ui = slicer.util.childWidgetVariables(uiWidget)
    
   
    uiWidget.setMRMLScene(slicer.mrmlScene)
    
    
    

    self.init_ui()
  


  def enter(self):
    self.addEvent(True)

  def exit(self):
    self.addEvent(False)


  def addEvent(self,bool_val):
    if bool_val:
      print("addEvent JAddFiber")
      self.TagMaps[util.MainNodeLoadedEvent] = slicer.mrmlScene.AddObserver(util.MainNodeLoadedEvent, self.OnMainNodeAdded)
      self.TagMaps[util.MainNodeRemovedEvent] = slicer.mrmlScene.AddObserver(util.MainNodeRemovedEvent, self.OnMainNodeRemoved)
      self.TagMaps[util.ArchiveFileLoadedEvent] = slicer.mrmlScene.AddObserver(util.ArchiveFileLoadedEvent, self.OnArchiveLoaded)
      self.TagMaps[util.SceneDestroyEvent] = slicer.mrmlScene.AddObserver(util.SceneDestroyEvent, self.OnSceneDestroyEvent)
      self.ui.btnReload.connect('clicked()', self.onReload)
    else:
      print("removeEvent JAddFiber")
      slicer.mrmlScene.RemoveObserver(self.TagMaps[util.MainNodeLoadedEvent])
      slicer.mrmlScene.RemoveObserver(self.TagMaps[util.MainNodeRemovedEvent])
      slicer.mrmlScene.RemoveObserver(self.TagMaps[util.ArchiveFileLoadedEvent])
      slicer.mrmlScene.RemoveObserver(self.TagMaps[util.SceneDestroyEvent])
      self.ui.btnReload.disconnect('clicked()', self.onReload)
  
  '''
    当有新的ScalarVolumeNode添加的时候,恢复初始设置
  '''
  @vtk.calldata_type(vtk.VTK_OBJECT)
  def OnMainNodeAdded(self,caller,str_event,calldata):
    self.logic.m_Node = calldata  
    if self.logic.m_Node:
      util.SetGlobalSaveValue("JBaseDump_MainNodeID",self.logic.m_Node.GetID())
  
  '''
    当原有的ScalarVolumeNode删除的时候,删除所有的标签
  '''
  @vtk.calldata_type(vtk.VTK_OBJECT)
  def OnMainNodeRemoved(self,caller,str_event,calldata):
    self.logic.m_Node = None  
    util.SetGlobalSaveValue("JBaseDump_MainNodeID",None)


  def OnSceneDestroyEvent(self,_a,_b):
    print("JBaseDump do not need destroy")
  
  def OnArchiveLoaded(self,_a,_b):
    nodeid = util.GetGlobalSaveValue("JBaseDump_MainNodeID")
    print("OnArchiveLoaded JBaseDump main nodeid is",nodeid)
    if nodeid is None:
      return
    node = util.GetNodeByID(nodeid)
    self.logic.m_Node = node  

  def init_ui(self):
    pass


  
  

  
  

class JBaseDumpLogic(ScriptedLoadableModuleLogic):
  m_Node = None
  def __init__(self):
    """
    Called when the logic class is instantiated. Can be used for initializing member variables.
    """
    ScriptedLoadableModuleLogic.__init__(self)
    slicer.mrmlScene.AddObserver(slicer.vtkMRMLScene.NodeAddedEvent, self.onNodeAdded)
  

  def setWidget(self,widget):
    self.m_Widget = widget

  @vtk.calldata_type(vtk.VTK_OBJECT)
  def onNodeAdded(self,caller, event, calldata):
    node = calldata
    #if isinstance(node, slicer.vtkMRMLMarkupsFiducialNode):
      #self.m_Widget.on_node_added(node)


 