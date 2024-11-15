import imp
import os
from re import A
from tabnanny import check
from time import sleep
import unittest
import logging
import sqlite3
import vtk, qt, ctk, slicer
from slicer.ScriptedLoadableModule import *
from slicer.util import VTKObservationMixin
import slicer.util as util
import SlicerWizard.Utilities as su 
import numpy as np
from Base.JBaseExtension import JBaseExtensionWidget
from qt import QPropertyAnimation
#
# JAdministrator
#

class JAdministrator(ScriptedLoadableModule):

  def __init__(self, parent):
    ScriptedLoadableModule.__init__(self, parent)
    self.parent.title = "JAdministrator"  # TODO: make this more human readable by adding spaces
    self.parent.categories = ["RDN"]  # TODO: set categories (folders where the module shows up in the module selector)
    self.parent.dependencies = []  # TODO: add here list of module names that this module requires
    self.parent.contributors = ["jia ze yu"]  # TODO: replace with "Firstname Lastname (Organization)"
    # TODO: update with short description of the module and a link to online module documentation
    self.parent.helpText = """

"""
    # TODO: replace with organization, grant and thanks
    self.parent.acknowledgementText = """

"""

class JAdministratorWidget(JBaseExtensionWidget):
  init_once_flag = False
  conn = None
  cursor = None
  current_order = qt.Qt.AscendingOrder
  current_select_row = 0
  header_title_list = ['ID', '用户名', '密码', '准许', '注册时间', '上次登录时间', 'md5']
  header_width_list = [60, 200, 200, 60, 200, 200, 0]
  column_id = 0
  column_user = 1
  column_pwd = 2
  column_permit = 3
  column_reg_time = 4
  column_login_time = 5
  column_md5 = 6
  def setup(self):
    super().setup()
    print("JAdministratorWidget setup")
    

  def enter(self):
    self.init_once()
    self.addEvent(True)
    
  def init_once(self):
    if self.init_once_flag == True:
      return
    self.init_once_flag = True
    self.ui.btnReturn.setToolButtonStyle(qt.Qt.ToolButtonTextBesideIcon)
    self.init_table()

  def init_later(self):
    pass

  def init_table(self):
    title_size = len(self.header_title_list)
    self.ui.table_user.setColumnCount(title_size)
    self.ui.table_user.setHorizontalHeaderLabels(self.header_title_list)
    self.ui.table_user.setSelectionMode(qt.QAbstractItemView.SingleSelection)
    self.ui.table_user.horizontalHeader().setFixedHeight(56) #固定高度
    self.ui.table_user.verticalHeader().setDefaultSectionSize(56)
    self.ui.table_user.setEditTriggers(qt.QAbstractItemView.NoEditTriggers) #设置不触发编辑选项
    self.ui.table_user.horizontalHeader().setStretchLastSection(True)
    self.ui.table_user.setSelectionBehavior(qt.QAbstractItemView.SelectRows)
    #设置显示排序标志
    self.ui.table_user.horizontalHeader().setSortIndicatorShown(True)
    #隐藏纵向头部栏
    self.ui.table_user.verticalHeader().hide()
    #设置平分宽度,这里我们不需要平分
    #self.ui.table_user.horizontalHeader().setSectionResizeMode(qt.QHeaderView.Stretch) 
    for i in range(len(self.header_width_list)):
      self.ui.table_user.setColumnWidth(i, self.header_width_list[i])
    
    dbpath = os.path.join(util.mainWindow().GetProjectBasePath(),"Resources","user_data.db")
    self.conn = sqlite3.connect(dbpath)
    self.cursor = self.conn.cursor()

    self.fetch_all_users()
    hide = True
    self.ui.table_user.setColumnHidden(self.column_id, hide)
    self.ui.table_user.setColumnHidden(self.column_permit, hide)
    self.ui.table_user.setColumnHidden(self.column_md5, hide)

  def fetch_all_users(self):
    self.cursor.execute('SELECT * FROM users')
    items_list = self.cursor.fetchall()
    print(items_list)
    self.set_table_data(items_list)

  def set_table_data(self, datas):
    self.ui.table_user.setRowCount(len(datas))
    row_index = 0
    for item in datas:
      id = item[0]
      name = item[1]
      for i in range(len(self.header_title_list)):   
        info = self.get_des_info(i, item[i])
        widget_item = qt.QTableWidgetItem(info)
        widget_item.setData(qt.Qt.UserRole, item[i])
        widget_item.setTextAlignment(qt.Qt.AlignCenter)
        self.ui.table_user.setItem(row_index, i, widget_item)
      row_index = row_index + 1
    if row_index != 0:
      self.ui.table_user.setCurrentCell(0, 0)
      self.on_table_select_change(0, 0, 0, 0)
      self.current_select_row = 0
  def get_des_info(self, index, info):
    result = str(info)
    return result

  def exit(self):    
    self.addEvent(False)

  def addEvent(self,bool_val):
    self.add_button_event("btnCopy", 'clicked()', self.on_copy_info, bool_val)
    self.add_button_event("btnChange", 'clicked()', self.on_change_password, bool_val)
    self.add_button_event("btnAdd", 'clicked()', self.on_register_account, bool_val)
    self.add_button_event("btnDelete", 'clicked()', self.on_delete_account, bool_val)
    self.add_button_event("btn_search", 'clicked()', self.on_search_clicked, bool_val)
    self.add_button_event("btnReturn", 'clicked()', self.on_return_clicked, bool_val)
    if bool_val:
      self.ui.table_user.horizontalHeader().connect('sectionClicked(int)', self.on_sort)      
      self.ui.table_user.connect('currentCellChanged(int, int, int, int)', self.on_table_select_change)
    else:
      self.ui.table_user.horizontalHeader().disconnect('sectionClicked(int)', self.on_sort)
      self.ui.table_user.disconnect('currentCellChanged(int, int, int, int)', self.on_table_select_change)
    pass

  def on_return_clicked(self):
    util.send_event_str(util.SetPage, 2)

  def on_search_clicked(self):
    search_str = self.ui.lbl_search_info.text.strip()
    if search_str == '':      
      self.fetch_all_users()
      return
    search_info = f'%{search_str}%'
    self.cursor.execute('SELECT * FROM users WHERE username LIKE ?', (search_info,))
    user_data = self.cursor.fetchall()
    self.set_table_data(user_data)
    pass

  def on_delete_account(self):
    current_row = self.current_select_row
    delete_id = int(self.ui.table_user.item(current_row, 0).text())
    delete_name = self.ui.table_user.item(current_row, 1).text()
    result = util.getModuleWidget("JMessageBox").show_question("提示", f'是否要删除用户名:{delete_name}的用户？')
    if result == 0:
      return
    self.cursor.execute('DELETE from users where id=?', (delete_id,))
    res = self.conn.commit()
    self.fetch_all_users()
    print("User registered successfully.",res)

  def on_change_password(self):
    row = self.current_select_row
    user_id = self.ui.table_user.item(row, self.column_id).text()
    user_name = self.ui.table_user.item(row, self.column_user).text()
    user_pwd = self.ui.table_user.item(row, self.column_pwd).text()
    tmp_permit = self.ui.table_user.item(row, self.column_permit).text()
    user_reg_time = self.ui.table_user.item(row, self.column_reg_time).text()
    user_login_time = self.ui.table_user.item(row, self.column_login_time).text()
    user_info = [user_name, user_pwd, tmp_permit, user_reg_time, user_login_time]
    result = util.getModuleWidget("JMessageBox").show_change_password(user_id, user_info)
    if result == 0:
      return
    md5_value = util.get_md5_value(user_info)
    try:
      self.cursor.execute('UPDATE users set password=?, md5=? WHERE username = ?', (user_info[1], md5_value, user_name))
      self.conn.commit()
      print(result, user_info)
      self.ui.table_user.item(row, self.column_pwd).setText(user_info[1])
    except sqlite3.Error as e:
      print("SQLite error:", e)

  def on_register_account(self):
    user_info = ["", ""]
    result = util.getModuleWidget("JMessageBox").show_register_account(user_info)
    if result == 0:
      return
    username = user_info[0]
    password = user_info[1]
    try:
      from datetime import datetime
      # 检查用户名是否已经存在
      self.cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
      existing_user = self.cursor.fetchone()

      if existing_user:
          return

      # 获取当前时间作为注册时间
      registration_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

      # 插入新用户信息
      sign_up_list = [username, password, "1", registration_time, registration_time]
      md5_value = util.get_md5_value(sign_up_list)
      self.cursor.execute('INSERT INTO users (username, password, permission, registration_time, last_login_time, md5) VALUES (?, ?, ?, ?, ?, ?)', (username, password, 1, registration_time, registration_time, md5_value))
      res = self.conn.commit()
      self.fetch_all_users()
      print("User registered successfully.",res)
    except sqlite3.Error as e:
      print("SQLite error:", e)

  def on_copy_info(self):
    util.add_to_clipboard(self.ui.lblInfo.text)

  def on_table_select_change(self, currRow, currColumn, perviouRow, perviousColumn):
    print("currRow, currColumn, perviouRow, perviousColumn", currRow, currColumn, perviouRow, perviousColumn)
    detail_info = self.get_user_detail_info(currRow)
    self.ui.lblInfo.setText(detail_info)
    self.current_select_row = currRow

  def get_user_detail_info(self, row):
    user_id = self.ui.table_user.item(row, self.column_id).text()
    user_name = self.ui.table_user.item(row, self.column_user).text()
    user_pwd = self.ui.table_user.item(row, self.column_pwd).text()
    tmp_permit = self.ui.table_user.item(row, self.column_permit).text()
    user_permit = '是'
    if tmp_permit != "1":
      user_permit = '否'
    user_reg_time = self.ui.table_user.item(row, self.column_reg_time).text()
    user_login_time = self.ui.table_user.item(row, self.column_login_time).text()
    detail_info = f'''
    id:  {user_id}
    用户名:  {user_name}
    密码:  {user_pwd}
    允许登录:  {user_permit}
    注册时间:  {user_reg_time}
    登录时间:  {user_login_time}'''
    return detail_info

  def on_sort(self, column):
    if self.current_order == qt.Qt.AscendingOrder:
      self.current_order = qt.Qt.DescendingOrder
    else:
      self.current_order = qt.Qt.AscendingOrder
    self.ui.table_user.horizontalHeader().setSortIndicator(column, self.current_order)
    self.ui.table_user.sortByColumn(column)

  def add_button_event(self, btn_name, operate_type, callback_func, is_connect):
    if hasattr(self.ui, btn_name) == False:
      return
    button = getattr(self.ui, btn_name)
    if is_connect == True:
      button.connect(operate_type, callback_func)
    else:
      button.disconnect(operate_type, callback_func)  

  def set_label_style_sheet(self, lbl, image_name):
    img_path = self.resourcePathEx(f'Image/{image_name}.png')
    style_str = "border-image: url("+img_path +");"              
    lbl.setStyleSheet(style_str)

