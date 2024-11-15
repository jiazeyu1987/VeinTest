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
# UltrasoundSetting
#

class LineItem:
  ui = None
  index = 0
  def __init__(self, in_ui, in_index):
    self.ui = in_ui
    self.index = in_index
    self.set_select_state(False)

  def set_select_state(self, is_select):
    if is_select == True:
      self.ui.lbl_line.setStyleSheet("background-color: rgb(12, 44, 255);")
    else:
      self.ui.lbl_line.setStyleSheet("background-color: rgb(255, 255, 255);")

class UltrasoundSetting(ScriptedLoadableModule):

  def __init__(self, parent):
    ScriptedLoadableModule.__init__(self, parent)
    self.parent.title = "UltrasoundSetting"  # TODO: make this more human readable by adding spaces
    self.parent.categories = ["RDN"]  # TODO: set categories (folders where the module shows up in the module selector)
    self.parent.dependencies = []  # TODO: add here list of module names that this module requires
    self.parent.contributors = ["jia ze yu"]  # TODO: replace with "Firstname Lastname (Organization)"
    # TODO: update with short description of the module and a link to online module documentation
    self.parent.helpText = """

"""
    # TODO: replace with organization, grant and thanks
    self.parent.acknowledgementText = """

"""

class WidgetEventFilter(qt.QObject):
  view = None
  events = [
    qt.QEvent.MouseButtonPress,
  ]

  def __init__(self):
    qt.QObject.__init__(self)

  def eventFilter(self, object, event):
    if event.type() in self.events:
      self.view.update_mark_pos(event.pos())
    return False

  def setView(self, view):
    self.view = view
#
# UltrasoundSettingWidget
#

class UltrasoundSettingWidget(JBaseExtensionWidget):
  init_once_flag = False
  event_filter = None
  inter = 40
  total_num = 0
  treat_view = None
  select_line = None
  lines_list = []
  lines_ui_list = []
  def setup(self):
    super().setup()
    print("UltrasoundSettingWidget setup")
    self.init_once()
    
  def init_once(self):
    if self.init_once_flag == True:
      return
    self.init_once_flag = True
    self.ui.tabWidget.setCurrentIndex(0)
    self.treat_view = self.ui.tabWidget.widget(0)
    self.ui.widget_angle.SetWidgetValue(12.5, 1.5, 30, 5, "偏转 %1°")
    self.ui.widget_color.SetWidgetValue(12.5, 1.5, 30, 5, "色彩增益 %1%")
    self.ui.widget_gain.SetWidgetValue(12.5, 1.5, 30, 5, "增益 %1%")
    #self.ui.widget_line.setAttribute(qt.Qt.WA_TransparentForMouseEvents, True)
    self.init_lines_widget(30)
    pass

  def init_lines_widget(self, num):
    self.total_num = num
    self.ui.widget_line.setFixedSize(qt.QSize(380, num * self.inter))
    for i in range(num):
      template1 = slicer.util.loadUI(self.resourcePath("UI/LineItem.ui"))
      template1ui = slicer.util.childWidgetVariables(template1)
      template = LineItem(template1ui, i)
      util.addWidget(self.ui.widget_line, template1, 0, i * self.inter)    
      self.lines_list.append(template)
      self.lines_ui_list.append(template1)
    
    self.event_filter = WidgetEventFilter()
    self.event_filter.setView(self)
    self.ui.widget_line.installEventFilter(self.event_filter)
    target_pos = self.get_target_pos(5)
    self.ui.lbl_bar.move(target_pos)
    pass

  def addEvent(self,bool_val):
    self.add_button_event("btn_auto_tgc", 'clicked()', self.on_click_auto_tgc, bool_val)
    self.add_button_event("btn_compound", 'clicked()', self.on_click_compound, bool_val)
    self.add_button_event("btn_harmonic", 'clicked()', self.on_click_harmonic, bool_val)
    self.add_button_event("btn_hand", 'clicked()', self.on_click_hand, bool_val)
    self.add_button_event("btn_vtu", 'clicked()', self.on_click_vtu, bool_val)

    self.add_button_event("slider_low", 'valueChanged(int)', self.pressure_low_value_change, bool_val)
    self.add_button_event("slider_high", 'valueChanged(int)', self.pressure_high_value_change, bool_val)

    self.add_button_event("widget_gain", 'onValueChange(int)', self.on_gain_value_change, bool_val)
    pass

  def clear_line_list(self):
    for ui in self.lines_ui_list:
      util.removeFromParent2(ui)

    self.lines_ui_list.clear()
    self.lines_list.clear()
    self.select_line = None

  def update_mark_pos(self, pos):
    posy = pos.y()
    num = int(posy / self.inter)
    if num >= self.total_num:
      num = self.total_num - 1
    if self.select_line:
      self.select_line.set_select_state(False)
    self.select_line = self.lines_list[num]
    self.select_line.set_select_state(True)
    target_pos = self.get_target_pos(num)
    util.start_move_animation(self.ui.lbl_bar, self.ui.widget_line, 1000, self.ui.lbl_bar.pos, target_pos, self.animation_end)

  def get_target_pos(self, num):
    return qt.QPoint(150, num * self.inter - 5 + self.inter/2)
  
  def animation_end(self):
    print("animation_end")

  def add_button_event(self, btn_name, operate_type, callback_func, is_connect):
    if hasattr(self.ui, btn_name) == False:
      return
    button = getattr(self.ui, btn_name)
    if is_connect == True:
      button.connect(operate_type, callback_func)
    else:
      button.disconnect(operate_type, callback_func)   
  
  def hide_top_view(self):
    if self.ui.tabWidget.count != 3:
      return
    self.ui.tabWidget.removeTab(0)    
    self.ui.tabWidget.setCurrentIndex(0)

  def insert_top_view(self):
    if self.ui.tabWidget.count != 2:
      return
    self.ui.tabWidget.insertTab(0, self.treat_view, "治疗进程")
    self.ui.tabWidget.setCurrentIndex(0)

  def on_click_auto_tgc(self):
    print('auto_tgc')
    self.clear_line_list()
    
    self.init_lines_widget(40)
    pass
  
  def on_click_compound(self):
    pass
  
  def on_click_harmonic(self):
    pass
  
  def on_click_hand(self):
    pass
  
  def on_click_vtu(self):
    pass

  def pressure_low_value_change(self, value):
    self.ui.lbl_low_value.setText('设定值：' + str(value))
    pass

  def pressure_high_value_change(self, value):
    self.ui.lbl_high_value.setText('设定值：' + str(value))
    pass

  def set_current_pressure_value(self, value):
    self.ui.lbl_current_value.setText(f'当前值：{value} mbar')

  def set_pressure_range(self, low_min, low_max, high_min, high_max):
    self.ui.slider_low.setRange(low_min, low_max)
    self.ui.slider_high.setRange(high_min, high_max)
  
  def on_gain_value_change(self, value):
    print('on_gain_value_change', value)

  