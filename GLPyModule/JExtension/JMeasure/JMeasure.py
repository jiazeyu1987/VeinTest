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
from MeasureLib.Helper import JMeasureTool


# JMeasure
#


class JMeasurePanelPanel(ctk.ctkSettingsPanel):
    def __init__(self, *args, **kwargs):
        ctk.ctkSettingsPanel.__init__(self, *args, **kwargs)
        self.ui = _ui_JMeasurePanelPanel(self)


class _ui_JMeasurePanelPanel:
    def __init__(self, parent):
        util.getModuleWidget("JMeasure").init_setting_panel_ui(parent)


class JMeasure(ScriptedLoadableModule):

    def __init__(self, parent):
        ScriptedLoadableModule.__init__(self, parent)
        self.parent.title = "JMeasure"  # TODO: make this more human readable by adding spaces
        self.parent.categories = [
            "JPlugins"]  # TODO: set categories (folders where the module shows up in the module selector)
        self.parent.dependencies = []  # TODO: add here list of module names that this module requires
        self.parent.contributors = ["jia ze yu"]  # TODO: replace with "Firstname Lastname (Organization)"
        # TODO: update with short description of the module and a link to online module documentation
        self.parent.helpText = """

"""
        # TODO: replace with organization, grant and thanks
        self.parent.acknowledgementText = """

"""


#
# JMeasureWidget
#

class JMeasureWidget(ScriptedLoadableModuleWidget, VTKObservationMixin):
    tool_list = []

    tool_whirling = "whirling"
    tool_reset = "reset"
    tool_wl_auto = "windowlevel_auto"
    tool_wl_bone = "windowlevel_bone"
    tool_wl_tissue = "windowlevel_tissue"
    tool_line = "tool_line"
    tool_angle = "tool_angle"
    tool_area_open = "tool_area_open"
    tool_area = "tool_area"
    tool_hide_measure = "tool_hide_measure"
    tool_zoomin = "tool_zoomin"
    tool_zoomout = "tool_zoomout"
    tool_multivolume_slider = "tool_multivolume_slider"
    tool_multivolume_point = "tool_multivolume_point"
    tool_contact_developer = "tool_contact_developer"
    tool_contact_doctor = "tool_contact_doctor"
    tool_windowlevel = "tool_windowlevel"
    tool_video_link = "tool_video_link"
    tool_logo = "tool_logo"
    tool_test = "tool_test"
    tool_save = "tool_save"
    tool_load = "tool_load"
    tool_layout = "tool_layout"
    tool_screenshot = "tool_screenshot"
    tool_developer = "tool_developer"
    tool_measurebox = "tool_measurebox"
    tool_crosshairbox = "tool_crosshairbox"
    tool_thanks = "tool_thanks"
    tool_friends = "tool_friends"
    tool_chatgpt = "tool_chatgpt"
    tool_setting = "tool_setting"
    tool_controller = "tool_controller"
    tool_exit = "tool_exit"
    tool_minimum = "tool_minimum"
    tool_extension = "tool_extension"
    tool_close_scene = "tool_close_scene"
    tool_save_volume_paras = "tool_save_volume_paras"
    tool_load_volume_paras = "tool_load_volume_paras"
    tool_page_data = "tool_page_data"
    tool_page_scan = "tool_page_scan"
    tool_page_volumerendering = "tool_page_volumerendering"
    tool_page_cmf = "tool_page_cmf"
    tool_page_roi = "tool_page_roi"
    tool_jpacs = "tool_jpacs"
    tool_scale = "tool_scale"
    tool_light = "tool_light"
    tool_handeye = "tool_handeye"
    tool_ime = "tool_ime"
    tool_register = "tool_register"
    tool_elibot = "tool_elibot"
    tool_usb = "tool_usb"
    tool_tick = "tool_tick"
    use_tool_bar = 0
    layout_init = False
    button_width = 60
    button_height = 80
    toolbars = ""
    right_to_left = ""
    left_to_right = ""
    logo_text = ""
    logo_icon_name = ""
    horizontal = "horizontal"
    vertical = "vertical"
    orientation = "horizontal"
    tmap = {}
    measure_flag = False
    resourcelist = {}
    toolbar_layout_list = {}
    qprocess = None

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
        self.logic = JMeasureLogic()
        self.logic.setWidget(self)

        uiWidget = slicer.util.loadUI(self.resourcePath('UI/JMeasure.ui'))
        self.layout.addWidget(uiWidget)
        self.ui = slicer.util.childWidgetVariables(uiWidget)

        uiWidget.setMRMLScene(slicer.mrmlScene)
        self.init_ui()
        self.resourcelist = {}
        self.ui.JMeasure.setStyleSheet("background-color: %s;" % (util.QSS_QWidget_background_color))

        slicer.mrmlScene.AddObserver(slicer.vtkMRMLScene.NodeRemovedEvent, self.OnNodeRemovedEvent)

    def enter(self):
        print("measure enter")

    def exit(self):
        pass

    def get_resource_list(self):
        txt = ""
        for key in self.resourcelist:
            value = self.resourcelist[key]
            txt = txt + key + ":\t\t" + value + "\n"
        filepath = util.get_resource("toolbar_resource_list.txt", use_default_path=False)
        if txt != "":
            with open(filepath, "w") as file:
                file.write(txt)
        return txt

    def init_setting_panel_ui(self, parent):
        template1 = slicer.util.loadUI(self.resourcePath("UI/JMeasurePanel.ui"))
        panelui = slicer.util.childWidgetVariables(template1)
        parent.registerProperty("General/bg_3d_color1", panelui.lineEdit1, "text",
                                str(qt.SIGNAL("textChanged(QString)")))
        parent.registerProperty("General/bg_3d_color2", panelui.lineEdit2, "text",
                                str(qt.SIGNAL("textChanged(QString)")))
        settings = qt.QSettings()
        color1_str = settings.value("General/bg_3d_color1")
        color2_str = settings.value("General/bg_3d_color2")
        if color1_str == "" or color1_str is None:
            color1_str = "0,0,0"
        if color2_str == "" or color2_str is None:
            color2_str = "0,0,0"

        default_path = settings.value("General/default_path")
        if default_path == "" or default_path is None:
            default_path = os.path.join(util.mainWindow().GetProjectBasePath(), "Resources").replace('\\', '/')
            panelui.le_path.setText(default_path)
        color1list = color1_str.split(",")
        color2list = color2_str.split(",")
        color1 = qt.QColor(float(color1list[0]) * 255, float(color1list[1]) * 255, float(color1list[2]) * 255)
        color2 = qt.QColor(float(color2list[0]) * 255, float(color2list[1]) * 255, float(color2list[2]) * 255)
        panelui.colorPicker1.setColor(color1)
        panelui.colorPicker2.setColor(color2)
        panelui.colorPicker1.setProperty("changeColorOnSet", True)
        panelui.colorPicker1.setDisplayColorName(True)
        panelui.colorPicker2.setProperty("changeColorOnSet", True)
        panelui.colorPicker2.setDisplayColorName(True)
        panelui.colorPicker1.connect('colorChanged(QColor)', self.on_change_color)
        panelui.colorPicker2.connect('colorChanged(QColor)', self.on_change_color)
        panelui.lineEdit1.setVisible(False)
        panelui.lineEdit2.setVisible(False)
        parent.registerProperty("General/default_path", panelui.le_path, "text", str(qt.SIGNAL("textChanged(QString)")))
        vBoxLayout = qt.QVBoxLayout(parent)
        vBoxLayout.addWidget(panelui.JMeasurePanel)
        self.tmap["colorPicker1"] = panelui.colorPicker1
        self.tmap["colorPicker2"] = panelui.colorPicker2
        self.tmap["lineEdit1"] = panelui.lineEdit1
        self.tmap["lineEdit2"] = panelui.lineEdit2

    def on_change_color(self, color):
        color1 = self.tmap["colorPicker1"].color
        color2 = self.tmap["colorPicker2"].color
        self.tmap["lineEdit1"].setText("%f,%f,%f" % (color1.redF(), color1.greenF(), color1.blueF()))
        self.tmap["lineEdit2"].setText("%f,%f,%f" % (color2.redF(), color2.greenF(), color2.blueF()))
        viewNode = slicer.app.layoutManager().threeDWidget(0).mrmlViewNode()
        viewNode.SetBackgroundColor(color1.redF(), color1.greenF(), color1.blueF())
        viewNode.SetBackgroundColor2(color2.redF(), color2.greenF(), color2.blueF())

    def addPanel(self):
        self.settingsPanel = JMeasurePanelPanel()
        slicer.app.settingsDialog().addPanel("通用", self.settingsPanel)

    def init_from_config_json(self, config):
        if self.layout_init:
            return
        self.layout_init = True
        self.button_width = int(config['button_width'])
        self.button_height = int(config['button_height'])
        if 'use_tool_bar' in config:
            self.use_tool_bar = int(config['use_tool_bar'])
        if 'right_to_left' in config:
            self.right_to_left = config['right_to_left']
        self.left_to_right = config['left_to_right']

        if 'orientation' in config:
            self.orientation = config['orientation']
        else:
            self.orientation = self.horizontal
        self.init_layout()
        self.get_resource_list()

    def init_ui(self):
        qt.QTimer.singleShot(10, self.addPanel)

    def init_layout(self):

        toollist = []
        tool_button_list = ["tool_layout", "tool_measurebox", "tool_windowlevel", "tool_developer"]
        left_to_rights = self.left_to_right.split("|")
        for button_str in left_to_rights:
            if button_str in tool_button_list:
                tool = self.add_tool_by_name(button_str, self.ui.parent_widget1321)
                toollist.append(tool)
        for button_str in left_to_rights:
            if button_str not in tool_button_list:
                tool = self.add_tool_by_name(button_str, self.ui.parent_widget1321)
                toollist.append(tool)

        layout = None
        if self.ui.parent_widget1321.layout() is None:
            if self.orientation == self.vertical:
                layout = qt.QVBoxLayout(self.ui.parent_widget1321)
                layout.setSpacing(10)
                layout.setContentsMargins(4, 8, 4, 8)
                sub_layout1 = qt.QVBoxLayout()
                sub_layout2 = qt.QVBoxLayout()
                layout.addLayout(sub_layout1)
                layout.addLayout(sub_layout2)
                sub_layout1.setSpacing(10)
                sub_layout1.setContentsMargins(0, 0, 0, 0)
                sub_layout2.setSpacing(10)
                sub_layout2.setContentsMargins(0, 0, 0, 0)
                sub_layout2.setAlignment(qt.Qt.AlignTop)
            else:
                layout = qt.QHBoxLayout(self.ui.parent_widget1321)
                layout.setSpacing(10)
                layout.setContentsMargins(0, 0, 0, 0)
                sub_layout1 = qt.QHBoxLayout()
                sub_layout2 = qt.QHBoxLayout()
                layout.addLayout(sub_layout1)
                layout.addLayout(sub_layout2)
                sub_layout1.setSpacing(10)
                sub_layout1.setContentsMargins(4, 8, 4, 8)
                sub_layout2.setSpacing(10)
                sub_layout2.setContentsMargins(4, 8, 4, 8)
                sub_layout2.setAlignment(qt.Qt.AlignRight)
        else:
            layout = self.ui.parent_widget1321.layout()
        # if self.use_tool_bar==2:
        #   spacer = qt.QWidget()
        #   spacer.setFixedWidth(100)
        #   util.moduleSelector().addWidget(spacer)

        project_name = util.getjson("project_name")
        filepath = os.path.join(util.mainWindow().GetProjectBasePath(), "ProjectCache", project_name,
                                "banner.png").replace('\\', '/')
        if os.path.exists(filepath):
            if self.orientation == self.horizontal:
                qlabel = qt.QLabel()
                qlabel.setFixedSize(32, 24)
                qtextlabel = qt.QLabel()
                qtextlabel.setText(util.get_from_PAAA("current_project_selector_description"))
                sub_layout1.addWidget(qlabel)
                sub_layout1.addWidget(qtextlabel)
                util.add_pixelmap_to_label(filepath, qlabel)
        else:
            if self.orientation == self.horizontal:
                qlabel = qt.QLabel()
                qlabel.setFixedSize(32, 24)
                util.addWidget2(sub_layout1, qlabel)
                qlabel.setText(util.getjson("window_title"))

        for tool in toollist:
            if tool.layout:
                if self.use_tool_bar == 2:
                    action = util.moduleSelector().addWidget(tool.layout)
                    self.toolbar_layout_list[tool.label] = action
                else:
                    sub_layout2.addWidget(tool.layout)
                    pass

    def hide_all(self):
        for label in self.toolbar_layout_list:
            action = self.toolbar_layout_list[label]
            util.moduleSelector().removeAction(action)

    def add_actions(self, namelist):
        for name in namelist:
            action = self.toolbar_layout_list[name]
            util.moduleSelector().addAction(action)

    def init_old_toolbars(self):
        # for toolbar in self.toolbars:
        #   if toolbar.strip()=="":
        #     return
        #   toolnames = toolbar.split("|")
        #   print(toolnames)
        #   if len(toolnames)<4:
        #     return
        #   start_pos = int(toolnames[1])
        #   widget,pos = self.add_group(self.ui.parent_widget1321,toolnames[3:])
        #   widget.move(start_pos,0)
        #   start_pos = start_pos + pos + (int(self.normal_spacing))
        pass

    def add_group(self, parent_widget1321, tool_name_list):
        parent_widget1321 = qt.QWidget(parent_widget1321)
        toollist = []
        for tool_name in tool_name_list:
            print("add tool by name:", tool_name)
            tool = self.add_tool_by_name(tool_name, parent_widget1321)
            toollist.append(tool)
        pos = 0
        for tool in toollist:
            pos = pos + 0
            if tool.layout:
                if self.orientation == self.vertical:
                    tool.layout.move(0, pos)
                else:
                    tool.layout.move(pos, 0)
            pos = pos + self.button_width
        return parent_widget1321, pos

    def get_btn_by_name(self, tool_name):
        for tool in self.tool_list:
            if tool.label == tool_name:
                print(tool.label, tool.btn)
                return tool.btn
        return None

    def get_tool_by_name(self, tool_name):
        for tool in self.tool_list:
            if tool.label == tool_name:
                return tool
        return None

    def add_tool_by_name(self, tool_name, parent_widget1321):
        print("add_tool_by_name", tool_name)
        if tool_name == "space":
            return JMeasureTool(None, None, "")
        if tool_name == self.tool_whirling:
            return self.add_whirling_tool(parent_widget1321)
        if tool_name == self.tool_reset:
            return self.add_reset_tool(parent_widget1321)
        if tool_name == self.tool_wl_auto:
            return self.add_WindowLevel_tool(parent_widget1321)
        if tool_name == self.tool_wl_bone:
            return self.add_WindowLevel_bone(parent_widget1321)
        if tool_name == self.tool_wl_tissue:
            return self.add_WindowLevel_tissue(parent_widget1321)
        if tool_name == self.tool_line:
            return self.add_line_tool(parent_widget1321)
        if tool_name == self.tool_angle:
            return self.add_angle_tool(parent_widget1321)
        if tool_name == self.tool_area:
            return self.add_area_tool(parent_widget1321)
        if tool_name == self.tool_area_open:
            return self.add_area_open_tool(parent_widget1321)
        if tool_name == self.tool_hide_measure:
            return self.add_hide_measure_tool(parent_widget1321)
        if tool_name == self.tool_zoomin:
            return self.add_zoomin_tool(parent_widget1321)
        if tool_name == self.tool_zoomout:
            return self.add_zoomout_tool(parent_widget1321)
        if tool_name == self.tool_contact_developer:
            return self.add_tool_contact_developer(parent_widget1321)
        if tool_name == self.tool_contact_doctor:
            return self.add_tool_contact_doctor(parent_widget1321)
        if tool_name == self.tool_thanks:
            return self.add_tool_thanks(parent_widget1321)
        if tool_name == self.tool_friends:
            return self.add_tool_friends(parent_widget1321)
        if tool_name == self.tool_controller:
            return self.add_tool_controller(parent_widget1321)
        if tool_name == self.tool_screenshot:
            return self.add_tool_screenshot(parent_widget1321)
        if tool_name == self.tool_save_volume_paras:
            return self.add_tool_save_volume_paras(parent_widget1321)
        if tool_name == self.tool_load_volume_paras:
            return self.add_tool_load_volume_paras(parent_widget1321)
        if tool_name == self.tool_jpacs:
            return self.add_tool_jpacs(parent_widget1321)
        if tool_name == self.tool_scale:
            return self.add_tool_scale(parent_widget1321)
        if tool_name == self.tool_light:
            return self.add_tool_light(parent_widget1321)
        if tool_name == self.tool_handeye:
            return self.add_tool_handeye(parent_widget1321)
        if tool_name == self.tool_ime:
            return self.add_tool_ime(parent_widget1321)
        if tool_name == self.tool_tick:
            return self.add_tool_tick(parent_widget1321)
        if tool_name == self.tool_usb:
            return self.add_tool_usb(parent_widget1321)
        if tool_name == self.tool_elibot:
            return self.add_tool_elibot(parent_widget1321)
        if tool_name == self.tool_register:
            return self.add_tool_register(parent_widget1321)
        if tool_name == self.tool_multivolume_slider:
            tool = self.add_multivolume_slider_tool(parent_widget1321)
            return tool
        if tool_name == self.tool_multivolume_point:
            return self.add_multivolume_point_tool(parent_widget1321)
        if tool_name == self.tool_video_link:
            return self.add_tool_video_link(parent_widget1321)
        if tool_name == self.tool_test:
            return self.add_tool_test(parent_widget1321)
        if self.tool_logo in tool_name:
            return self.add_tool_logo(parent_widget1321)
        if tool_name == self.tool_layout:
            return self.add_tool_layout(parent_widget1321)
        if tool_name == self.tool_developer:
            return self.add_tool_developer(parent_widget1321)
        if tool_name == self.tool_windowlevel:
            return self.add_tool_windowlevel_presets(parent_widget1321)
        if tool_name == self.tool_measurebox:
            return self.add_tool_measurebox(parent_widget1321)
        if tool_name == self.tool_crosshairbox:
            return self.add_tool_crosshairbox(parent_widget1321)
        if tool_name == self.tool_save:
            return self.add_tool_save(parent_widget1321)
        if tool_name == self.tool_close_scene:
            return self.add_tool_close_scene(parent_widget1321)
        if tool_name == self.tool_exit:
            return self.add_tool_exit(parent_widget1321)
        if tool_name == self.tool_minimum:
            return self.add_tool_minimum(parent_widget1321)
        if tool_name == self.tool_load:
            return self.add_tool_load(parent_widget1321)
        if tool_name == self.tool_chatgpt:
            return self.add_tool_chatgpt(parent_widget1321)
        if tool_name == self.tool_setting:
            return self.add_tool_setting(parent_widget1321)
        if tool_name == self.tool_extension:
            return self.add_tool_extension(parent_widget1321)
        if tool_name == self.tool_page_data:
            return self.add_tool_page_data(parent_widget1321)
        if tool_name == self.tool_page_scan:
            return self.add_tool_page_scan(parent_widget1321)
        if tool_name == self.tool_page_volumerendering:
            return self.add_tool_page_volumerendering(parent_widget1321)
        if tool_name == self.tool_page_cmf:
            return self.add_tool_page_cmf(parent_widget1321)
        if tool_name == self.tool_page_roi:
            return self.add_tool_page_roi(parent_widget1321)

    '''
    MultiVolume滚动条工具
  '''

    def add_multivolume_slider_tool(self, parent):
        module_widget = util.getModuleWidget("JMultiVolumeTool")
        layout, btn, slider = module_widget.create_slide_layout(parent, 50)
        tool = JMeasureTool(layout, btn, "tool_multivolume_slider")
        tool.slider = slider
        self.tool_list.append(tool)
        tool.timer = qt.QTimer()
        tool.timer.setInterval(50)
        module_widget.set_slider_tool(tool)
        return tool

    '''
    MultiVolume取点工具
  '''

    def add_multivolume_point_tool(self, parent):
        module_widget = util.getModuleWidget("JMultiVolumeTool")
        layout, btn = self.create_labeled_checkable_button(parent, "tool_dce_point.png", "tool_dce_point.png",
                                                           "在DCE图像上取点", "取点")
        tool = JMeasureTool(layout, btn, self.tool_multivolume_point)
        self.tool_list.append(tool)
        module_widget.set_point_tool(tool)
        util.registe_view_tool(btn, "tool_point")
        return tool

    def add_tool_video_link(self, parent):
        layout, btn = self.create_labeled_clicked_button(parent, "video.png", "在网上查看软件使用教程", "视频教程")
        tool = JMeasureTool(layout, btn, "video_link")
        self.tool_list.append(tool)
        btn.connect('clicked()', self.on_video_link)
        return tool

    def on_video_link(self):
        qt.QDesktopServices.openUrl(qt.QUrl("https://h5.clewm.net/?url=qr61.cn%2FoWV3W3%2FqFyRbhg&hasredirect=1"))

    def add_tool_logo(self, parent):
        import qt
        btn = qt.QPushButton(parent)
        btn.setGeometry(0, 0, 48, 48)

        labelPic = qt.QLabel()
        labelText = qt.QLabel()
        picPath = util.get_resource(self.logo_icon_name + '.png').replace('\\', '/')
        labelPic.setPixmap(qt.QPixmap(picPath))
        labelPic.setObjectName("labelPic")
        labelText.setText(self.logo_text)
        labelText.setObjectName("labelText")
        labelText.setStyleSheet("font: 16px 'Source Han Sans CN-Regular, Source Han Sans CN';")
        layout = qt.QHBoxLayout()
        layout.addSpacing(2)
        layout.addWidget(labelPic)
        layout.addSpacing(10)
        layout.addWidget(labelText)
        layout.addStretch()
        btn.setLayout(layout)
        btn.setStyleSheet("background-color: #363d4a; border: 0px")
        tool = JMeasureTool(btn, btn, "logo")
        self.tool_list.append(tool)
        # btn.connect('clicked()', self.on_logo)

        return tool

    def add_tool_test(self, parent):
        layout, btn = self.create_labeled_checkable_button(parent, "tool_clicked_zoomin.png", "tool_clicked_zoomin.png",
                                                           "测试", "测试")
        tool = JMeasureTool(layout, btn, "test")
        self.tool_list.append(tool)
        btn.connect('toggled(bool)', self.on_test)
        util.registe_view_tool(btn, "test")
        return tool

    def on_test(self, is_show):
        # util.send_event_str(1241211,"abcdeft")
        print("on save")
        util.show_gif_progress()
        application_path = slicer.app.applicationDirPath() + "/bak/save.%s" % (self.get_extension())
        util.saveScene(application_path)
        util.hide_gif_progress()

    def add_icon_action(self, menu, path, name, func):
        # path = self.resourcePath(path).replace("\\", "/")
        self.resourcelist[path] = "action_" + name
        path = util.get_resource(path)
        icon = qt.QPixmap(path).scaled(qt.QSize(16, 16), qt.Qt.KeepAspectRatio, qt.Qt.SmoothTransformation)
        icon = qt.QIcon(icon)
        menu.addAction(icon, name, func)

    def update_measure_box(self, btn, path, name):
        btn.toggled.disconnect()
        if name == "长度":
            # self.on_tool_line(True)
            btn.connect('toggled(bool)', self.on_measurebox_tool_line)
        if name == "角度":
            # self.on_tool_angle(True)
            btn.connect('toggled(bool)', self.on_measurebox_tool_angle)
        if name == "面积":
            # self.on_tool_area(True)
            btn.connect('toggled(bool)', self.on_measurebox_tool_area)
        if name == "曲线":
            # self.on_tool_area_open(True)
            btn.connect('toggled(bool)', self.on_measurebox_tool_area_open)
        if name == "矩形":
            btn.connect('toggled(bool)', self.on_measurebox_tool_plane)
        if name == "ROI":
            btn.connect('toggled(bool)', self.on_measurebox_tool_roi)
        # path = self.resourcePath(path).replace("\\", "/")
        path = util.get_resource(path)
        icon = qt.QPixmap(path).scaled(qt.QSize(24, 24), qt.Qt.KeepAspectRatio, qt.Qt.SmoothTransformation)
        icon = qt.QIcon(icon)
        btn.setIcon(icon)
        btn.setText(name)
        btn.setChecked(True)

    def activate_crosshairbox(self):
        print("activate_crosshairbox")
        tool = self.get_tool_by_name("crosshairbox")
        btn = tool.btn
        btn.setChecked(False)
        btn.setChecked(True)

    def add_tool_crosshairbox(self, parent):
        layout, btn = self.create_toolbutton(parent, "tool_cross.png", "十字线", "十字线")
        btn.setCheckable(True)
        btn.connect('toggled(bool)', self.on_crosshairbox_crosshair)
        menu = qt.QMenu(parent)
        btn.setMenu(menu)
        self.add_icon_action(menu, "tool_cross.png", "十字线",
                             lambda: self.update_crosshairbox("tool_cross.png", "十字线"))
        self.add_icon_action(menu, "tool_whirling.png", "MPR",
                             lambda: self.update_crosshairbox("tool_whirling.png", "MPR"))
        tool = JMeasureTool(layout, btn, "crosshairbox")
        util.registe_view_tool(btn, "crosshairbox")
        self.tool_list.append(tool)

        return tool

    def update_crosshairbox(self, path, name):
        print("update_crosshairbox", name)
        tool = self.get_tool_by_name("crosshairbox")
        layout = tool.layout
        btn = tool.btn
        btn.toggled.disconnect()
        if name == "MPR":
            # self.on_tool_line(True)
            btn.connect('toggled(bool)', self.on_crosshairbox_mpr)
        if name == "十字线":
            # self.on_tool_angle(True)
            btn.connect('toggled(bool)', self.on_crosshairbox_crosshair)
        # path = self.resourcePath(path).replace("\\", "/")
        path = util.get_resource(path)
        icon = qt.QPixmap(path).scaled(qt.QSize(24, 24), qt.Qt.KeepAspectRatio, qt.Qt.SmoothTransformation)
        icon = qt.QIcon(icon)
        btn.setIcon(icon)
        label = util.findChild(layout, name="labelText")
        label.setText(name)
        btn.setChecked(False)
        btn.setChecked(True)

    def on_crosshairbox_mpr(self, is_show):
        print("on_crosshairbox_mpr", is_show)

        if is_show:
            self.on_crosshairbox_crosshair(False)
            util.trigger_view_tool("crosshairbox")
        slicer.app.applicationLogic().SetIntersectingSlicesEnabled(
            slicer.vtkMRMLApplicationLogic.IntersectingSlicesVisibility, is_show)
        slicer.app.applicationLogic().SetIntersectingSlicesEnabled(
            slicer.vtkMRMLApplicationLogic.IntersectingSlicesInteractive, is_show)
        displayNodes = util.getNodesByClass("vtkMRMLSliceDisplayNode")
        for displayNode in displayNodes:
            displayNode.SetIntersectingSlicesLineThicknessMode(1)
        sliceNodes = util.getNodesByClass("vtkMRMLSliceNode")
        for sliceNode in sliceNodes:
            sliceNode.Modified()

    def on_crosshairbox_crosshair(self, is_show):
        print("on_crosshairbox_crosshair", is_show)

        if is_show:
            self.on_crosshairbox_mpr(False)
            util.trigger_view_tool("crosshairbox")
        crosshairNode = slicer.util.getNode("Crosshair")
        color_cross = [0, 1.0, 0.968]
        crosshairNode.SetCrosshairColor(color_cross)

        if is_show:
            crosshairNode.SetCrosshairMode(slicer.vtkMRMLCrosshairNode.ShowIntersection)
            crosshairNode.SetCrosshairBehavior(crosshairNode.CenteredJumpSlice)
        else:
            crosshairNode.SetCrosshairMode(slicer.vtkMRMLCrosshairNode.NoCrosshair)

    def add_tool_measurebox(self, parent):
        layout, btn = self.create_toolbutton(parent, "tool_line.png", "测量", "测量")
        btn.setCheckable(True)
        btn.connect('toggled(bool)', self.on_measurebox_tool_line)
        menu = qt.QMenu(parent)
        btn.setMenu(menu)
        slicer.app.applicationLogic().GetInteractionNode().AddObserver(
            slicer.vtkMRMLInteractionNode.InteractionModeChangedEvent, self.OnInteractionModeChangedEvent)
        self.add_icon_action(menu, "tool_line.png", "长度",
                             lambda: self.update_measure_box(btn, "tool_line.png", "长度"))
        self.add_icon_action(menu, "tool_angle.png", "角度",
                             lambda: self.update_measure_box(btn, "tool_angle.png", "角度"))
        self.add_icon_action(menu, "tool_area.png", "面积",
                             lambda: self.update_measure_box(btn, "tool_area.png", "面积"))
        self.add_icon_action(menu, "tool_curve.png", "曲线",
                             lambda: self.update_measure_box(btn, "tool_curve.png", "曲线"))
        self.add_icon_action(menu, "tool_rectangle.png", "矩形",
                             lambda: self.update_measure_box(btn, "tool_rectangle.png", "矩形"))
        self.add_icon_action(menu, "tool_roi.png", "ROI", lambda: self.update_measure_box(btn, "tool_roi.png", "ROI"))
        self.add_icon_action(menu, "invisible.png", "隐藏所有", self.on_hide_all_measure)
        self.add_icon_action(menu, "visible.png", "显示所有", self.on_show_all_measure)
        self.add_icon_action(menu, "tool_delete.png", "删除所有", self.on_delete_all_measure)
        tool = JMeasureTool(layout, btn, "measurebox")
        util.registe_view_tool(btn, "measurebox")
        self.tool_list.append(tool)
        return tool

    def on_show_all_measure(self):
        nodes = util.getNodesByClass(util.vtkMRMLMarkupsNode)
        for node in nodes:
            if node.GetAttribute("is_measure") == "1":
                util.ShowNode(node)

    def on_hide_all_measure(self):
        nodes = util.getNodesByClass(util.vtkMRMLMarkupsNode)
        for node in nodes:
            if node.GetAttribute("is_measure") == "1":
                util.HideNode(node)

    def on_delete_all_measure(self):
        res = util.messageBox("确定删除所有测量项吗", windowTitle="警告")
        if res == 0:
            return
        nodes = util.getNodesByClass(util.vtkMRMLMarkupsNode)
        for node in nodes:
            if node.GetAttribute("is_measure") == "1":
                util.RemoveNode(node)
        print("on_delete_all_measure:", len(nodes))

    def add_tool_measurebox_outside(self, parent, btn):

        pic = "tool_line.png"
        icon_path = util.get_resource(pic)
        util.add_pixel_middle(icon_path, btn, "测量", size=32)
        btn.setCheckable(True)
        btn.connect('toggled(bool)', self.on_measurebox_tool_line)
        menu = qt.QMenu(parent)
        btn.setMenu(menu)
        slicer.app.applicationLogic().GetInteractionNode().AddObserver(
            slicer.vtkMRMLInteractionNode.InteractionModeChangedEvent, self.OnInteractionModeChangedEvent)
        self.add_icon_action(menu, "tool_line.png", "长度",
                             lambda: self.update_measure_box_outside(btn, "tool_line.png", "长度"))
        self.add_icon_action(menu, "tool_angle.png", "角度",
                             lambda: self.update_measure_box_outside(btn, "tool_angle.png", "角度"))
        self.add_icon_action(menu, "tool_area.png", "面积",
                             lambda: self.update_measure_box_outside(btn, "tool_area.png", "面积"))
        self.add_icon_action(menu, "tool_curve.png", "曲线",
                             lambda: self.update_measure_box_outside(btn, "tool_curve.png", "曲线"))
        self.add_icon_action(menu, "tool_rectangle.png", "矩形",
                             lambda: self.update_measure_box_outside(btn, "tool_rectangle.png", "矩形"))
        self.add_icon_action(menu, "tool_roi.png", "ROI",
                             lambda: self.update_measure_box_outside(btn, "tool_roi.png", "ROI"))

        tool = JMeasureTool(btn, btn, "measurebox")
        util.registe_view_tool(btn, "measurebox")
        self.tool_list.append(tool)
        return tool

    def update_measure_box_outside(self, btn, path, name):
        btn.toggled.disconnect()
        if name == "长度":
            # self.on_tool_line(True)
            btn.connect('toggled(bool)', self.on_measurebox_tool_line)
        if name == "角度":
            # self.on_tool_angle(True)
            btn.connect('toggled(bool)', self.on_measurebox_tool_angle)
        if name == "面积":
            # self.on_tool_area(True)
            btn.connect('toggled(bool)', self.on_measurebox_tool_area)
        if name == "曲线":
            # self.on_tool_area_open(True)
            btn.connect('toggled(bool)', self.on_measurebox_tool_area_open)
        if name == "矩形":
            btn.connect('toggled(bool)', self.on_measurebox_tool_plane)
        if name == "ROI":
            btn.connect('toggled(bool)', self.on_measurebox_tool_roi)
        # path = self.resourcePath(path).replace("\\", "/")
        # path = util.get_resource(path)
        # icon = qt.QPixmap(path).scaled(qt.QSize(32, 32), qt.Qt.KeepAspectRatio, qt.Qt.SmoothTransformation)
        # icon = qt.QIcon(icon)
        # btn.setIcon(icon)
        btn.setChecked(False)
        btn.setChecked(True)
        pic = util.findChild(btn, "labelPic")
        pixelmap_scaled = qt.QPixmap(util.get_resource(path))
        pixelmap_scaled = pixelmap_scaled.scaled(32, 32, 0, 1)
        pic.setPixmap(pixelmap_scaled)

    def on_measurebox_tool_roi(self, is_show):
        logic = util.getModuleLogic("Markups")
        if is_show:
            slicer.app.applicationLogic().GetInteractionNode().SetPlaceModePersistence(0)
            util.trigger_view_tool("measurebox")
            self.measure_flag = True
            areaNode = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLMarkupsROINode", "volume")
            util.GetDisplayNode(areaNode).SetHandlesInteractive(False)
            logic.SetActiveList(areaNode)
            areaNode.GetMeasurement('volume').SetEnabled(True)
            areaNode.AddObserver(vtk.vtkCommand.ModifiedEvent, self.OnInteractionModeChangedEvent)
            areaNode.SetAttribute("is_measure", "1")
            slicer.app.applicationLogic().GetInteractionNode().SetCurrentInteractionMode(
                slicer.vtkMRMLInteractionNode.Place)
            util.GetDisplayNode(areaNode).SetViewNodeIDs(util.viewNodeIDs)
            self.do_common_markups_setting(areaNode)
        else:
            self.measure_flag = False
            slicer.app.applicationLogic().GetInteractionNode().SetCurrentInteractionMode(2)

    def on_measurebox_tool_plane(self, is_show):
        logic = util.getModuleLogic("Markups")
        if is_show:
            slicer.app.applicationLogic().GetInteractionNode().SetPlaceModePersistence(0)
            util.trigger_view_tool("measurebox")
            self.measure_flag = True
            areaNode = util.CreateNodeByClass(util.vtkMRMLMarkupsPlaneNode)
            areaNode.SetSize(250, 250)
            util.AddNode(areaNode)
            areaNode.SetName("plane")
            logic.SetActiveList(areaNode)
            areaNode.GetMeasurement('area').SetEnabled(True)
            areaNode.AddObserver(vtk.vtkCommand.ModifiedEvent, self.OnInteractionModeChangedEvent)
            areaNode.SetAttribute("is_measure", "1")
            slicer.app.applicationLogic().GetInteractionNode().SetCurrentInteractionMode(
                slicer.vtkMRMLInteractionNode.Place)
            util.GetDisplayNode(areaNode).SetViewNodeIDs(util.viewNodeIDs)
            self.do_common_markups_setting(areaNode)

            planeNode = areaNode


        else:
            self.measure_flag = False
            slicer.app.applicationLogic().GetInteractionNode().SetCurrentInteractionMode(2)

    def on_measurebox_tool_area_open(self, is_show):

        logic = util.getModuleLogic("Markups")
        if is_show:
            slicer.app.applicationLogic().GetInteractionNode().SetPlaceModePersistence(0)
            util.trigger_view_tool("measurebox")
            self.measure_flag = True
            areaNode = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLMarkupsCurveNode", "area")
            areaNode.CreateDefaultDisplayNodes()
            areaNode.SetAttribute("is_measure", "1")
            logic.SetActiveList(areaNode)
            areaNode.GetMeasurement('length').SetEnabled(True)
            slicer.app.applicationLogic().GetInteractionNode().SetCurrentInteractionMode(
                slicer.vtkMRMLInteractionNode.Place)
        else:
            self.measure_flag = False
            slicer.app.applicationLogic().GetInteractionNode().SetCurrentInteractionMode(2)

    def on_measurebox_tool_line(self, is_show):

        logic = util.getModuleLogic("Markups")
        if is_show:
            slicer.app.applicationLogic().GetInteractionNode().SetPlaceModePersistence(0)
            util.trigger_view_tool("measurebox")
            self.measure_flag = True
            lineNode = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLMarkupsLineNode", "line")
            lineNode.SetAttribute("is_measure", "1")
            lineNode.CreateDefaultDisplayNodes()
            logic.SetActiveList(lineNode)
            lineNode.GetMeasurement('length').SetEnabled(True)
            slicer.app.applicationLogic().GetInteractionNode().SetCurrentInteractionMode(
                slicer.vtkMRMLInteractionNode.Place)
        else:
            self.measure_flag = False
            slicer.app.applicationLogic().GetInteractionNode().SetCurrentInteractionMode(2)

    def on_measurebox_tool_angle(self, is_show):

        logic = util.getModuleLogic("Markups")
        if is_show:
            slicer.app.applicationLogic().GetInteractionNode().SetPlaceModePersistence(0)
            util.trigger_view_tool("measurebox")
            self.measure_flag = True
            angleNode = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLMarkupsAngleNode", "angle")
            angleNode.CreateDefaultDisplayNodes()
            angleNode.SetAttribute("is_measure", "1")
            logic.SetActiveList(angleNode)
            slicer.app.applicationLogic().GetInteractionNode().SetCurrentInteractionMode(
                slicer.vtkMRMLInteractionNode.Place)
        else:
            self.measure_flag = False
            slicer.app.applicationLogic().GetInteractionNode().SetCurrentInteractionMode(2)

    def on_measurebox_tool_area(self, is_show):

        logic = util.getModuleLogic("Markups")
        if is_show:
            slicer.app.applicationLogic().GetInteractionNode().SetPlaceModePersistence(0)
            util.trigger_view_tool("measurebox")
            self.measure_flag = True
            areaNode = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLMarkupsClosedCurveNode", "area")
            areaNode.CreateDefaultDisplayNodes()
            areaNode.SetAttribute("is_measure", "1")
            logic.SetActiveList(areaNode)
            areaNode.GetMeasurement('length').SetEnabled(True)
            areaNode.GetMeasurement('area').SetEnabled(True)
            slicer.app.applicationLogic().GetInteractionNode().SetCurrentInteractionMode(
                slicer.vtkMRMLInteractionNode.Place)
        else:
            self.measure_flag = False
            slicer.app.applicationLogic().GetInteractionNode().SetCurrentInteractionMode(2)

    def get_extension(self):
        import configparser
        config = configparser.ConfigParser()

        with open(util.mainWindow().GetProjectIniPath().replace("\\", "/"), encoding='utf-8') as f:
            config.read_file(f)
            f.close()
        scene_extension = config.get('%General', 'scene_extension', fallback='mrb')
        print("scene_extension:", scene_extension)
        return scene_extension

    def add_tool_windowlevel_presets(self, parent):
        layout, btn = self.create_toolbutton(parent, "tool_windowlevel.png", "调整窗宽窗位", "W/L")
        menu = qt.QMenu(parent)
        btn.setMenu(menu)

        menu.addAction("CT_BONE", lambda: util.set_windowlevel(1000, 400))
        menu.addAction("CT_AIR", lambda: util.set_windowlevel(1000, -426))
        menu.addAction("CT-Brain", lambda: util.set_windowlevel(100, 50))
        menu.addAction("CT_ABDOMEN", lambda: util.set_windowlevel(350, 40))
        menu.addAction("CT_LUNG", lambda: util.set_windowlevel(1400, -500))
        menu.addAction("CT_Brain_Tissue", lambda: util.set_windowlevel(100, 20))
        tool = JMeasureTool(layout, btn, "test")
        self.tool_list.append(tool)
        return tool

    def add_tool_developer(self, parent):
        layout, btn = self.create_toolbutton(parent, "tool_setting.png", "其他", "其他")
        menu = qt.QMenu(parent)
        btn.setMenu(menu)

        menu.addAction("保存", lambda: util.saveScene(slicer.app.applicationDirPath() + "/bak/save.%s") % (
            self.get_extension()))
        menu.addAction("数据查看", lambda: util.send_event_str(util.SetPage, "1000"))
        menu.addAction("模型列表", lambda: self.change_to_test_style("JManagerModel"))
        # menu.addAction("Volumes",lambda:self.change_to_test_style("Volumes"))
        # menu.addAction("JBoneTexture",lambda:self.change_to_test_style("JBoneTexture"))
        # menu.addAction("BoneThicknessMapping",lambda:self.change_to_test_style("BoneThicknessMapping"))
        # menu.addAction("PedicleScrewSimulator",lambda:self.change_to_test_style("PedicleScrewSimulator"))
        # menu.addAction("VolumeRendering",lambda:self.change_to_test_style("VolumeRendering"))
        # menu.addAction("JBrainSegment",lambda:self.change_to_test_style("JBrainSegment"))
        # menu.addAction("SegmentEditor",lambda:self.change_to_test_style("SegmentEditor"))
        # menu.addAction("Segmentations",lambda:self.change_to_test_style("Segmentations"))
        # menu.addAction("Models",lambda:self.change_to_test_style("Models"))
        # menu.addAction("Markups",lambda:self.change_to_test_style("Markups"))
        # menu.addAction("ViewControllers",lambda:self.change_to_test_style("ViewControllers"))
        # menu.addAction("JAutoSegmentSpine",lambda:self.change_to_test_style("JAutoSegmentSpine"))
        # menu.addAction("ChatGPT",lambda:self.change_to_test_style("JChatGPT"))
        # menu.addAction("Elastix",lambda:self.change_to_test_style("Elastix"))
        # menu.addAction("RepairSkull",lambda:self.change_to_test_style("RepairSkull"))
        # menu.addAction("FiducialsToModelDistance",lambda:self.change_to_test_style("FiducialsToModelDistance"))
        for name1 in util.moduleNames():
            menu.addAction(name1, lambda b1=1, a1=name1: (print(a1), self.change_to_test_style(b1, a1)))
        tool = JMeasureTool(layout, btn, "test")
        self.tool_list.append(tool)
        return tool

    def change_to_test_style(self, k, style):
        print("switch to module:" + style)
        util.fresh_project_ui_frame()
        if self.orientation == "horizontal":
            util.show_right_style(right_module=style, middle_top_module="JMeasure", right_width=500, full_screen=True)
            # util.show_left_right_style(right_module=style)
        else:
            util.show_right_style(right_module=style, middle_right_module="JMeasure", right_width=500,
                                  middle_right_width=58, full_screen=True)
            # util.getModuleWidget(style).setFixedWidth(util.FixedWidth)
            # util.show_left_right_style(right_module=style)

    def add_tool_exit(self, parent):
        layout, btn = self.create_labeled_clicked_button(parent, "tool_exit.png", "退出当前案例", "退出")
        tool = JMeasureTool(layout, btn, "exit")
        self.tool_list.append(tool)
        btn.connect('clicked()', self.on_exit)
        return tool

    def on_exit(self):
        res = util.messageBox("退出将损失当前的所有数据,确认要退出当前操作吗", windowTitle="警告")
        if res == 0:
            return
        util.quit()

    def add_tool_minimum(self, parent):
        layout, btn = self.create_labeled_clicked_button(parent, "Clicked_Measure_Curve.png", "最小化", "最小化")
        tool = JMeasureTool(layout, btn, "minumum")
        self.tool_list.append(tool)
        btn.connect('clicked()', self.on_minumum)
        return tool

    def on_minumum(self):
        slicer.util.mainWindow().showMinimized()

    def add_tool_close_scene(self, parent):
        layout, btn = self.create_labeled_clicked_button(parent, "tool_close_scene.png",
                                                         "删除当前的所有数据,将软件重置为初始化状态", "清除")
        tool = JMeasureTool(layout, btn, "close_scene")
        self.tool_list.append(tool)
        btn.connect('clicked()', self.on_close_scene)
        return tool

    def on_close_scene(self):
        result = util.confirmOkCancelDisplay("确认将清除当前所有数据,是否继续?")
        if result == False:
            return
        util.close_scene()
        util.send_event_str(util.SetPage, "3")

    def add_tool_save(self, parent):
        layout, btn = self.create_labeled_clicked_button(parent, "tool_topmenu_save.png", "保存当前的进度", "保存")
        tool = JMeasureTool(layout, btn, "save")
        self.tool_list.append(tool)
        btn.connect('clicked()', self.on_save)
        return tool

    def on_save(self):
        import sqlite3
        from datetime import datetime
        import time
        if util.isPackage():
            fileName = qt.QFileDialog.getSaveFileName(None, ("保存文件"),
                                                      "/save.%s" % (self.get_extension()),
                                                      ("存档 (*.%s)" % (self.get_extension())))
            print("save file name is:", fileName)
            if fileName != "":
                filepath = fileName
            else:
                return
        else:
            # 获取当前时间戳
            timestamp = int(time.time())
            # 将时间戳转换为字符串
            project_name = util.getjson("project_name")
            timestamp_str = str(timestamp)
            filepath = os.path.join(util.mainWindow().GetProjectBasePath(), "ProjectCache", project_name, "mrbs",
                                    util.username, timestamp_str + ".mrb").replace('\\', '/')
            print("save file to:", filepath)
        util.send_event_str(util.ProgressStart, "正在保存")
        util.send_event_str(util.ProgressValue, 30)

        scene_node_name = "main_scene_view_save_node"
        scene_node = util.getFirstNodeByName(scene_node_name)
        if scene_node:
            util.RemoveNode(scene_node)
        util.getModuleLogic("SceneViews").CreateSceneView(scene_node_name, "abc", 1, vtk.vtkImageData())

        database_path = os.path.join(util.mainWindow().GetProjectBasePath(), "Resources", "Database", util.username,
                                     "ctkDICOM.sql")
        # 连接到数据库
        conn = sqlite3.connect(database_path)
        # 创建一个游标对象，用于执行 SQL 语句
        print(database_path, util.patient_uid, filepath, datetime.now(), datetime.now())
        cursor = conn.cursor()
        cursor.execute('INSERT INTO Analysis (PatientID, pathlist,recordtime,modifytime) VALUES (?, ?,?,?)',
                       (util.patient_uid, filepath, datetime.now(), datetime.now()))
        conn.commit()
        # 关闭连接
        conn.close()
        util.saveScene(filepath)
        util.send_event_str(util.ProgressValue, 100)
        util.showWarningText("文件保存至: " + filepath)

    def add_tool_setting(self, parent):
        layout, btn = self.create_labeled_clicked_button(parent, "tool_settings.png", "设置", " 设置")
        tool = JMeasureTool(layout, btn, "setting")
        self.tool_list.append(tool)
        btn.connect('clicked()', self.enter_setting)
        return tool

    def enter_setting(self):
        slicer.app.openSettingsDialog()

    def add_tool_extension(self, parent):
        layout, btn = self.create_labeled_clicked_button(parent, "tool_extension.png", "插件", " 插件")
        tool = JMeasureTool(layout, btn, "extension")
        self.tool_list.append(tool)
        btn.connect('clicked()', self.enter_extension)
        return tool

    def enter_extension(self):
        if util.getModuleWidget("JLogin").permission == 1:
            util.showWarningText("只有管理员才有权限使用")
        else:
            slicer.app.openExtensionsManagerDialog()

    def add_tool_chatgpt(self, parent):
        layout, btn = self.create_labeled_clicked_button(parent, "tool_chatgpt.png", "向chatgpt咨询问题", " gpt")
        tool = JMeasureTool(layout, btn, "chatgpt")
        self.tool_list.append(tool)
        btn.connect('clicked()', self.test_chatgpt)
        return tool

    def test_chatgpt(self):
        util.send_event_str(util.SetPage, util.ChageGPTPage)

    def add_tool_page_data(self, parent):

        layout, btn = self.create_labeled_clicked_button(parent, "tool_page_data.png", "进入数据加载页面", "数据库")
        tool = JMeasureTool(layout, btn, "page_data")
        self.tool_list.append(tool)
        btn.connect('clicked()', self.goto_page_data)
        return tool

    def goto_page_data(self):
        util.send_event_str(util.SetPage, 3)

    def add_tool_page_scan(self, parent):
        layout, btn = self.create_labeled_clicked_button(parent, "tool_page_scan.png", "进行CMF数据扫描页面", "扫描")
        tool = JMeasureTool(layout, btn, "page_scan")
        self.tool_list.append(tool)

        btn.connect('clicked()', self.goto_page_scan)

        return tool

    def goto_page_scan(self):
        # base_project_path = util.mainWindow().GetProjectBasePath()
        # exe_path = base_project_path+"/Resources/scan_folder/scan.exe"
        # if not os.path.exists(exe_path):
        #   util.showWarningText(exe_path+"《》不存在")
        #   return
        # util.mainWindow().ShowExtraPcocess(exe_path)
        util.show_gif_progress()
        util.send_event_str(util.SetPage, 7)
        util.singleShot(1000, lambda: util.hide_gif_progress())

    def add_tool_page_volumerendering(self, parent):
        layout, btn = self.create_labeled_clicked_button(parent, "tool_page_volumerendering.png", "进入三维重建页面",
                                                         "渲染")
        tool = JMeasureTool(layout, btn, "page_volumerendering")
        self.tool_list.append(tool)
        btn.connect('clicked()', self.goto_page_volumerendering)
        return tool

    def goto_page_volumerendering(self):
        util.show_gif_progress()
        util.send_event_str(util.SetPage, 4)
        util.singleShot(1000, lambda: util.hide_gif_progress())

    def add_tool_page_cmf(self, parent):
        layout, btn = self.create_labeled_clicked_button(parent, "tool_page_cmf.png", "进入CMF页面", "全景")
        tool = JMeasureTool(layout, btn, "page_cmf")
        self.tool_list.append(tool)
        btn.connect('clicked()', self.goto_page_cmf)
        return tool

    def goto_page_cmf(self):
        util.show_gif_progress()
        util.send_event_str(util.SetPage, 5)
        util.singleShot(1000, lambda: util.hide_gif_progress())

    def add_tool_page_roi(self, parent):
        layout, btn = self.create_labeled_clicked_button(parent, "tool_page_roi.png", "进入ROI页面", "ROI")
        tool = JMeasureTool(layout, btn, "page_roi")
        self.tool_list.append(tool)
        btn.connect('clicked()', self.goto_page_roi)
        return tool

    def goto_page_roi(self):
        util.show_gif_progress()
        util.send_event_str(util.SetPage, 6)
        util.singleShot(1000, lambda: util.hide_gif_progress())

    def clear_cmf_stylesheet(self, inname):
        ilist = ["page_roi", "page_cmf", "page_volumerendering", "page_scan", "page_data"]

        btnScissors_stylesheet = ""
        btnScissors_stylesheet = btnScissors_stylesheet + "QPushButton{background-color: #333333;}"
        btnScissors_stylesheet = btnScissors_stylesheet + "QPushButton:hover{background-color: rgb(70, 70, 70);}"
        btnScissors_stylesheet = btnScissors_stylesheet + "QPushButton{background-color: #333333;}"

        btnScissors_style2sheet = ""
        btnScissors_style2sheet = btnScissors_style2sheet + "QPushButton{background-color: rgb(151, 151, 151);}"
        btnScissors_style2sheet = btnScissors_style2sheet + "QPushButton:hover{background-color: rgb(70, 70, 70);}"
        btnScissors_style2sheet = btnScissors_style2sheet + "QPushButton{background-color: rgb(151, 151, 151);}"
        for name in ilist:
            tool = self.get_tool_by_name(name)
            if tool.label == inname:
                tool.btn.setStyleSheet(btnScissors_style2sheet)
            else:
                tool.btn.setStyleSheet(btnScissors_stylesheet)

    def add_tool_chatgpt(self, parent):
        layout, btn = self.create_labeled_clicked_button(parent, "tool_chatgpt.png", "向chatgpt咨询问题", " gpt")
        tool = JMeasureTool(layout, btn, "chatgpt")
        self.tool_list.append(tool)
        btn.connect('clicked()', self.test_chatgpt)
        return tool

    def test_chatgpt(self):
        util.send_event_str(util.SetPage, util.ChageGPTPage)

    def add_tool_load(self, parent):
        layout, btn = self.create_labeled_clicked_button(parent, "tool_topmenu_load.png", "加载之前的进度", "加载")
        tool = JMeasureTool(layout, btn, "load")
        self.tool_list.append(tool)
        btn.connect('clicked()', self.on_load)
        return tool

    def on_load(self):
        util.close_scene()
        if util.JsonData is None:
            filepath = (os.path.join(util.mainWindow().GetProjectBasePath(), "Resources", "save.%s") % (
                self.get_extension())).replace('\\', '/')
        else:
            project_name = util.getjson("project_name")
            filepath = (os.path.join(util.mainWindow().GetProjectBasePath(), "ProjectCache", project_name,
                                     "save.%s") % (self.get_extension())).replace('\\', '/')
        print("load file path:", filepath)
        settings = qt.QSettings()
        default_path = settings.value("General/default_path")
        if default_path == "" or default_path is None:
            default_path = os.path.join(util.mainWindow().GetProjectBasePath(), "Resources").replace('\\', '/')
        if util.isPackage():
            file_dialog = qt.QFileDialog()
            file_dialog.setDirectory(default_path)
            file_dialog.setNameFilter('files (*.%s)' % (self.get_extension()))  # 过滤器，只显示后缀名为.mrb的文件
            file_dialog.setFileMode(0)  # 设置打开文件模式
            if file_dialog.exec_():
                # 获取所选文件的路径
                fileName = file_dialog.selectedFiles()[0]
                if fileName != "":
                    filepath = fileName
                else:
                    return
            else:
                return

        if not qt.QFile(filepath).exists():
            util.showWarningText("当前文件不存在: " + filepath)
            return
        self._onload(filepath)

    def _onload(self, filepath):
        try:
            util.loadScene(filepath)
        except Exception as e:
            print("mrb load with exception:" + e.__str__())
        util.send_event_str(util.ArchiveFileLoadedEvent, "1")

        current_page = util.GetGlobalSaveValue("current_page")
        print("_onload current_page:", current_page)
        if current_page is None:
            util.send_event_str(util.SetPage, 2)
        elif int(current_page) < 2:
            util.send_event_str(util.SetPage, 2)
        else:
            util.send_event_str(util.SetPage, current_page)

        scene_node_name = "main_scene_view_save_node"
        scene_view_node = util.getFirstNodeByName(scene_node_name)
        if scene_view_node:
            util.getModuleLogic("SceneViews").RestoreSceneView(scene_view_node.GetID(), False)

    def add_tool_layout(self, parent):
        layout, btn = self.create_toolbutton(parent, "tool_layout.png", "更改布局", "布局")
        menu = qt.QMenu(parent)
        btn.setMenu(menu)

        datas = []
        page_action = None
        datas = util.getjson("layout", "")
        first_id = None
        for data in datas:
            info = util.getcustomjson(data, "info")
            id = int(util.getcustomjson(data, "id"))
            if not first_id:
                first_id = id
            menu.addAction(info, lambda a, v1=id: self.on_choose_layout(a, v1))
        tool = JMeasureTool(layout, btn, "layout")
        self.tool_list.append(tool)
        btn.connect('clicked()', lambda: self.on_choose_layout("", first_id))
        return tool

    def on_choose_layout(self, a, page):
        print("on choose page:", a, page)
        slicer.app.layoutManager().setLayout(page)

    '''
    旋转工具
  '''

    def add_whirling_tool(self, parent):
        layout, btn = self.create_labeled_checkable_button(parent, "tool_whirling.png", "tool_whirling.png",
                                                           "拖动十字线进行旋转", "MPR")
        tool = JMeasureTool(layout, btn, "whirling")
        self.tool_list.append(tool)
        btn.connect('toggled(bool)', self.on_whirling)
        # util.singleShot(10,lambda:btn.setChecked(True))
        # util.registe_view_tool(btn,"whirling")
        return tool

    def on_whirling(self, is_show):
        print("on_whirling:", is_show)
        if is_show:
            util.trigger_view_tool("whirling")
        slicer.app.applicationLogic().SetIntersectingSlicesEnabled(
            slicer.vtkMRMLApplicationLogic.IntersectingSlicesVisibility, is_show)
        slicer.app.applicationLogic().SetIntersectingSlicesEnabled(
            slicer.vtkMRMLApplicationLogic.IntersectingSlicesInteractive, is_show)
        displayNodes = util.getNodesByClass("vtkMRMLSliceDisplayNode")
        for displayNode in displayNodes:
            displayNode.SetIntersectingSlicesLineThicknessMode(2)
        sliceNodes = util.getNodesByClass("vtkMRMLSliceNode")
        for sliceNode in sliceNodes:
            sliceNode.Modified()

    def on_normal(self):
        util.trigger_view_tool("")

    '''
    通过框选来调整窗宽床位的工具
  '''

    def add_WindowLevel_tool(self, parent):
        layout, btn = self.create_labeled_checkable_button(parent, "tool_grayscale.png", "tool_grayscale.png",
                                                           "框选二维视图中感兴趣的区域来更改窗宽床位", "灰度")
        tool = JMeasureTool(layout, btn, "windowlevel_auto")
        self.tool_list.append(tool)
        btn.connect('toggled(bool)', self.on_windowlevel_auto)
        util.registe_view_tool(btn, "windowlevel_auto")
        return tool

    def on_windowlevel_auto(self, is_show):
        print(is_show)
        if is_show:
            util.trigger_view_tool("windowlevel_auto")
            slicer.app.applicationLogic().GetInteractionNode().SetAttribute("AdjustWindowLevelMode", "Rectangle")
            slicer.app.applicationLogic().GetInteractionNode().SetCurrentInteractionMode(
                slicer.vtkMRMLInteractionNode.AdjustWindowLevel)

        else:
            slicer.app.applicationLogic().GetInteractionNode().SetCurrentInteractionMode(2)

    '''
    重置工具
  '''

    def add_reset_tool(self, parent):
        layout, btn = self.create_labeled_clicked_button(parent, "tool_reset.png", "将所有窗口的显示重置为初始状态",
                                                         "重置")
        tool = JMeasureTool(layout, btn, "reset")
        self.tool_list.append(tool)
        btn.connect('clicked()', self.on_reset)
        return tool

    def on_reset(self):
        util.reinit(ori=True)
        util.trigger_view_tool("")
        util.forceRenderAllViews()

    '''
    显示窗宽窗位的头骨部分
  '''

    def add_WindowLevel_bone(self, parent):
        layout, btn = self.create_labeled_clicked_button(parent, "tool_windowlevel_bone.png", "显示骨窗", "骨窗")
        tool = JMeasureTool(layout, btn, "windowlevel_bone")
        self.tool_list.append(tool)
        btn.connect('clicked()', self.on_windowlevel_bone)
        return tool

    def on_windowlevel_bone(self):
        applicationLogic = slicer.app.applicationLogic()
        selectionNode = applicationLogic.GetSelectionNode()
        if not selectionNode:
            print("selection node is None2")
            return
        volumeid = selectionNode.GetActiveVolumeID()
        if not volumeid:
            return
        node = util.GetNodeByID(volumeid)
        if not node:
            print("selection node is None")
            return
        displaynode = node.GetDisplayNode()
        if not displaynode:
            print("selection node display node is None")
            return
        displaynode.AutoWindowLevelOff()
        displaynode.SetWindow(1250)
        displaynode.SetLevel(300)

    '''
    显示窗宽窗位的头骨部分
  '''

    def add_WindowLevel_tissue(self, parent):
        layout, btn = self.create_labeled_clicked_button(parent, "tool_windowlevel_tissue.png", "显示软组织的窗宽窗位",
                                                         "软组织窗")
        tool = JMeasureTool(layout, btn, "windowlevel_tissue")
        self.tool_list.append(tool)
        btn.connect('clicked()', self.on_windowlevel_tissue)
        return tool

    def on_windowlevel_tissue(self):
        applicationLogic = slicer.app.applicationLogic()
        selectionNode = applicationLogic.GetSelectionNode()
        if not selectionNode:
            return
        volumeid = selectionNode.GetActiveVolumeID()
        node = util.GetNodeByID(volumeid)
        if not node:
            print("selection node is None")
            return
        displaynode = node.GetDisplayNode()
        if not displaynode:
            print("selection node display node is None")
            return
        displaynode.AutoWindowLevelOff()
        displaynode.SetWindow(91)
        displaynode.SetLevel(24)

    '''
    测量长度的工具
  '''

    def add_line_tool(self, parent):
        layout, btn = self.create_labeled_checkable_button(parent, "tool_line.png", "tool_line.png", "测量长度的工具",
                                                           "线段")
        tool = JMeasureTool(layout, btn, "tool_line")
        self.tool_list.append(tool)
        btn.connect('toggled(bool)', self.on_tool_line)
        util.registe_view_tool(btn, "tool_line")
        return tool

    def on_tool_line(self, is_show):
        logic = util.getModuleLogic("Markups")
        if is_show:
            util.trigger_view_tool("tool_line")
            lineNode = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLMarkupsLineNode", "line")
            lineNode.CreateDefaultDisplayNodes()
            dn = lineNode.GetDisplayNode()
            logic.SetActiveList(lineNode)
            # Use crosshair glyph to allow more accurate point placement
            self.do_common_markups_setting(lineNode)
            # Hide measurement result while markup up
            lineNode.GetMeasurement('length').SetEnabled(True)
            util.GetDisplayNode(lineNode).SetViewNodeIDs(util.viewNodeIDs)
            slicer.app.applicationLogic().GetInteractionNode().SetCurrentInteractionMode(
                slicer.vtkMRMLInteractionNode.Place)
        else:
            slicer.app.applicationLogic().GetInteractionNode().SetCurrentInteractionMode(2)

    @vtk.calldata_type(vtk.VTK_OBJECT)
    def OnNodeRemovedEvent(self, caller, str_event, calldata):
        node = calldata
        if isinstance(node, slicer.vtkMRMLMarkupsNode):
            self.OnInteractionModeChangedEvent(caller, str_event)

    def OnMarkupsComplete(self, markups_node):
        id = markups_node.GetID()
        if markups_node.GetAttribute("scene_view_node_id") is None:
            scene_view_node_name = util.generate_random_string()
            util.getModuleLogic("SceneViews").CreateSceneView(scene_view_node_name, "measure scene view", 4,
                                                              vtk.vtkImageData())
            scene_view_node = util.getFirstNodeByExactName(scene_view_node_name)
            slicer.app.applicationLogic().GetInteractionNode().RemoveObserver(
                slicer.vtkMRMLInteractionNode.InteractionModeChangedEvent)
            markups_node.SetAttribute("scene_view_node_id", scene_view_node.GetID())
            slicer.app.applicationLogic().GetInteractionNode().AddObserver(
                slicer.vtkMRMLInteractionNode.InteractionModeChangedEvent, self.OnInteractionModeChangedEvent)
        util.trigger_view_tool("")
        util.send_event_str(util.MarkupsModified)

    def OnInteractionModeChangedEvent(self, caller, event):
        selectionNode = slicer.mrmlScene.GetNodeByID("vtkMRMLSelectionNodeSingleton")
        markups_node_id = selectionNode.GetActivePlaceNodeID()
        interaction_node = slicer.app.applicationLogic().GetInteractionNode()
        CurrentInteractionMode = interaction_node.GetCurrentInteractionMode()
        ActiveListID = util.getModuleLogic("Markups").GetActiveListID()
        tool = self.get_tool_by_name("measurebox")
        if CurrentInteractionMode == slicer.vtkMRMLInteractionNode.ViewTransform:
            if self.measure_flag:
                tool.btn.setChecked(False)

            if markups_node_id:
                markups_node = util.GetNodeByID(markups_node_id)
                if markups_node and markups_node.IsA("vtkMRMLMarkupsPlaneNode"):
                    if util.get_from_PAAA("current_project_selector_project_name") != "PResearchPlatform1":
                        planeNode = markups_node
                        # 设置Normal不可见
                        util.GetDisplayNode(planeNode).SetNormalVisibility(False)
                        util.GetDisplayNode(planeNode).SetNormalOpacity(0)
                        # 设置文字不可见
                        util.GetDisplayNode(planeNode).SetTextScale(0)
                        # 设置中心点不可见
                        planeNode.SetNthControlPointVisibility(0, False)
                        # 设置Label不可见
                        util.GetDisplayNode(planeNode).SetPropertiesLabelVisibility(False)

                        if util.get_from_PAAA("current_project_selector_project_name") == "PResearchPlatform":
                            # 设置边缘的几个点可见
                            util.GetDisplayNode(planeNode).SetHandlesInteractive(True)
                            # 设置中心点不可见
                            util.GetDisplayNode(planeNode).SetGlyphScale(0.1)
                            # 设置填充的透明度
                            util.GetDisplayNode(planeNode).SetFillOpacity(0)
                            # 设置边缘的透明度
                            util.GetDisplayNode(planeNode).SetOutlineOpacity(0.5)
                if markups_node:
                    self.OnMarkupsComplete(markups_node)
                else:
                    print("empty markups node")
        # if "JManagerMarkups" in util.moduleNames():
        #   util.getModuleWidget("JManagerMarkups").inner_manager.fresh_list()
        return
        # if CurrentInteractionMode == slicer.vtkMRMLInteractionNode.Place:
        #  if ActiveListID is not None:

        if CurrentInteractionMode == slicer.vtkMRMLInteractionNode.Place:
            util.showWarningText("Place:" + ActiveListID)
        elif CurrentInteractionMode == slicer.vtkMRMLInteractionNode.ViewTransform:
            util.showWarningText("ViewTransform:" + ActiveListID)
        elif CurrentInteractionMode == slicer.vtkMRMLInteractionNode.AdjustWindowLevel:
            util.showWarningText("AdjustWindowLevel:" + ActiveListID)
        elif CurrentInteractionMode == slicer.vtkMRMLInteractionNode.Select:
            util.showWarningText("Select:" + ActiveListID)
        elif CurrentInteractionMode == slicer.vtkMRMLInteractionNode.User:
            util.showWarningText("User:" + ActiveListID)
        else:
            util.showWarningText("No Region:" + "," + CurrentInteractionMode + "," + ActiveListID)

    '''
    测量角度的工具
  '''

    def add_angle_tool(self, parent):
        layout, btn = self.create_labeled_checkable_button(parent, "tool_angle.png", "tool_angle.png", "测量角度的工具",
                                                           "角度")
        tool = JMeasureTool(layout, btn, "tool_angle")
        self.tool_list.append(tool)
        btn.connect('toggled(bool)', self.on_tool_angle)
        util.registe_view_tool(btn, "tool_angle")
        return tool

    def on_tool_angle(self, is_show):
        logic = util.getModuleLogic("Markups")
        if is_show:
            util.trigger_view_tool("tool_angle")
            angleNode = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLMarkupsAngleNode", "angle")
            angleNode.CreateDefaultDisplayNodes()
            util.GetDisplayNode(angleNode).SetViewNodeIDs(util.viewNodeIDs)
            dn = angleNode.GetDisplayNode()
            logic.SetActiveList(angleNode)
            self.do_common_markups_setting(angleNode)
            # Use crosshair glyph to allow more accurate point placement

            # Hide measurement result while markup up
            slicer.app.applicationLogic().GetInteractionNode().SetCurrentInteractionMode(
                slicer.vtkMRMLInteractionNode.Place)
        else:
            slicer.app.applicationLogic().GetInteractionNode().SetCurrentInteractionMode(2)

    '''
    测量面积的工具
  '''

    def add_area_tool(self, parent):
        layout, btn = self.create_labeled_checkable_button(parent, "teasure_area.png", "teasure_area.png",
                                                           "测量面积的工具", "面积")
        tool = JMeasureTool(layout, btn, "tool_area")
        self.tool_list.append(tool)
        btn.connect('toggled(bool)', self.on_tool_area)
        util.registe_view_tool(btn, "tool_area")
        return tool

    def on_tool_area(self, is_show):
        logic = util.getModuleLogic("Markups")
        if is_show:
            util.trigger_view_tool("tool_area")
            areaNode = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLMarkupsClosedCurveNode", "area")
            areaNode.CreateDefaultDisplayNodes()
            dn = areaNode.GetDisplayNode()
            logic.SetActiveList(areaNode)
            # Use crosshair glyph to allow more accurate point placement
            self.do_common_markups_setting(areaNode)
            # Hide measurement result while markup up
            areaNode.GetMeasurement('length').SetEnabled(True)
            areaNode.GetMeasurement('area').SetEnabled(True)
            util.GetDisplayNode(areaNode).SetViewNodeIDs(util.viewNodeIDs)
            slicer.app.applicationLogic().GetInteractionNode().SetCurrentInteractionMode(
                slicer.vtkMRMLInteractionNode.Place)

        else:
            slicer.app.applicationLogic().GetInteractionNode().SetCurrentInteractionMode(2)

    '''
    曲线测量长度
  '''

    def add_area_open_tool(self, parent):
        layout, btn = self.create_labeled_checkable_button(parent, "tool_measure.png", "tool_measure.png",
                                                           "测量长度的工具,左键选择曲线,右键取消", "长度")
        tool = JMeasureTool(layout, btn, "tool_curve")
        self.tool_list.append(tool)
        btn.connect('toggled(bool)', self.on_tool_area_open)
        util.registe_view_tool(btn, "tool_curve")
        return tool

    def on_tool_area_open(self, is_show):
        logic = util.getModuleLogic("Markups")
        if is_show:
            util.trigger_view_tool("tool_curve")
            areaNode = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLMarkupsCurveNode", "area")
            areaNode.CreateDefaultDisplayNodes()
            dn = areaNode.GetDisplayNode()
            logic.SetActiveList(areaNode)
            # Use crosshair glyph to allow more accurate point placement
            util.GetDisplayNode(areaNode).SetViewNodeIDs(util.viewNodeIDs)
            self.do_common_markups_setting(areaNode)
            # Hide measurement result while markup up
            areaNode.GetMeasurement('length').SetEnabled(True)
            slicer.app.applicationLogic().GetInteractionNode().SetCurrentInteractionMode(
                slicer.vtkMRMLInteractionNode.Place)
        else:
            slicer.app.applicationLogic().GetInteractionNode().SetCurrentInteractionMode(2)

    '''
    联系开发者
  '''

    def add_tool_contact_developer(self, parent):
        layout, btn = self.create_labeled_clicked_button(parent, "contact_wechat.png", "联系开发者", "开发支持")
        tool = JMeasureTool(layout, btn, "tool_contact_developer")
        self.tool_list.append(tool)
        btn.connect('clicked()', self.on_contact_developer)
        return tool

    def on_contact_developer(self):
        image_path = self.resourcePath(('software_support.png')).replace('\\', '/')
        dlg = qt.QDialog()
        dlg.setWindowTitle("获取技术支持请加微信")
        dlg.setWindowIcon(qt.QIcon(self.resourcePath(('software_support.png')).replace('\\', '/')))
        dlg.setWindowFlags(dlg.windowFlags() & ~0x00010000)
        dlg.setModal(True)
        l = qt.QHBoxLayout(dlg)
        image = qt.QLabel()
        l.addWidget(image)
        image.setPixmap(qt.QPixmap(image_path))
        dlg.exec()

    def add_tool_contact_doctor(self, parent):
        layout, btn = self.create_labeled_clicked_button(parent, "contact_gongzhonghao.png", "获取临床支持", "临床支持")
        tool = JMeasureTool(layout, btn, "tool_contact_doctor")
        self.tool_list.append(tool)
        btn.connect('clicked()', self.on_contact_doctor)
        return tool

    def on_contact_doctor(self):
        image_path = self.resourcePath(('doctor_support.png')).replace('\\', '/')
        dlg = qt.QDialog()
        dlg.setWindowTitle("获取临床支持请加公众号")
        dlg.setWindowIcon(qt.QIcon(self.resourcePath(('doctor_support.png')).replace('\\', '/')))
        dlg.setWindowFlags(dlg.windowFlags() & ~0x00010000)
        dlg.setModal(True)
        l = qt.QHBoxLayout(dlg)
        image = qt.QLabel()
        l.addWidget(image)
        image.setPixmap(qt.QPixmap(image_path))
        dlg.exec()

    def add_tool_screenshot(self, parent):
        layout, btn = self.create_labeled_clicked_button(parent, "tool_screen_shot.png", "截图", "截图")
        tool = JMeasureTool(layout, btn, "tool_screenshot")
        self.tool_list.append(tool)
        btn.connect('clicked()', self.on_tool_screenshot)
        return tool

    def on_tool_screenshot(self):
        util.mainWindow().GetCaptureToolBar().screenshotButtonClicked()
        return

    def add_tool_controller(self, parent):
        layout, btn = self.create_labeled_clicked_button(parent, "tool_show_controller.png", "是否显示四视图上的控制栏",
                                                         "控制栏")
        tool = JMeasureTool(layout, btn, "tool_controller")
        self.tool_list.append(tool)
        btn.connect('clicked()', self.on_tool_controller)
        return tool

    def on_tool_controller(self):
        lm = slicer.app.layoutManager()
        vis = lm.threeDWidget(0).threeDController().visible
        util.setViewControllersVisible(not vis)

    def add_tool_jpacs(self, parent):
        layout, btn = self.create_labeled_clicked_button(parent, "tool_data_loader.png", "返回到数据加载的页面", "数据")
        tool = JMeasureTool(layout, btn, "tool_jpacs")
        self.tool_list.append(tool)
        btn.connect('clicked()', self.on_tool_jpacs)
        return tool

    def on_tool_jpacs(self):
        util.send_event_str(util.SetPage, 3)

    def add_tool_handeye(self, parent):
        layout, btn = self.create_labeled_clicked_button(parent, "tool_handleye.png", "进行手眼标定", "手眼\n标定")
        tool = JMeasureTool(layout, btn, "tool_light")
        self.tool_list.append(tool)
        btn.connect('clicked()', self.on_tool_handeye)
        return tool

    def on_tool_handeye(self):
        # util.showWarningText("正在进行手眼标定")
        util.getModuleWidget("JRobotNDI").start_hand_eye()

    def add_tool_tick(self, parent):
        layout, btn = self.create_labeled_checkable_button(parent, "tool_show_controller.png",
                                                           "tool_show_controller.png", "Tick", "Tick")
        tool = JMeasureTool(layout, btn, "tool_tick")
        self.tool_list.append(tool)
        btn.setCheckable(True)
        btn.connect('toggled(bool)', self.on_tool_tick)
        return tool

    def on_tool_tick(self, is_show):
        if is_show:
            import random
            random_float = random.uniform(0, 3)
            util.getModule("Tick").start_thread(1)
        else:
            util.getModule("Tick").pause_thread()

    def add_tool_ime(self, parent):
        layout, btn = self.create_labeled_checkable_button(parent, "tool_light_on.png", "tool_light_off.png", "NDI显示",
                                                           "NDI")
        tool = JMeasureTool(layout, btn, "tool_ime")
        self.tool_list.append(tool)
        btn.setCheckable(True)
        btn.connect('toggled(bool)', self.on_tool_ime)
        return tool

    def on_tool_ime(self, is_show):
        # util.showWarningText("正在进行手眼标定")
        widget = util.getModuleWidget("JNDIConnector").ui.widget
        if is_show:
            qwidget = qt.QWidget()
            qwidget.setParent(slicer.app.layoutManager().sliceWidget("Red+"))
            util.addWidget2(qwidget, widget)
            qwidget.geometry = util.getModuleWidget("RDNTreat").treat_layout.get_ndi_layout()
            qwidget.show()
        else:
            widget.setParent(None)

    def fresh_threeD_gui(self, in_name):
        return
        if in_name != "tool_elibot":
            tool = self.get_tool_by_name("tool_elibot")
            tool.btn.setChecked(False)
        if in_name != "tool_ime":
            tool = self.get_tool_by_name("tool_ime")
            tool.btn.setChecked(False)

    def add_tool_usb(self, parent):
        layout, btn = self.create_labeled_checkable_button(parent, "tool_scale_on.png", "tool_scale_off.png", "控制USB",
                                                           "USB")
        tool = JMeasureTool(layout, btn, "tool_usb")
        self.tool_list.append(tool)
        btn.setCheckable(True)
        btn.connect('toggled(bool)', self.on_tool_usb)
        return tool

    def on_tool_usb(self, is_show):
        widget = util.getModuleWidget("JUSBConnector").ui.widget
        if is_show:
            self.fresh_threeD_gui("tool_elibot")
            qwidget = qt.QWidget()
            qwidget.setParent(slicer.app.layoutManager().sliceWidget("Red+"))
            # qwidget.setParent(slicer.app.layoutManager().threeDWidget(0).threeDView())
            util.addWidget2(qwidget, widget)
            qwidget.geometry = util.getModuleWidget("RDNTreat").treat_layout.get_usb_layout()
            qwidget.show()
        else:
            widget.setParent(None)

    def add_tool_elibot(self, parent):
        layout, btn = self.create_labeled_checkable_button(parent, "tool_scale_on.png", "tool_scale_off.png",
                                                           "机械臂控制面板", "机械臂")
        tool = JMeasureTool(layout, btn, "tool_elibot")
        self.tool_list.append(tool)
        btn.setCheckable(True)
        btn.connect('toggled(bool)', self.on_tool_elibot)
        return tool

    def on_tool_elibot(self, is_show):
        # util.showWarningText("正在进行手眼标定")
        widget = util.getModuleWidget("JRobotArm").ui.widget
        if is_show:
            self.fresh_threeD_gui("tool_elibot")
            qwidget = qt.QWidget()
            qwidget.setParent(slicer.app.layoutManager().sliceWidget("Red+"))
            # qwidget.setParent(slicer.app.layoutManager().threeDWidget(0).threeDView())
            util.addWidget2(qwidget, widget)
            qwidget.geometry = util.getModuleWidget("RDNTreat").treat_layout.get_robot_layout()
            qwidget.show()
        else:
            widget.setParent(None)

    def add_tool_register(self, parent):
        layout, btn = self.create_labeled_clicked_button(parent, "tool_volumerendering_recorder.png", "配准", "配准")
        tool = JMeasureTool(layout, btn, "tool_register")
        self.tool_list.append(tool)
        btn.connect('clicked()', self.on_tool_register)
        return tool

    def on_tool_register(self):
        util.getModuleWidget("JRobotNDI").start_register()

    def add_tool_light(self, parent):
        layout, btn = self.create_labeled_checkable_button(parent, "tool_light_on.png", "tool_light_off.png",
                                                           "添加渲染阴影", "光照")
        tool = JMeasureTool(layout, btn, "tool_light")
        self.tool_list.append(tool)
        btn.connect('toggled(bool)', self.on_tool_hide_light)
        return tool

    def on_tool_hide_light(self, is_show):
        util.getModuleLogic("Lights").setUseSSAO(True)
        layoutManager = slicer.app.layoutManager()
        for threeDViewIndex in range(layoutManager.threeDViewCount):
            viewNode = layoutManager.threeDWidget(threeDViewIndex).mrmlViewNode()
            if is_show:
                util.getModuleLogic("Lights").addManagedView(viewNode)
            else:
                util.getModuleLogic("Lights").removeManagedView(viewNode)
                # 没有作用
                # threeD_view_background_color = util.getjson("threeD_view_background_color","0|0|0")
                # tl = threeD_view_background_color.split("|")
                # threeD_view_background_color2 = util.getjson("threeD_view_background_color2","0|0|0")
                # tl2 = threeD_view_background_color2.split("|")
                # util.singleShot(1000,lambda:viewNode.SetBackgroundColor(float(tl[0]),float(tl[1]),float(tl[2])))
                # util.singleShot(1000,lambda:viewNode.SetBackgroundColor2(float(tl2[0]),float(tl2[1]),float(tl2[2])))

    def add_tool_scale(self, parent):
        layout, btn = self.create_labeled_checkable_button(parent, "tool_scale_on.png", "tool_scale_off.png",
                                                           "最大化视图区域", "展示")
        tool = JMeasureTool(layout, btn, "tool_scale")
        self.tool_list.append(tool)
        btn.connect('toggled(bool)', self.on_tool_hide_scale)
        return tool

    def on_tool_hide_scale(self, is_show):
        util.main_panel.setVisible(not is_show)

    def add_tool_load_volume_paras(self, parent):
        import json
        file_name = util.get_resource("volumerendering.json")
        data = {}
        data["paras"] = []
        try:
            if os.path.exists(file_name):
                with open(file_name, "r") as json_file:
                    data = json.load(json_file)
        except Exception as e:
            pass
        layout, btn = self.create_toolbutton(parent, "tool_volumerendering_list.png", "读取体绘制的参数", "体绘制")
        menu = qt.QMenu(parent)
        btn.setMenu(menu)

        json1 = None
        for data1 in data["paras"]:
            json1 = data1
            break
        if json1:
            btn.setCheckable(False)
            btn.connect('clicked()', lambda: self.on_choose_volume_paras(0, 0, json1))

        index = 0
        for data1 in data["paras"]:
            sub_json_data = data1
            menu.addAction(f"模式{index}", lambda a, v1=index, v2=sub_json_data: self.on_choose_volume_paras(a, v1, v2))
            index += 1

        tool = JMeasureTool(layout, btn, "load_volume_paras")
        self.tool_list.append(tool)
        return tool

    def on_choose_volume_paras(self, _, index, json_data):
        print("on_choose_volume_paras:", json_data)
        import json
        volumeNode = util.getFirstNodeByClass(util.vtkMRMLVolumeNode)
        if volumeNode is None:
            return
        volRenLogic = slicer.modules.volumerendering.logic()
        displayNode = volRenLogic.GetFirstVolumeRenderingDisplayNode(volumeNode)
        if not displayNode:
            displayNode = volRenLogic.CreateDefaultVolumeRenderingNodes(volumeNode)

        gradientOpacityTransferFunction = displayNode.GetVolumePropertyNode().GetVolumeProperty().GetGradientOpacity()
        gradientOpacityTransferFunction.RemoveAllPoints()
        GradientOpacityJsonData = json_data["GradientOpacity"]
        for data in GradientOpacityJsonData:
            for key in data:
                val = data[key]
                if len(val) != 4:
                    util.showWarningText("json文件损坏")
                    return
                gradientOpacityTransferFunction.AddPoint(val[0], val[1], val[2], val[3])

        scalarOpacityTransferFunction = displayNode.GetVolumePropertyNode().GetVolumeProperty().GetScalarOpacity()
        scalarOpacityTransferFunction.RemoveAllPoints()
        ScalarOpacityData = json_data["ScalarOpacity"]
        for data in ScalarOpacityData:
            for key in data:
                val = data[key]
                if len(val) != 4:
                    util.showWarningText("json文件损坏")
                    return
                scalarOpacityTransferFunction.AddPoint(val[0], val[1], val[2], val[3])

        RGBTransferFunction = displayNode.GetVolumePropertyNode().GetVolumeProperty().GetRGBTransferFunction()
        RGBTransferFunction.RemoveAllPoints()
        RGBTransferFunctionData = json_data["RGBTransferFunction"]
        for data in RGBTransferFunctionData:
            for key in data:
                val = data[key]
                if len(val) != 6:
                    util.showWarningText("json文件损坏")
                    return
                RGBTransferFunction.AddRGBPoint(val[0], val[1], val[2], val[3], val[4], val[5])

    def add_tool_save_volume_paras(self, parent):
        layout, btn = self.create_labeled_clicked_button(parent, "tool_volumerendering_recorder.png",
                                                         "记录体绘制的参数", "体参")
        tool = JMeasureTool(layout, btn, "save_volume_paras")
        self.tool_list.append(tool)
        btn.connect('clicked()', self.on_tool_save_volume_paras)
        return tool

    def on_tool_save_volume_paras(self):
        import json
        volumeNode = util.getFirstNodeByClass(util.vtkMRMLScalarVolumeNode)
        if not volumeNode:
            return
        volRenLogic = slicer.modules.volumerendering.logic()
        displayNode = volRenLogic.GetFirstVolumeRenderingDisplayNode(volumeNode)
        if not displayNode:
            displayNode = volRenLogic.CreateDefaultVolumeRenderingNodes(volumeNode)
        # Set up gradient vs opacity transfer function
        json_data = {}
        gradientOpacityTransferFunction = displayNode.GetVolumePropertyNode().GetVolumeProperty().GetGradientOpacity()
        size = gradientOpacityTransferFunction.GetSize()
        json_data["GradientOpacity"] = []
        for i in range(size):
            sub_json = {}
            val = [0, 0, 0, 0]
            gradientOpacityTransferFunction.GetNodeValue(i, val)
            sub_json[i] = val
            json_data["GradientOpacity"].append(sub_json)

        scalarOpacityTransferFunction = displayNode.GetVolumePropertyNode().GetVolumeProperty().GetScalarOpacity()
        size = scalarOpacityTransferFunction.GetSize()
        json_data["ScalarOpacity"] = []
        for i in range(size):
            sub_json = {}
            val = [0, 0, 0, 0]
            scalarOpacityTransferFunction.GetNodeValue(i, val)
            sub_json[i] = val
            json_data["ScalarOpacity"].append(sub_json)

        RGBTransferFunction = displayNode.GetVolumePropertyNode().GetVolumeProperty().GetRGBTransferFunction()
        size = RGBTransferFunction.GetSize()
        json_data["RGBTransferFunction"] = []
        for i in range(size):
            sub_json = {}
            val = [0, 0, 0, 0, 0, 0]
            RGBTransferFunction.GetNodeValue(i, val)
            sub_json[i] = val
            json_data["RGBTransferFunction"].append(sub_json)

        file_name = util.get_resource("volumerendering.json").replace('\\', '/')
        data = {}
        data["paras"] = []
        try:
            if os.path.exists(file_name):
                with open(file_name, "r") as json_file:
                    data = json.load(json_file)
        except Exception as e:
            pass
        data["paras"].append(json_data)
        with open(file_name, "w") as json_file:
            json.dump(data, json_file, indent=4)
        util.showWarningText("记录成功")

    def add_tool_friends(self, parent):
        layout, btn = self.create_labeled_clicked_button(parent, "btn_friends.png", "致谢", "致谢")
        tool = JMeasureTool(layout, btn, "tool_friends")
        self.tool_list.append(tool)
        btn.connect('clicked()', self.on_tool_friends)
        return tool

    def on_tool_friends(self):
        filename = util.get_resource(('namelist.txt'))
        f = open(filename, 'r')
        content = f.read()
        print(content)
        f.close()
        util.send_event_str(util.Thanks_Friends, content)

    def add_tool_thanks(self, parent):
        layout, btn = self.create_labeled_clicked_button(parent, "thanksicon.png", "致谢", "致谢")
        tool = JMeasureTool(layout, btn, "tool_thanks")
        self.tool_list.append(tool)
        btn.connect('clicked()', self.on_tool_thanks)
        return tool

    def on_tool_thanks(self):
        image_path = util.get_resource(('thanks.jpg')).replace('\\', '/')
        dlg = qt.QDialog()
        dlg.setWindowTitle("致谢")
        dlg.setWindowIcon(qt.QIcon(util.get_resource(('doctor_support.png')).replace('\\', '/')))
        dlg.setWindowFlags(dlg.windowFlags() & ~0x00010000)
        dlg.setModal(True)
        l = qt.QHBoxLayout(dlg)
        image = qt.QLabel()
        image.setPixmap(qt.QPixmap(image_path))

        scroll_area = qt.QScrollArea()
        scroll_area.setWidget(image)
        scroll_area.setHorizontalScrollBarPolicy(1)
        l.addWidget(scroll_area)

        dlg.exec()

    '''
    放大工具
  '''

    def add_zoomout_tool(self, parent):
        layout, btn = self.create_labeled_clicked_button(parent, "tool_zoomout.png", "放大视图", "放大")
        tool = JMeasureTool(layout, btn, "tool_zoomout")
        self.tool_list.append(tool)
        btn.connect('clicked()', self.on_zoomout)
        return tool

    def on_zoomout(self):
        layoutManager = slicer.app.layoutManager()
        for sliceViewName in layoutManager.sliceViewNames():
            view = layoutManager.sliceWidget(sliceViewName).sliceView()
            sliceNode = view.mrmlSliceNode()
            self.zoom(0.9, [sliceNode])

    '''
    缩小工具
  '''

    def add_zoomin_tool(self, parent):
        layout, btn = self.create_labeled_clicked_button(parent, "tool_zoomin.png", "缩小视图", "缩小")
        tool = JMeasureTool(layout, btn, "tool_zoomin")
        self.tool_list.append(tool)
        btn.connect('clicked()', self.on_zoomin)
        return tool

    def on_zoomin(self):
        layoutManager = slicer.app.layoutManager()
        for sliceViewName in layoutManager.sliceViewNames():
            view = layoutManager.sliceWidget(sliceViewName).sliceView()
            sliceNode = view.mrmlSliceNode()
            self.zoom(1.1, [sliceNode])

    def zoom(self, factor, sliceNodes=None):
        """Zoom slice nodes by factor.
    factor: "Fit" or +/- amount to zoom
    sliceNodes: list of slice nodes to change, None means all.
    """
        layoutManager = slicer.app.layoutManager()
        for sliceNode in sliceNodes:
            if factor == "Fit":
                sliceWidget = layoutManager.sliceWidget(sliceNode.GetLayoutName())
                if sliceWidget:
                    sliceWidget.sliceLogic().FitSliceToAll()
            else:
                newFOVx = sliceNode.GetFieldOfView()[0] * factor
                newFOVy = sliceNode.GetFieldOfView()[1] * factor
                newFOVz = sliceNode.GetFieldOfView()[2]
                sliceNode.SetFieldOfView(newFOVx, newFOVy, newFOVz)
                sliceNode.UpdateMatrices()

    '''
    隐藏测量项的工具
  '''

    def add_hide_measure_tool(self, parent):
        layout, btn = self.create_labeled_checkable_button(parent, "tool_visible_on.png", "tool_visible_on.png",
                                                           "隐藏所有的测量项", "隐藏")
        tool = JMeasureTool(layout, btn, "tool_hide_measure")
        self.tool_list.append(tool)
        btn.connect('toggled(bool)', self.on_tool_hide_measure)
        return tool

    def on_tool_hide_measure(self, is_show):
        display_nodes = util.getNodesByClass("vtkMRMLMarkupsDisplayNode")
        for dn in display_nodes:
            dn.SetVisibility(not is_show)

    def set_styles(self, btnlist):
        for btn in btnlist:
            if isinstance(btn, qt.QPushButton):
                btnScissors_stylesheet = ""
                btnScissors_stylesheet = btnScissors_stylesheet + "QPushButton{background-color: #333333;}"
                btnScissors_stylesheet = btnScissors_stylesheet + "QPushButton:hover{background-color: rgb(70, 70, 70);}"
                btnScissors_stylesheet = btnScissors_stylesheet + "QPushButton:checked{background-color: rgb(35, 170, 242);}"
                btn.setStyleSheet(btnScissors_stylesheet)
            else:
                btnScissors_stylesheet = ""
                btnScissors_stylesheet = btnScissors_stylesheet + "QToolButton{background-color: #333333;}"
                btnScissors_stylesheet = btnScissors_stylesheet + "QToolButton:hover{background-color: rgb(70, 70, 70);}"
                btnScissors_stylesheet = btnScissors_stylesheet + "QToolButton:checked{background-color: rgb(35, 170, 242);}"
                btn.setStyleSheet(btnScissors_stylesheet)

    def get_big_icon_measure_panel(self, style=0):
        uiWidget = slicer.util.loadUI(self.resourcePath('UI/BigIconPanelTemplate.ui'))
        ui = slicer.util.childWidgetVariables(uiWidget)
        jm = util.getModuleWidget("JMeasure")

        btnlist = [ui.btn00, ui.btn01, ui.btn02, ui.btn03, ui.btn04, ui.btn10, ui.btn11, ui.btn12, ui.btn13, ui.btn14]
        self.set_styles(btnlist)

        pic = "tool_line.png"
        btn = btnlist[0]
        btn.setCheckable(True)
        icon_path = util.get_resource(pic)
        util.add_pixel_middle(icon_path, btn, jm.resourcelist[pic], size=32)
        btn.connect('toggled(bool)', jm.on_tool_line)
        util.registe_view_tool(btn, "tool_line")

        pic = "tool_angle.png"
        btn = btnlist[1]
        btn.setCheckable(True)
        icon_path = util.get_resource(pic)
        util.add_pixel_middle(icon_path, btn, jm.resourcelist[pic], size=32)
        btn.connect('toggled(bool)', jm.on_tool_angle)
        util.registe_view_tool(btn, "tool_angle")

        pic = "tool_area.png"
        btn = btnlist[2]
        btn.setCheckable(True)
        icon_path = util.get_resource(pic)
        util.add_pixel_middle(icon_path, btn, jm.resourcelist[pic], size=32)
        btn.connect('toggled(bool)', self.on_tool_area)
        util.registe_view_tool(btn, "tool_area")

        pic = "tool_curve.png"
        btn = btnlist[3]
        btn.setCheckable(True)
        icon_path = util.get_resource(pic)
        util.add_pixel_middle(icon_path, btn, jm.resourcelist[pic], size=32)
        btn.connect('toggled(bool)', jm.on_tool_area_open)
        util.registe_view_tool(btn, "tool_curve")

        pic = "tool_rectangle.png"
        btn = btnlist[4]
        btn.setCheckable(True)
        icon_path = util.get_resource(pic)
        util.add_pixel_middle(icon_path, btn, jm.resourcelist[pic], size=32)
        btn.connect('toggled(bool)', jm.on_measurebox_tool_plane)
        util.registe_view_tool(btn, "measurebox")

        # pic = "tool_roi.png"
        # btn = btnlist[5]
        # btn.setCheckable(True)
        # icon_path = util.get_resource(pic)
        # util.add_pixel_middle(icon_path,btn,jm.resourcelist[pic],size=32)
        # btn.connect('toggled(bool)', jm.on_measurebox_tool_roi)
        # util.registe_view_tool(btn,"tool_roi")

        for i in range(5, len(btnlist)):
            btnlist[i].setVisible(False)
        return uiWidget, ui

    def do_common_markups_setting(self, node):
        node.SetAttribute("current_main_module_name", util.current_main_module_name)
        markupsDisplayNode = util.GetDisplayNode(node)
        views = [
            slicer.app.layoutManager().threeDWidget(0).threeDView(),
            slicer.app.layoutManager().sliceWidget("Red").sliceView(),
            slicer.app.layoutManager().sliceWidget("Yellow").sliceView(),
            slicer.app.layoutManager().sliceWidget("Green").sliceView()
        ]
        slicer.app.applicationLogic().GetInteractionNode().SetPlaceModePersistence(0)
        for view in views:
            markupsDisplayableManager = view.displayableManagerByClassName('vtkMRMLMarkupsDisplayableManager')
            # Assign keyboard shortcut to trigger custom actions
            widget = markupsDisplayableManager.GetWidget(markupsDisplayNode)
            # Remove old event translation
            widget.SetEventTranslation(widget.WidgetStateOnWidget,
                                       slicer.vtkMRMLInteractionEventData.LeftButtonClickEvent, vtk.vtkEvent.NoModifier,
                                       vtk.vtkWidgetEvent.NoEvent)

    def get_big_icon_basic_panel(self, style=0):
        uiWidget = slicer.util.loadUI(self.resourcePath('UI/BigIconPanelTemplate.ui'))
        ui = slicer.util.childWidgetVariables(uiWidget)
        jm = util.getModuleWidget("JMeasure")

        btnlist = [ui.btn00, ui.btn01, ui.btn02, ui.btn03, ui.btn04, ui.btn10, ui.btn11, ui.btn12, ui.btn13, ui.btn14]
        self.set_styles(btnlist)

        pic = "tool_reset.png"
        btn = btnlist[0]
        icon_path = util.get_resource(pic)
        util.add_pixel_middle(icon_path, btn, jm.resourcelist[pic], size=32)
        btn.connect('clicked()', lambda: jm.on_reset())

        pic = "tool_zoomout.png"
        btn = btnlist[1]
        icon_path = util.get_resource(pic)
        util.add_pixel_middle(icon_path, btn, jm.resourcelist[pic], size=32)
        btn.connect('clicked()', lambda: jm.on_zoomout())

        pic = "tool_zoomin.png"
        btn = btnlist[2]
        icon_path = util.get_resource(pic)
        util.add_pixel_middle(icon_path, btn, jm.resourcelist[pic], size=32)
        btn.connect('clicked()', lambda: jm.on_zoomin())

        pic = "tool_grayscale.png"
        btn = btnlist[3]
        icon_path = util.get_resource(pic)
        btn.setCheckable(True)
        util.add_pixel_middle(icon_path, btn, jm.resourcelist[pic], size=32)
        btn.connect('toggled(bool)', jm.on_windowlevel_auto)
        util.registe_view_tool(btn, "windowlevel_auto")

        pic = "tool_whirling.png"
        btn = btnlist[4]
        icon_path = util.get_resource(pic)
        btn.setCheckable(True)
        util.add_pixel_middle(icon_path, btn, jm.resourcelist[pic], size=32)
        btn.connect('toggled(bool)', jm.on_whirling)
        util.registe_view_tool(btn, "whirling")

        pic = "tool_screen_shot.png"
        btn = btnlist[5]
        icon_path = util.get_resource(pic)
        util.add_pixel_middle(icon_path, btn, jm.resourcelist[pic], size=32)
        btn.connect('clicked()', jm.on_tool_screenshot)

        for i in range(6, len(btnlist)):
            btnlist[i].setVisible(False)
        return uiWidget, ui

    def on_tool_screenshot(self):
        util.mainWindow().GetCaptureToolBar().screenshotButtonClicked()
        return

    def get_big_icon_panel(self, style=0):
        uiWidget = slicer.util.loadUI(self.resourcePath('UI/BigIconPanel.ui'))
        ui = slicer.util.childWidgetVariables(uiWidget)

        jm = util.getModuleWidget("JMeasure")

        pic = "tool_reset.png"
        btn = ui.btn_refresh
        icon_path = util.get_resource(pic)
        util.add_pixel_middle(icon_path, btn, jm.resourcelist[pic], size=32)
        btn.connect('clicked()', lambda: jm.on_reset())

        pic = "tool_zoomout.png"
        btn = ui.btn_zoomout
        icon_path = util.get_resource(pic)
        util.add_pixel_middle(icon_path, btn, jm.resourcelist[pic], size=32)
        btn.connect('clicked()', lambda: jm.on_zoomout())

        pic = "tool_zoomin.png"
        btn = ui.btn_zoomin
        icon_path = util.get_resource(pic)
        util.add_pixel_middle(icon_path, btn, jm.resourcelist[pic], size=32)
        btn.connect('clicked()', lambda: jm.on_zoomin())

        if style == 1:
            pic = "tool_volumerendering_recorder.png"
            btn = ui.btn_volume_save
            icon_path = util.get_resource(pic)
            util.add_pixel_middle(icon_path, btn, jm.resourcelist[pic], size=32)
            btn.connect('clicked()', lambda: jm.on_tool_save_volume_paras())

            import json
            btn = ui.btn_volume_load
            file_name = util.get_resource("volumerendering.json")
            data = {}
            data["paras"] = []
            if os.path.exists(file_name):
                with open(file_name, "r") as json_file:
                    data = json.load(json_file)
            menu = qt.QMenu(btn)
            index = 0
            for data in data["paras"]:
                sub_json_data = data
                menu.addAction(f"模式{index}",
                               lambda a, v1=index, v2=sub_json_data: jm.on_choose_volume_paras(a, v1, v2))
                index += 1
            pic = "tool_volumerendering_list.png"
            icon_path = util.get_resource(pic)
            util.add_pixel_middle(icon_path, btn, jm.resourcelist[pic], size=32)
            btn.connect('clicked()', lambda: jm.on_tool_save_volume_paras())
            btn.setLayoutDirection(qt.Qt.LeftToRight)
            btn.setToolButtonStyle(qt.Qt.ToolButtonTextBesideIcon)
            btn.setPopupMode(1)
            btn.setMenu(menu)
        elif style == 2:
            ui.btn_volume_save.setVisible(False)
            ui.btn_volume_load.setVisible(False)
            ui.btn_mpr.setVisible(False)
        else:
            ui.btn_volume_save.setVisible(False)
            ui.btn_volume_load.setVisible(False)

        pic = "tool_grayscale.png"
        btn = ui.btn_gray
        icon_path = util.get_resource(pic)
        util.add_pixel_middle(icon_path, btn, jm.resourcelist[pic], size=32)
        btn.connect('toggled(bool)', jm.on_windowlevel_auto)
        util.registe_view_tool(btn, "windowlevel_auto")

        pic = "tool_whirling.png"
        btn = ui.btn_mpr
        icon_path = util.get_resource(pic)
        util.add_pixel_middle(icon_path, btn, jm.resourcelist[pic], size=32)
        btn.connect('toggled(bool)', jm.on_whirling)
        util.registe_view_tool(btn, "whirling")

        pic = "tool_settings.png"
        btn = ui.btn_setting
        icon_path = util.get_resource(pic)
        util.add_pixel_middle(icon_path, btn, jm.resourcelist[pic], size=32)
        btn.connect('clicked()', jm.enter_setting)

        pic = "goto_markups_manager_cmf.png"
        btn = ui.btn_markups_list
        icon_path = util.get_resource(pic)
        util.add_pixel_middle(icon_path, btn, "切换到测量项列表的页面", size=32)
        btn.connect("clicked()", self.on_MarkupList)

        tool = jm.add_tool_measurebox_outside(ui.widget_4, ui.btn_measurebox)
        ui.btn_measurebox.setLayoutDirection(qt.Qt.LeftToRight)
        ui.btn_measurebox.setToolButtonStyle(qt.Qt.ToolButtonTextBesideIcon)
        ui.btn_measurebox.setPopupMode(1)

        return uiWidget, ui

    def on_MarkupList(self):
        util.send_event_str(util.SetPage, 915)
        util.getModuleWidget("JManagerMarkups").inner_manager.fresh_list()

    def create_labeled_clicked_button(self, parent, picture_name, tooltip, label, icon_width=20, rlist=None):
        import qt
        if rlist:
            rlist[picture_name] = tooltip
        self.resourcelist[picture_name] = tooltip
        btn = qt.QPushButton(parent)
        # picture_name = self.resourcePath(('Icons/'+picture_name)).replace('\\','/')
        picture_name = util.get_resource(picture_name)
        labelText = qt.QLabel()
        pixelmap = qt.QPixmap(picture_name)
        pixelmap_scaled = pixelmap.scaled(icon_width, icon_width, 0, 1)
        labelPic = qt.QLabel()
        labelPic.setPixmap(pixelmap_scaled)
        labelPic.setObjectName("labelPic")
        labelPic.setAlignment(0x0004 | 0x0080)
        labelPic.setStyleSheet("background-color: transparent;")
        labelText.setText(label)
        labelText.setObjectName("labelText")
        labelText.setStyleSheet(
            "font: 12px 'Source Han Sans CN-Regular, Source Han Sans CN';background-color: transparent;")
        if self.orientation == self.horizontal:
            layout = qt.QHBoxLayout()
            btn.setFixedSize(self.button_width * 3, self.button_height)
        else:
            layout = qt.QVBoxLayout()
            btn.setFixedSize(self.button_width + 15, self.button_height * 2.5)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setAlignment(0x0004 | 0x0080)
        layout.addStretch()
        layout.addSpacing(2)
        layout.addWidget(labelPic)
        layout.addSpacing(6)
        layout.addWidget(labelText)
        layout.addStretch()
        btn.setLayout(layout)
        btn_stylesheet = btn.styleSheet
        btn_stylesheet = btn_stylesheet + "QPushButton:hover{background-color: #444444}"
        btn_stylesheet = btn_stylesheet + "QPushButton:pressed{background-color: #004444}"
        btn.setStyleSheet(btn_stylesheet)

        stylesheet = btn.styleSheet
        stylesheet = stylesheet + "QPushButton{border: 0px}"
        btn.setStyleSheet(stylesheet)
        return btn, btn

    def create_labeled_checkable_button(self, parent, checked_false_name, checked_true_name, tooltip, label,
                                        icon_width=20):
        import qt
        self.resourcelist[checked_false_name] = tooltip
        btn = qt.QPushButton(parent)

        # btn_checked_true = self.resourcePath(('Icons/'+checked_true_name)).replace('\\','/')
        # btn_checked_false = self.resourcePath(('Icons/'+checked_false_name)).replace('\\','/')
        btn_checked_false = util.get_resource(checked_false_name)

        pixelmap = qt.QPixmap(btn_checked_false)
        pixelmap_scaled = pixelmap.scaled(icon_width, icon_width, 0, 1)
        labelPic = qt.QLabel()
        labelPic.setPixmap(pixelmap_scaled)
        labelPic.setObjectName("labelPic")
        labelPic.setAlignment(0x0004 | 0x0080)
        labelPic.setStyleSheet("background-color: transparent;")
        labelText = qt.QLabel()
        labelText.setText(label)
        labelText.setObjectName("labelText")
        labelText.setStyleSheet(
            "font: 12px 'Source Han Sans CN-Regular, Source Han Sans CN';background-color: transparent;")

        if self.orientation == self.horizontal:
            layout = qt.QHBoxLayout()
            btn.setFixedSize(self.button_width * 3, self.button_height)
        else:
            layout = qt.QVBoxLayout()
            btn.setFixedSize(self.button_width + 15, self.button_height * 2.5)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setAlignment(0x0004 | 0x0080)
        layout.addStretch()
        layout.addSpacing(2)
        layout.addWidget(labelPic)
        layout.addSpacing(6)
        layout.addWidget(labelText)
        layout.addStretch()
        btn.setLayout(layout)
        btn.setCheckable(True)
        btn_stylesheet = btn.styleSheet
        btn_stylesheet = btn_stylesheet + "QPushButton:hover{background-color: #444444}"
        btn.setStyleSheet(btn_stylesheet)
        stylesheet = btn.styleSheet
        stylesheet = stylesheet + "QPushButton{border: 0px}"
        stylesheet = stylesheet + "QPushButton:checked{background-color: #004444};"
        btn.setStyleSheet(stylesheet)
        return btn, btn

    def create_toolbutton(self, parent, picture_name, tooltip, label, icon_width=20):
        import qt
        self.resourcelist[picture_name] = tooltip
        if self.orientation == self.horizontal:
            labelText = qt.QLabel()
            labelText.setText(label)
            labelText.setObjectName("labelText")
            labelText.setStyleSheet(
                "font: 12px 'Source Han Sans CN-Regular, Source Han Sans CN';background-color: transparent;")
            btn = qt.QToolButton()
            btn.setLayoutDirection(qt.Qt.LeftToRight)
            btn.setToolButtonStyle(qt.Qt.ToolButtonTextBesideIcon)
            btn.setPopupMode(1)
            path = util.get_resource(picture_name)
            pixmap = qt.QPixmap(path)
            pixelmap_scaled = pixmap.scaled(icon_width, icon_width, 0, 1)
            buttonIcon = qt.QIcon(pixelmap_scaled)
            btn.setIcon(buttonIcon)
            btn.setIconSize(qt.QSize(icon_width, icon_width))
            btn.setText("")

            layout = qt.QHBoxLayout()
            layout_btn = qt.QPushButton(parent)
            layout_btn.setFixedSize(self.button_width * 3 + 15, self.button_height)
            btn.setFixedSize(self.button_width + 15, self.button_height)

            layout.setContentsMargins(0, 0, 0, 0)
            layout.setAlignment(0x0004 | 0x0080)
            layout.addWidget(btn)
            layout.addSpacing(6)
            layout.addWidget(labelText)
            layout.addStretch()
            layout_btn.setLayout(layout)
            btn_stylesheet = layout_btn.styleSheet
            btn_stylesheet = btn_stylesheet + "QPushButton:hover{background-color: #444444}"
            btn_stylesheet = btn_stylesheet + "QPushButton{border: 0px}"
            layout_btn.setStyleSheet(btn_stylesheet)
            btn_stylesheet2 = btn.styleSheet
            btn_stylesheet2 = btn_stylesheet2 + "QToolButton:hover{background-color: #444444}"
            btn_stylesheet2 = btn_stylesheet2 + "QToolButton{border: 0px}"
            btn_stylesheet2 = btn_stylesheet2 + "QToolButton::menu-button{background-color: transparent}"
            btn_stylesheet2 = btn_stylesheet2 + "QToolButton::menu-button{border: 0px}"
            btn_stylesheet2 = btn_stylesheet2 + "QToolButton:checked{background-color: #004444};"
            btn.setStyleSheet(btn_stylesheet2)
            return layout_btn, btn
        else:
            btn = qt.QToolButton(parent)
            btn.setFixedSize(self.button_width + 15, self.button_height * 2.5)

            btn.setToolButtonStyle(3)
            btn.setPopupMode(1)
            path = util.get_resource(picture_name)
            pixmap = qt.QPixmap(path)
            pixelmap_scaled = pixmap.scaled(icon_width, icon_width, 0, 1)
            buttonIcon = qt.QIcon(pixelmap_scaled)
            btn.setIcon(buttonIcon)
            btn.setIconSize(qt.QSize(icon_width, icon_width))
            btn.setText(label)

            font = qt.QFont()
            font.setPointSize(9)
            btn.setFont(font)

            btn_stylesheet = btn.styleSheet
            btn_stylesheet = btn_stylesheet + "QToolButton:hover{background-color: #444444 ;}"
            btn_stylesheet = btn_stylesheet + "QToolButton:checked{background-color: #004444};"
            btn.setStyleSheet(btn_stylesheet)
            return btn, btn


class JMeasureLogic(ScriptedLoadableModuleLogic):
    def __init__(self):
        """
    Called when the logic class is instantiated. Can be used for initializing member variables.
    """
        ScriptedLoadableModuleLogic.__init__(self)

    def setWidget(self, widget):
        self.m_Widget = widget

    def hide_reload(self, show):
        pass
