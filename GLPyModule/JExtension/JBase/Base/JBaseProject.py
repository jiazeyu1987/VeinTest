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
import os
import ctypes
import sys


class Node:
    def __init__(self, data):
        self.data = int(data)
        self.next = None


class LinkedList:
    def __init__(self):
        self.head = None

    # 在链表末尾添加新节点
    def append(self, data):
        new_node = Node(data)
        if not self.head:
            self.head = new_node
            return
        current = self.head
        while current.next:
            current = current.next
        current.next = new_node
        self.save()

    # 在链表头部插入新节点
    def prepend(self, data):
        new_node = Node(data)
        new_node.next = self.head
        self.head = new_node

    # 删除链表中的一个节点
    def delete(self, key):
        current = self.head
        if current and current.data == key:
            self.head = current.next
            current = None
            return
        prev = None
        while current and current.data != key:
            prev = current
            current = current.next
        if current is None:
            return
        prev.next = current.next
        current = None

    def pop(self):
        if not self.head:
            return None
        current = self.head
        prev = None
        while current.next:
            prev = current
            current = current.next
        if prev:
            prev.next = None
        else:
            self.head = None
        self.save()
        return current.data

    def save(self):
        data1 = []
        current = self.head
        data1.append(current.data.__str__())
        while current:
            current = current.next
            if current:
                data1.append(current.data.__str__())
        if len(data1) > 0:
            str1 = ",".join(data1)
            util.SetGlobalSaveValue("page_list", str1)

    # 打印整个链表
    def print_list(self):
        current = self.head
        while current:
            print(current.data, end=" -> ")
            current = current.next
        print("None")

    def get_first(self):
        if self.head:
            return self.head.data
        return None

    def get_last(self):
        current = self.head
        while current and current.next:
            current = current.next
        if current:
            return current.data
        return None


class JBaseProjectWidget(ScriptedLoadableModuleWidget, VTKObservationMixin):
    TagMaps = {}
    preinit = False
    ui = None
    linked_list = None

    def __init__(self, parent=None):
        """
        Called when the user opens the module the first time and the widget is initialized.
        """
        ScriptedLoadableModuleWidget.__init__(self, parent)
        VTKObservationMixin.__init__(self)  # needed for parameter node observation
        self.logic = None
        self._parameterNode = None
        self._updatingGUIFromParameterNode = False

    def setup(self):
        """
        Called when the user opens the module the first time and the widget is initialized.
        """
        ScriptedLoadableModuleWidget.setup(self)

        self.init_ui()
        self.linked_list = LinkedList()

    def makesure_key_file(self):
        key_path = slicer.app.slicerHome + "/key.txt"
        print("key_path:", key_path)
        return self.create_or_read_file(key_path)

    def create_or_read_file(self, file_name):
        # if not os.path.exists(file_name):
        with open(file_name, 'w') as f:
            id = self.get_mac_id()
            hashed_id = self.hash_id(id)
            hashed_id = hashed_id[-6:]
            f.write(hashed_id)
            return hashed_id

    # 对 CPU ID 进行哈希
    def hash_id(self, id):
        import hashlib
        return hashlib.sha256(id.encode()).hexdigest()

    def get_mac_id(self):
        str = util.mainWindow().GetMac()
        return str

    def addEvent(self, bool_val):
        if bool_val:
            print("addEvent Project Base")
        else:
            print("removeEvent Project Base")

    def enter(self):
        self.addEvent(True)

    def exit(self):
        self.addEvent(False)

    def preinit_modules(self):
        if not self.preinit:
            if util.JsonData:
                modules_str = util.getjson("pre_init")
                print("modules_str:", modules_str)
            else:
                modules_str = util.get_project_config("Init", "PreinitModules", "")
                print("modules_str2:", modules_str)
            if modules_str != "":
                modules = modules_str.split(", ")
                print("pre init modules:", modules)
                for module_name in modules:
                    print("pre init", module_name)
                    util.layout_panel("right").setModule(module_name)
            self.preinit = True

    def init_ui(self):
        import slicer.util as util
        self.settings = util.mainWindow().GetProjectSettings()
        util.load_extra_module_by_config(os.path.dirname(__file__))
        util.update_setting_from_config(self.settings)
        '''
          更新所有传入的模块的Reload按钮的可见性
          如果General/module_reload==2,那么可见
        '''
        util.update_module_reload_visibility([], self.settings)
        '''
          如果用激活码激活的话,激活WindowTitle的激活状态
        '''
        util.update_activate_state()
        self.TagMaps[util.ProgressStart] = slicer.mrmlScene.AddObserver(util.ProgressStart, self.OnProgressStart)
        self.TagMaps[util.ProgressValue] = slicer.mrmlScene.AddObserver(util.ProgressValue, self.OnProgressValue)
        self.TagMaps[util.ApplicationDisActivate] = slicer.mrmlScene.AddObserver(util.ApplicationDisActivate,
                                                                                 self.OnApplicationDisActivate)
        self.TagMaps[util.SetPage] = slicer.mrmlScene.AddObserver(util.SetPage, self.OnSetPage)
        self.TagMaps[util.GotoPrePage] = slicer.mrmlScene.AddObserver(util.GotoPrePage, self.OnGotoPrePage)
        self.TagMaps[util.GotoLastPage] = slicer.mrmlScene.AddObserver(util.GotoLastPage, self.OnGotoLastPage)
        self.TagMaps[util.GotoNextPage] = slicer.mrmlScene.AddObserver(util.GotoNextPage, self.OnGotoNextPage)
        self.TagMaps[util.GotoCurrentPage] = slicer.mrmlScene.AddObserver(util.GotoCurrentPage, self.OnGotoCurrentPage)
        self.TagMaps[util.NewFileLoadedFromMain] = slicer.mrmlScene.AddObserver(util.NewFileLoadedFromMain,
                                                                                self.OnNewFileLoaded)
        self.TagMaps[util.ArchiveFileLoadedEvent] = slicer.mrmlScene.AddObserver(util.ArchiveFileLoadedEvent,
                                                                                 self.OnArchiveFileLoadedEvent)

        self.TagMaps[util.SceneDestroyEvent] = slicer.mrmlScene.AddObserver(util.SceneDestroyEvent,
                                                                            self.OnSceneDestroyEvent)

        print("PPunctureGuid init Done")

    def OnSceneDestroyEvent(self, _a, _b):
        pass

    @vtk.calldata_type(vtk.VTK_OBJECT)
    def OnApplicationDisActivate(self, caller, str_event, calldata):
        raise Exception("PDuruofei Don't Have OnApplicationDisActivate Action")

    @vtk.calldata_type(vtk.VTK_OBJECT)
    def OnProgressStart(self, caller, str_event, calldata):
        val = calldata.GetAttribute("value")
        if val is None:
            val = "请稍候..."
        util.createProgressDialog2(parent=self, value=0, maximum=100, windowTitle=val)
        slicer.app.processEvents()

    @vtk.calldata_type(vtk.VTK_OBJECT)
    def OnProgressValue(self, caller, str_event, calldata):
        val = calldata.GetAttribute("value")
        util.setProgress(int(float(val)))
        slicer.app.processEvents()

    @vtk.calldata_type(vtk.VTK_OBJECT)
    def OnNewFileLoaded(self, caller, str_event):
        self.OnGotoNextPage("", "")

    @vtk.calldata_type(vtk.VTK_OBJECT)
    def OnArchiveFileLoadedEvent(self, caller, str_event, calldata):
        page_list = util.GetGlobalSaveValue("page_list")
        page_list = page_list.split(",")
        self.linked_list = LinkedList()
        for page in page_list:
            self.linked_list.append(page)
        util.singleShot(0, lambda: util.HideProgressBar())

    def on_activate(self):
        logic1 = util.getModuleLogic("JActivateCode")
        '''
          先远程激活
        '''
        res_net = logic1.verify_activate_code(self.ui.codetxt.text)
        if res_net:

            self.ui.tabWidget.setCurrentIndex(0)
            self.ui.label_3.setText("")
            self.ui.codetxt.setText("")
            util.mainWindow().setWindowTitle(
                util.mainWindow().GetProjectSettings().value("General/window_title") + "(已激活)")
            util.mainWindow().set_verification(True)
        else:
            widget1 = util.getModuleWidget("JMeasure")
            res_local = widget1.deshacoc(self.ui.label_4.text, self.ui.codetxt.text)
            if res_local:
                logic1.save_lock_file(self.ui.codetxt.text)
                self.ui.tabWidget.setCurrentIndex(0)
                self.ui.label_3.setText("")
                self.ui.codetxt.setText("")
                util.mainWindow().setWindowTitle(
                    util.mainWindow().GetProjectSettings().value("General/window_title") + "(已激活)")
                util.mainWindow().set_verification(True)
            else:
                self.ui.codetxt.setText("")
                self.ui.label_3.setText("激活码错误")

    @vtk.calldata_type(vtk.VTK_OBJECT)
    def OnSetPage(self, caller, str_event, calldata):
        # print("OnSetPage",self.linked_list.get_last())
        val = calldata.GetAttribute("value")
        if int(val) != int(self.linked_list.get_last()):
            self.linked_list.append(val)
        self._SetPage(self.linked_list.get_last())

    def OnGotoPrePage(self, _b, _a):
        print("OnGotoPrePage", self.linked_list.get_last())
        self.linked_list.pop()
        self._SetPage(self.linked_list.get_last())

    def OnGotoLastPage(self, _b, _a):
        print("OnGotoNextPage:", self.linked_list.get_last())
        next_page = self.linked_list.get_last() - 1
        self.linked_list.append(next_page)
        self._SetPage(self.linked_list.get_last())

    def OnGotoNextPage(self, _b, _a):
        print("OnGotoNextPage:", self.linked_list.get_last())
        next_page = self.linked_list.get_last() + 1
        self.linked_list.append(next_page)
        self._SetPage(self.linked_list.get_last())

    def OnGotoCurrentPage(self, _b, _a):
        self._SetPage(self.linked_list.get_last())

    def _SetPage(self, page):
        # print("Setting Page:", page)
        # 必须大于1,不然进入JPACS会覆盖掉之前的存档
        if page > 1:
            util.SetGlobalSaveValue("current_page", page.__str__())
        util.trigger_view_tool("")
