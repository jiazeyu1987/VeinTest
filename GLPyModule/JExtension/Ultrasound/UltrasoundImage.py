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
# UltrasoundImage
#

class UltrasoundImage(ScriptedLoadableModule):

  def __init__(self, parent):
    ScriptedLoadableModule.__init__(self, parent)
    self.parent.title = "UltrasoundImage"  # TODO: make this more human readable by adding spaces
    self.parent.categories = ["RDN"]  # TODO: set categories (folders where the module shows up in the module selector)
    self.parent.dependencies = []  # TODO: add here list of module names that this module requires
    self.parent.contributors = ["jia ze yu"]  # TODO: replace with "Firstname Lastname (Organization)"
    # TODO: update with short description of the module and a link to online module documentation
    self.parent.helpText = """

"""
    # TODO: replace with organization, grant and thanks
    self.parent.acknowledgementText = """

"""

class ScreenShotItem:
  ui = None
  view = None
  img_path = ""
  def __init__(self, in_ui, path, in_view) -> None:
    self.ui = in_ui 
    self.img_path = path
    self.view = in_view
    scaled_pixmap = qt.QPixmap(path).scaled(qt.QSize(200, 200), qt.Qt.KeepAspectRatio, qt.Qt.SmoothTransformation)
    self.ui.lbl_image.setAlignment(qt.Qt.AlignLeft)
    self.ui.lbl_image.setPixmap(scaled_pixmap)
    self.ui.btn_delete.connect('clicked()', self.on_delete_click)

  def on_delete_click(self):
    self.view.delete_item_by_path(self.img_path)

class InfoItem:
  ui = None
  line_node = None
  node_name = ""
  def __init__(self, in_ui, node) -> None:
    self.ui = in_ui
    self.line_node = node
    
    self.line_node.AddObserver(slicer.vtkMRMLMarkupsNode.PointEndInteractionEvent, self.onMarkupEndInteraction)
    self.node_name = self.line_node.GetName()
    self.update_display_info()

  def update_display_info(self):
    length = str(self.line_node.GetMeasurement('length').GetValue())
    self.ui.lbl_des.setText(f'{self.node_name}:  {length}')

  def onMarkupEndInteraction(self, caller, event):
    lineNode = caller    
    self.update_display_info()
    pass

#
# UltrasoundImageWidget
#

class UltrasoundImageWidget(JBaseExtensionWidget):
  line_index = 0
  init_once_flag = False
  screen_shot_list = []
  def setup(self):
    super().setup()
    print("UltrasoundImageWidget setup")
    self.logic = UltrasoundImageLogic()
    self.logic.setWidget(self)
    
  def enter(self):
    self.init_once()
    self.addEvent(True)
    
  def init_once(self):
    if self.init_once_flag == True:
      return
    self.init_once_flag = True
    self.ui.tab_measure.tabBar().hide()
    self.ui.btn_measure.setCheckable(True)
    test_file = 'E:/data/CYH/T1/1_0.Dcm'
    loadedVolumeNode = util.loadVolume(test_file)
    loadedVolumeNode.SetAttribute("filepath",test_file)
    loadedVolumeNode2 = util.loadVolume('E:/data/CYH/Flair/1_0.Dcm')
    loadedVolumeNode2.SetAttribute("filepath",'E:/data/CYH/Flair/1_0.Dcm')
    self.init_defaut_value()
    self.ui.tabWidget.setCurrentIndex(0)
    self.ui.list_screen_shot.setSpacing(0)
    slicer.app.layoutManager().sliceWidget("Red").sliceController().setVisible(False)
    slicer.app.layoutManager().sliceWidget("Green").sliceController().setVisible(False)
    self.show_volume_in_different_window(loadedVolumeNode.GetID(), loadedVolumeNode2.GetID())
    pass

  def show_volume_in_different_window(self, node_id1, node_id2):
    sliceCompositeNodes = slicer.util.getNodesByClass("vtkMRMLSliceCompositeNode")
    for sliceCompositeNode in sliceCompositeNodes:
      sliceCompositeNode.SetLinkedControl(False)
    layoutManager = slicer.app.layoutManager()
    layoutManager.sliceWidget("Red").mrmlSliceCompositeNode().SetBackgroundVolumeID(node_id1)
    layoutManager.sliceWidget("Yellow").mrmlSliceCompositeNode().SetBackgroundVolumeID(node_id2)
    layoutManager = slicer.app.layoutManager()
    if layoutManager is not None:
      sliceLogics = layoutManager.mrmlSliceLogics()
      for i in range(sliceLogics.GetNumberOfItems()):
        sliceLogic = sliceLogics.GetItemAsObject(i)
        if sliceLogic:
          sliceLogic.FitSliceToAll()

  def exit(self):    
    self.addEvent(False)

  def addEvent(self,bool_val):
    self.add_button_event("btn_auto_tgc", 'clicked()', self.on_click_auto_tgc, bool_val)
    self.add_button_event("btn_compound", 'clicked()', self.on_click_compound, bool_val)
    self.add_button_event("btn_harmonic", 'clicked()', self.on_click_harmonic, bool_val)
    self.add_button_event("btn_hand", 'clicked()', self.on_click_hand, bool_val)
    self.add_button_event("btn_vtu", 'clicked()', self.on_click_vtu, bool_val)


    self.add_button_event("btn_stop_doppler", 'clicked()', self.on_click_stop_doppler, bool_val)


    self.add_button_event("btn_clear", 'clicked()', self.on_click_clear, bool_val)
    self.add_button_event("btn_save", 'clicked()', self.on_click_save, bool_val)

    self.add_button_event("btn_measure", 'toggled(bool)', self.on_toggle_measure, bool_val)
    self.add_button_event("tabWidget", 'currentChanged(int)', self.on_tab_current_change, bool_val)

    self.add_button_event("widget_gain", 'onValueChange(int)', self.on_gain_value_change, bool_val)
    self.add_button_event("widget_color", 'onValueChange(int)', self.on_color_value_change, bool_val)
    self.add_button_event("widget_angle", 'onValueChange(int)', self.on_angle_value_change, bool_val)
    pass

  def add_button_event(self, btn_name, operate_type, callback_func, is_connect):
    if hasattr(self.ui, btn_name) == False:
      return
    button = getattr(self.ui, btn_name)
    if is_connect == True:
      button.connect(operate_type, callback_func)
    else:
      button.disconnect(operate_type, callback_func)   
  
  def init_defaut_value(self):
    self.ui.widget_angle.SetWidgetValue(12.5, 1.5, 30, 5, "偏转 %1°")
    self.ui.widget_color.SetWidgetValue(12.5, 1.5, 30, 5, "色彩增益 %1%")
    self.ui.widget_gain.SetWidgetValue(12.5, 1.5, 30, 5, "增益 %1%")

  def on_angle_value_change(self, value):
    print('on_angle_value_change', value)

  def on_color_value_change(self, value):
    print('on_color_value_change', value)

  def on_gain_value_change(self, value):
    print('on_gain_value_change', value)

  def on_click_auto_tgc(self):
    pass
  
  def on_click_compound(self):
    pass
  
  def on_click_harmonic(self):
    pass
    
  def on_click_hand(self):
    pass
  
  def on_click_vtu(self):
    pass
    
  def on_click_stop_doppler(self):
    pass
  
  def on_click_clear(self):
    self.ui.btn_measure.setChecked(False)
    self.logic.clear_all_line_nodes()
    self.ui.list_measure.clear()
    pass
  
  def on_click_save(self):
    filename = f'{util.getScreenCapturePath()}/{qt.QDateTime().currentDateTime().toString("yyyyMMddhhmmss")}.png'
    print("on_click_save", filename)

    # Set view background to white
    view = slicer.app.layoutManager().sliceWidget('Red').sliceView()

    # Capture a screenshot
    import ScreenCapture
    cap = ScreenCapture.ScreenCaptureLogic()
    cap.captureImageFromView(view, filename)

    width_of_list = self.ui.list_screen_shot.width
    template1 = slicer.util.loadUI(self.resourcePath("UI/ScreenShotItem.ui"))
    template1ui = slicer.util.childWidgetVariables(template1)
    template = ScreenShotItem(template1ui, filename, self)
    item = qt.QListWidgetItem(self.ui.list_screen_shot)
    item.setSizeHint(qt.QSize(width_of_list-50, 200))
    self.ui.list_screen_shot.setItemWidget(item, template1)
    self.ui.list_screen_shot.addItem(item)
    self.screen_shot_list.append(filename)
    pass  
  
  def on_toggle_measure(self, is_show):
    logic = util.getModuleLogic("Markups")
    if is_show:
      slicer.app.applicationLogic().GetInteractionNode().SetPlaceModePersistence(0)
      lineNode = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLMarkupsLineNode", "line")
      lineNode.SetAttribute("is_measure","1")
      lineNode.CreateDefaultDisplayNodes()
      logic.SetActiveList(lineNode)
      lineNode.GetMeasurement('length').SetEnabled(True)
      slicer.app.applicationLogic().GetInteractionNode().SetCurrentInteractionMode(slicer.vtkMRMLInteractionNode.Place)
      lineNode.AddObserver(slicer.vtkMRMLMarkupsNode.PointPositionDefinedEvent, self.onMarkupDefine)
      self.logic.line_node_list.append(lineNode)
    else:
      self.measure_flag = False
      slicer.app.applicationLogic().GetInteractionNode().SetCurrentInteractionMode(2)
    pass
  

  def onMarkupDefine(self, caller, event):
    lineNode = caller
    length = lineNode.GetMeasurement('length').GetValue()
    if length == 0:
      return
    self.ui.tab_measure.setCurrentIndex(1)
    template1 = slicer.util.loadUI(self.resourcePath("UI/InfoItem.ui"))
    template1ui = slicer.util.childWidgetVariables(template1)
    template = InfoItem(template1ui, lineNode)
    item = qt.QListWidgetItem(self.ui.list_measure)
    item.setSizeHint(qt.QSize(200, 50))
    self.ui.list_measure.setItemWidget(item, template1)
    self.ui.list_measure.addItem(item)
    print("onMarkupChanged", length)
    pass

  def on_tab_current_change(self, tab_no):
    title_info = ""
    if tab_no == 2:
      title_info = "长度测量"
    self.ui.lbl_title2.setText(title_info)

  def delete_item_by_path(self, path):
    index_to_remove = self.screen_shot_list.index(path)
    self.screen_shot_list.pop(index_to_remove)
    self.ui.list_screen_shot.takeItem(index_to_remove)
    pass


class UltrasoundImageLogic(ScriptedLoadableModuleLogic):
  m_Node = None
  line_node_list = []
  logic = None
  def __init__(self):
    """
    Called when the logic class is instantiated. Can be used for initializing member variables.
    """
    ScriptedLoadableModuleLogic.__init__(self)
    slicer.mrmlScene.AddObserver(slicer.vtkMRMLScene.NodeAddedEvent, self.onNodeAdded)
    self.logic = util.getModuleLogic("Markups")

  def setWidget(self,widget):
    self.m_Widget = widget

  @vtk.calldata_type(vtk.VTK_OBJECT)
  def onNodeAdded(self,caller, event, calldata):
    node = calldata
    print("onNodeAdded", node.GetName())
    #if isinstance(node, slicer.vtkMRMLMarkupsFiducialNode):
      #self.m_Widget.on_node_added(node)

  @vtk.calldata_type(vtk.VTK_OBJECT)
  def onNodeRemove(self,caller, event, calldata):
    node = calldata
    print("onNodeRemove", node.GetName())

  def clear_all_line_nodes(self):
    for i in range(len(self.line_node_list)):
      node = self.line_node_list[i]
      print("clear_all_line_nodes", node.GetName())
      display_node = node.GetDisplayNode()
      slicer.mrmlScene.RemoveNode(display_node)
      node.RemoveAllObservers()
      slicer.mrmlScene.RemoveNode(node)


