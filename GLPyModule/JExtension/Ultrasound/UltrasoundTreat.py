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
# UltrasoundTreat
#

class UltrasoundTreat(ScriptedLoadableModule):

  def __init__(self, parent):
    ScriptedLoadableModule.__init__(self, parent)
    self.parent.title = "UltrasoundTreat"  # TODO: make this more human readable by adding spaces
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
# UltrasoundTreatWidget
#

class UltrasoundTreatWidget(JBaseExtensionWidget):
  old_xpos = 0
  init_once_flag = False
  widget_control = None
  treate_target_point = None
  def setup(self):
    super().setup()
    print("UltrasoundTreatWidget setup")

  def enter(self):
    self.init_once()
    self.init_control()
    self.addEvent(True)
    self.init_setting()
    if self.widget_control:
      self.widget_control.show()

  def init_setting(self):    
    widget = util.getModuleWidget("UltrasoundSetting").ui.tabWidget
    util.addWidget2(self.ui.widget_setting, widget)
    util.getModuleWidget("UltrasoundSetting").insert_top_view()

  def init_once(self):
    if self.init_once_flag == True:
      return
    self.init_once_flag = True
    print("init_once")
    self.widget_control = qt.QWidget()
    util.singleShot(10,self.init_later)
    self.ui.btn_change_view.setCheckable(True)
    self.ui.btn_change_view.hide()
    self.ui.btn_target.setCheckable(True)

  def init_control(self):
    widget = util.getModuleWidget("UltrasoundControl").ui.widget
    slice_widget = slicer.app.layoutManager().sliceWidget("Red")
    self.widget_control.setParent(slice_widget)
    util.addWidget2(self.widget_control,widget)    
    self.widget_control.show()
    util.singleShot(10,self.reset_control_geometry)

  def reset_control_geometry(self):
    slice_widget = slicer.app.layoutManager().sliceWidget("Red")
    slice_widget_height = slice_widget.height
    self.widget_control.geometry = qt.QRect(8, slice_widget_height-200, 404, 192)

  def init_later(self):
    width_of_progress = self.ui.widget_progress.width
    width_of_bg1 = width_of_progress * 6 / 7
    width_of_bg2 = width_of_progress - width_of_bg1
    
    height_of_progress = self.ui.widget_progress.height
    self.ui.lbl_bg1.setFixedSize(qt.QSize(width_of_bg1 , height_of_progress))
    self.ui.lbl_bg2.setFixedSize(qt.QSize(width_of_bg2 , height_of_progress))
    self.ui.lbl_cover.setFixedSize(qt.QSize(width_of_progress , height_of_progress))
    self.ui.lbl_bg1.move(0, 0)
    self.ui.lbl_bg2.move(width_of_bg1, 0)
    self.ui.lbl_cover.move(-width_of_progress, 0)
    self.old_xpos = -width_of_progress
    print("init_once2",width_of_progress)
    pass

  def exit(self):    
    self.addEvent(False)
    if self.widget_control:
      self.widget_control.hide()

  def addEvent(self,bool_val):
    util.getModuleWidget("UltrasoundSetting").addEvent(bool_val)
    self.add_button_event("btn_clear", 'clicked()', self.on_target_point_clear, bool_val)   
    self.add_button_event("btn_target", 'toggled(bool)', self.on_target_point_add, bool_val)
    self.add_button_event("btn_change_view", 'toggled(bool)', self.on_click_change_view, bool_val)
    self.add_button_event("btn_color", 'toggled(bool)', self.on_click_color, bool_val)
    if bool_val:
      self.TagMaps[util.UltrasoundStartTreat] = slicer.mrmlScene.AddObserver(util.UltrasoundStartTreat, self.start_treat)
    else:
      slicer.mrmlScene.RemoveObserver(self.TagMaps[util.UltrasoundStartTreat])
    pass

  def add_button_event(self, btn_name, operate_type, callback_func, is_connect):
    if hasattr(self.ui, btn_name) == False:
      return
    button = getattr(self.ui, btn_name)
    if is_connect == True:
      button.connect(operate_type, callback_func)
    else:
      button.disconnect(operate_type, callback_func)  

  def on_target_point_add(self, state):
    if not self.treate_target_point:
      treate_target_point = util.getFirstNodeByClassByAttribute(util.vtkMRMLMarkupsFiducialNode,"treate_target_node","1")
      if not treate_target_point:      
        treate_target_point = util.AddNewNodeByClass("vtkMRMLMarkupsFiducialNode")
        treate_target_point.SetAttribute("treate_target_node","1")
        treate_target_point.AddObserver(slicer.vtkMRMLMarkupsNode.PointPositionDefinedEvent, self.on_point_defined)
        treate_target_point.AddObserver(slicer.vtkMRMLMarkupsNode.PointEndInteractionEvent, self.on_point_modified)
        treate_target_point.AddObserver(slicer.vtkMRMLMarkupsNode.PointRemovedEvent, self.on_point_remove)
      self.treate_target_point = treate_target_point
          
      display_node = util.GetDisplayNode(self.treate_target_point)
      display_node.SetPointLabelsVisibility(False)
      display_node.SetGlyphTypeFromString("Circle2D")
      display_node.SetGlyphScale(10)
    interactionNode = slicer.app.applicationLogic().GetInteractionNode()
    interactionNode.SetPlaceModePersistence(1)
    selectionNode = slicer.app.applicationLogic().GetSelectionNode()
    selectionNode.SetReferenceActivePlaceNodeClassName("vtkMRMLMarkupsFiducialNode")
    selectionNode.SetActivePlaceNodeID(self.treate_target_point.GetID())
    if state:
      interactionNode.SetCurrentInteractionMode(interactionNode.Place)
    else:
      interactionNode.SetCurrentInteractionMode(interactionNode.ViewTransform)
  
  def on_point_defined(self, observer, eventid):
    print("on_point_defined")
    #self.ui.btn_target.setChecked(False)
    self.print_control_points()
    pass

  def on_point_modified(self, observer, eventid):
    print("on_point_modified")
    self.print_control_points()
    pass

  def on_point_remove(self, observer, eventid):
    print("on_point_remove")
    self.print_control_points()
    pass

  def print_control_points(self):
    if not self.treate_target_point:
      return
    num_of_control_point = self.treate_target_point.GetNumberOfControlPoints()
    for i in range(num_of_control_point):
      ras = vtk.vtkVector3d(0, 0, 0)
      self.treate_target_point.GetNthControlPointPosition(i, ras)
      print(i, ":", ras)

  def on_target_point_clear(self):
    if self.treate_target_point:    
      util.RemoveNode(self.treate_target_point) 
      self.treate_target_point = None
    pass

  def on_click_color(self):
    self.start_animation()
    pass
  
  def on_click_compound(self):
    pass
  
  def on_click_harmonic(self):
    pass
  
  def on_click_hand(self):
    pass
  
  def on_click_vtu(self):
    self.start_animation()
    pass
  
  def on_click_change_view(self, is_double):
    layoutManager = slicer.app.layoutManager()
    layout_id = 518
    if is_double:
      layout_id = 519
    layoutManager.setLayout(layout_id)
    util.singleShot(10,self.reset_control_geometry)
    pass

  def start_animation(self):    
    print('start_animation')
    self.ui.lbl_cover.move(self.old_xpos, 0)
    util.start_move_animation(self.ui.lbl_cover, self.ui.widget_progress, 2000, qt.QPoint(self.old_xpos, 0), qt.QPoint(0, 0), self.animation_end)

  def animation_end(self):
    print("animation_end")
    self.ui.lbl_cover.move(self.old_xpos, 0)

  @vtk.calldata_type(vtk.VTK_OBJECT)
  def start_treat(self,caller,str_event,calldata):
    self.start_animation()
    