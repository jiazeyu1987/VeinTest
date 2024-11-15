import slicer.util as util
import slicer, qt
from RDNTool.UltraSoundColorBar import UltraSoundColorBar
from RDNTool.RulerWidget import RulerWidget
from RDNTool.FocusWidget import FocusWidget
from RDNTool.InfoLabel import InfoLabel
from RDNTool.RectangleWidget import RectangleWidget
import os
import numpy as np


class UltraSoundSettingPanel:
    uiWidget = None
    ui = None
    parent = None
    geometry = None

    color_bar = None
    ruler = None

    mode = "MODE_BMODE"
    MODE_BMODE = "MODE_BMODE"
    MODE_PDI = "MODE_PDI"

    is_use_cursor = True
    widget_cursor = None
    CrosshairNodeObserverTag = None
    roi_point_node = None

    def __init__(self, main, flag=True):
        # 获取当前文件的绝对路径
        current_file_path = os.path.abspath(__file__)
        # 获取当前文件所在目录的上一层目录
        parent_directory = os.path.dirname(os.path.dirname(current_file_path))
        # 其他插件也会用到这个弹窗，所以不能通过parent加载ui文件
        self.uiWidget = util.loadUI(parent_directory + '/Resources/UI/UltrasoundSettingPanel.ui')
        # self.uiWidget = util.loadUI(main.resourcePath('UI/UltrasoundSettingPanel.ui'))
        self.ui = util.childWidgetVariables(self.uiWidget)
        self.parent = qt.QWidget()

        self.color_bar = UltraSoundColorBar(main)
        self.ruler = RulerWidget()
        self.focus_widget = FocusWidget()
        self.label_info = InfoLabel(main)
        util.addWidget2(self.parent, self.uiWidget)
        self.parent.raise_()
        self.parent.raise_()
        self.init_ui()
        if flag:
            util.singleShot(100, self.initLater)

    def init_ui(self):
        self.rectangle_widget = RectangleWidget()
        self.ui.btn_BMod.connect('toggled(bool)', self.on_btn_BMod)
        self.ui.btn_TMod.connect('toggled(bool)', self.on_btn_TMod)
        self.ui.btn_PDI.connect('toggled(bool)', self.on_btn_PDI)
        self.ui.btn_Ruler.connect('toggled(bool)', self.on_btn_Ruler)
        self.ui.btn_roi.connect('toggled(bool)', self.start_drawing)
        self.ui.pushButton_2.connect('clicked()', self.get_info)
        self.ui.btn_freeze.connect('toggled(bool)', self.on_freeze)
        self.ui.btn_set_probe.connect('clicked()', self.set_probe)
        self.ui.pushButton_4.connect('clicked()', self.on_set_roi)
        self.ui.ctkSliderWidget1.singleStep = 1
        self.ui.ctkSliderWidget1.minimum = 1
        self.ui.ctkSliderWidget1.maximum = 31
        self.ui.ctkSliderWidget1.value = 3
        util.global_data_map['ultra_depth'] = 3

        self.ui.ctkSliderWidget1.connect('valueChanged(double)', self.on_ctkSliderWidgetChanged)

        self.ui.ctkSliderWidget1_3.singleStep = 1
        self.ui.ctkSliderWidget1_3.minimum = -100
        self.ui.ctkSliderWidget1_3.maximum = 100
        self.ui.ctkSliderWidget1_3.value = 0
        self.ui.ctkSliderWidget1_3.connect('valueChanged(double)', self.on_liveGainChanged)

        self.ui.ctkSliderWidget1_4.singleStep = 1
        self.ui.ctkSliderWidget1_4.minimum = 1
        self.ui.ctkSliderWidget1_4.maximum = 31
        self.ui.ctkSliderWidget1_4.value = 0
        self.ui.ctkSliderWidget1_4.connect('valueChanged(double)', self.on_BFocusChanged)

        self.ui.ctkSliderWidget1_5.singleStep = 1
        self.ui.ctkSliderWidget1_5.minimum = 1
        self.ui.ctkSliderWidget1_5.maximum = 31
        self.ui.ctkSliderWidget1_5.value = 0
        self.ui.ctkSliderWidget1_5.connect('valueChanged(double)', self.on_pdiFocusChanged)

        self.ui.btn_Ruler.setChecked(True)
        self.ui.btn_BMod.setChecked(True)

        tgc_sliders = [self.ui.horizontalSlider, self.ui.horizontalSlider_2, self.ui.horizontalSlider_3,
                       self.ui.horizontalSlider_4, self.ui.horizontalSlider_5, self.ui.horizontalSlider_6,
                       self.ui.horizontalSlider_7, self.ui.horizontalSlider_8]
        for slider in tgc_sliders:
            slider.minimum = -20
            slider.maximum = 20
            slider.value = 0
            slider.singleStep = 1
        self.ui.horizontalSlider.connect('valueChanged(int)', self.on_tgc1)
        self.ui.horizontalSlider_2.connect('valueChanged(int)', self.on_tgc2)
        self.ui.horizontalSlider_3.connect('valueChanged(int)', self.on_tgc3)
        self.ui.horizontalSlider_4.connect('valueChanged(int)', self.on_tgc4)
        self.ui.horizontalSlider_5.connect('valueChanged(int)', self.on_tgc5)
        self.ui.horizontalSlider_6.connect('valueChanged(int)', self.on_tgc6)
        self.ui.horizontalSlider_7.connect('valueChanged(int)', self.on_tgc7)
        self.ui.horizontalSlider_8.connect('valueChanged(int)', self.on_tgc8)
        self.ui.pushButton.connect('clicked()', self.onresettgc)
        self.ui.btn_BMod.setChecked(True)

        # self.menu = qt.QMenu(self.ui.widget)
        #
        # self.create_menu_button("直线", self.menu, lambda: self.on_measurebox_tool_line("直线"))
        # self.create_menu_button("面积", self.menu, lambda: self.on_measurebox_tool_area("面积"))

        # self.ui.btn_measure.setMenu(self.menu)
        self.ui.btn_measure.connect('clicked()', self.on_measurebox_tool_line)

        self.label_info.show()
        self.ui.edit_power.setText("0")
        self.ui.btn_set_power.connect('clicked()', self.on_set_power)

    def on_reset_ui(self):
        self.onresettgc()
        self.rectangle_widget.clear_rectangle()
        self.ui.btn_BMod.setChecked(True)
        tgc_sliders = [self.ui.horizontalSlider, self.ui.horizontalSlider_2, self.ui.horizontalSlider_3,
                       self.ui.horizontalSlider_4, self.ui.horizontalSlider_5, self.ui.horizontalSlider_6,
                       self.ui.horizontalSlider_7, self.ui.horizontalSlider_8]
        for slider in tgc_sliders:
            slider.value = 0

        self.ui.ctkSliderWidget1.value = 3
        util.global_data_map['ultra_depth'] = 3

        self.ui.ctkSliderWidget1_3.value = 0
        self.ui.ctkSliderWidget1_4.value = 0
        self.ui.ctkSliderWidget1_5.value = 0

        self.ui.btn_Ruler.setChecked(True)
        self.ui.btn_BMod.setChecked(True)
        self.ui.label_dis.text = ""
        self.ui.comboBox_2.setCurrentIndex(0)

        self.ui.tabWidget.setCurrentIndex(0)
        self.ui.edit_power.setText("1")

    def create_menu_button(self, text, menu, slot):
        button = qt.QPushButton(text)
        button_action = qt.QWidgetAction(menu)
        button_action.setDefaultWidget(button)
        menu.addAction(button_action)
        button.clicked.connect(slot)

    def on_measurebox_tool_line(self):
        self.delete_all_markups()

        # self.ui.btn_measure.setText(text)

        # self.menu.hide()

        line_node = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLMarkupsLineNode")

        interaction_node = slicer.app.applicationLogic().GetInteractionNode()
        interaction_node.SetCurrentInteractionMode(slicer.vtkMRMLInteractionNode.Place)
        selection_node = slicer.app.applicationLogic().GetSelectionNode()
        selection_node.SetActivePlaceNodeID(line_node.GetID())
        selection_node.SetReferenceActivePlaceNodeClassName("vtkMRMLMarkupsLineNode")

        displayNode = line_node.GetDisplayNode()
        displayNode.SetTextScale(0)
        displayNode.SetColor(1, 0, 0)

        def update_line_length(caller, event):
            if line_node.GetNumberOfControlPoints() < 2:
                return

            spacing = util.global_data_map['ultra_depth'] / 480

            # point1 = np.array(line_node.GetNthControlPointPosition(0))
            # point2 = np.array(line_node.GetNthControlPointPosition(1))

            # physicalPoint1 = point1 * spacing
            # physicalPoint2 = point2 * spacing

            # lineLength = np.linalg.norm(physicalPoint1 - physicalPoint2) * util.ultra_height / 480

            length = line_node.GetMeasurement("length").GetValue() * spacing * util.ultra_height / 480
            self.ui.label_dis.setText(f"{length:.2f}")
            util.getModuleWidget("VeinTreat").set_depth(f"皮下深度测量:{length:.2f}")
            # print(f"point --- {point1,point2}")
            # print(f"distance: {length:.2f}---{lineLength:.2f}")

        line_node.AddObserver(slicer.vtkMRMLMarkupsNode.PointModifiedEvent, update_line_length)

    def refresh_red_widget(self):
        layoutManager = slicer.app.layoutManager()
        red_widget = layoutManager.sliceWidget('Red')
        red_logic = red_widget.sliceLogic()
        red_logic.FitSliceToAll()
        slicer.app.processEvents()

    def on_measurebox_tool_area(self, text):
        self.delete_all_markups()

        self.ui.btn_measure.setText(text)

        self.menu.hide()

        curve_node = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLMarkupsClosedCurveNode")

        interaction_node = slicer.app.applicationLogic().GetInteractionNode()
        interaction_node.SetCurrentInteractionMode(slicer.vtkMRMLInteractionNode.Place)
        selection_node = slicer.app.applicationLogic().GetSelectionNode()
        selection_node.SetActivePlaceNodeID(curve_node.GetID())
        selection_node.SetReferenceActivePlaceNodeClassName("vtkMRMLMarkupsClosedCurveNode")

    def delete_all_markups(self):
        markups_nodes = slicer.util.getNodesByClass('vtkMRMLMarkupsNode')
        for node in markups_nodes:
            slicer.mrmlScene.RemoveNode(node)

    def on_BFocusChanged(self, value):
        if value < self.ui.ctkSliderWidget1.value:
            util.getModuleWidget("RequestStatus").send_cmd(f"UltraImage, setTissueFocus, {int(value)}")

    def on_pdiFocusChanged(self, value):
        if value < self.ui.ctkSliderWidget1.value:
            util.getModuleWidget("RequestStatus").send_cmd(f"UltraImage, setColorFocus, {int(value)}")

    def onresettgc(self):
        util.getModuleWidget("RequestStatus").send_cmd(f"UltraImage, resetTGC")
        self.ui.horizontalSlider.setValue(0)
        self.ui.horizontalSlider_2.setValue(0)
        self.ui.horizontalSlider_3.setValue(0)
        self.ui.horizontalSlider_4.setValue(0)
        self.ui.horizontalSlider_5.setValue(0)
        self.ui.horizontalSlider_6.setValue(0)
        self.ui.horizontalSlider_7.setValue(0)
        self.ui.horizontalSlider_8.setValue(0)

    def on_tgc1(self, val):
        util.getModuleWidget("RequestStatus").send_cmd(f"UltraImage, setTGC1, {val}")

    def on_tgc2(self, val):
        util.getModuleWidget("RequestStatus").send_cmd(f"UltraImage, setTGC2, {val}")

    def on_tgc3(self, val):
        util.getModuleWidget("RequestStatus").send_cmd(f"UltraImage, setTGC3, {val}")

    def on_tgc4(self, val):
        util.getModuleWidget("RequestStatus").send_cmd(f"UltraImage, setTGC4, {val}")

    def on_tgc5(self, val):
        util.getModuleWidget("RequestStatus").send_cmd(f"UltraImage, setTGC5, {val}")

    def on_tgc6(self, val):
        util.getModuleWidget("RequestStatus").send_cmd(f"UltraImage, setTGC6, {val}")

    def on_tgc7(self, val):
        util.getModuleWidget("RequestStatus").send_cmd(f"UltraImage, setTGC7, {val}")

    def on_tgc8(self, val):
        util.getModuleWidget("RequestStatus").send_cmd(f"UltraImage, setTGC8, {val}")

    def on_liveGainChanged(self, value):
        util.getModuleWidget("RequestStatus").send_cmd(f"UltraImage, SetLiveGain, {int(value)}")

    def on_ctkSliderWidgetChanged(self, value):
        self.ui.ctkSliderWidget1.blockSignals(True)
        util.getModuleWidget("RequestStatus").send_cmd(f"UltraImage, SetDepth, {int(value)}")
        depth = int(float(util.getModuleWidget("RequestStatus").send_synchronize_cmd("UltraImage, GetDepth")))
        self.ruler.setDepth(depth)
        self.focus_widget.setDepth(depth)
        self.ui.ctkSliderWidget1.value = depth
        util.global_data_map['ultra_depth'] = depth
        self.ui.ctkSliderWidget1.blockSignals(False)

    def on_btn_TMod(self, isShow):
        if not isShow:
            return
        self.ui.btn_PDI.setChecked(False)
        self.ui.btn_BMod.setChecked(False)
        self.mode = self.MODE_BMODE
        util.getModuleWidget("RequestStatus").send_cmd(f"UltraImage, switchToTMode")
        self.switch_to_mode()
        if self.rectangle_widget:
            self.rectangle_widget.clear_rectangle()

    def on_btn_BMod(self, isShow):
        if not isShow:
            return
        self.ui.btn_PDI.setChecked(False)
        self.ui.btn_TMod.setChecked(False)
        self.mode = self.MODE_BMODE
        self.switch_to_mode()
        util.getModuleWidget("RequestStatus").send_cmd(f"UltraImage, switchToBMode")
        if self.rectangle_widget:
            self.rectangle_widget.clear_rectangle()

    def on_btn_PDI(self, isShow):
        if not isShow:
            return
        self.ui.btn_BMod.setChecked(False)
        self.ui.btn_TMod.setChecked(False)
        self.mode = self.MODE_PDI
        util.getModuleWidget("RequestStatus").send_cmd(f"UltraImage, switchToPDIMode")
        util.getModuleWidget("RequestStatus").send_cmd(f"UltraImage, setCROI, 100, 100, 300, 300")
        self.switch_to_mode()

    def set_probe(self):
        if self.ui.comboBox_2.currentText == "R60":
            util.getModuleWidget("RequestStatus").send_cmd(f"UltraImage, SetActivateProbe, R60")
        elif self.ui.comboBox_2.currentText == "L40":
            util.getModuleWidget("RequestStatus").send_cmd(f"UltraImage, SetActivateProbe, L40")
        elif self.ui.comboBox_2.currentText == "P25":
            util.getModuleWidget("RequestStatus").send_cmd(f"UltraImage, SetActivateProbe, P25")
        else:
            pass

    def on_freeze(self, boolval):
        if boolval:
            util.getModuleWidget("RequestStatus").send_cmd(f"UltraImage, setFreeze, 1")
        else:
            util.getModuleWidget("RequestStatus").send_cmd(f"UltraImage, setFreeze, 0")

    def get_info(self):
        info = util.getModuleWidget("RequestStatus").send_synchronize_cmd("UltraImage, GetInfo")
        self.ui.textEdit.setPlainText(info)

    def on_btn_Ruler(self, isShow):
        if isShow:
            self.ruler.show()
            self.focus_widget.show()
        else:
            self.ruler.hide()
            self.focus_widget.hide()

    def initLater(self):
        width = 320
        height = 500
        # posX = util.global_data_map['width'] - util.global_data_map['gap'] - util.global_data_map['offset'] - width
        # posY = util.global_data_map['gap']
        posX = 0
        posY = 0
        self.parent.geometry = qt.QRect(posX, posY, width, height)
        self.parent.setParent(util.getModuleWidget("VeinConfig").ui.widget)

    def show(self):
        self.parent.show()

    def hide(self):
        self.parent.hide()

    def on_define_roi(self, _a, _b):
        self.ui.pushButton_3.setChecked(False)

    def on_set_roi(self):
        util.getModuleWidget("RequestStatus").send_cmd(
            f"UltraImage, setCROI, {int(self.ui.lineEdit.text)}, {int(self.ui.lineEdit_2.text)}, {int(self.ui.lineEdit_4.text)}, {int(self.ui.lineEdit_3.text)}")
        self.rectangle_widget.set_rectangle_position(int(self.ui.lineEdit.text) + util.ultra_width,
                                                     int(self.ui.lineEdit_2.text) + util.ultra_height + util.ultra_y - int(
                                                         self.ui.lineEdit_3.text),
                                                     int(self.ui.lineEdit_4.text),
                                                     int(self.ui.lineEdit_3.text))

    def on_roi(self, val):
        CrosshairNode = slicer.mrmlScene.GetFirstNodeByClass('vtkMRMLCrosshairNode')
        if val:
            self.CrosshairNodeObserverTag = CrosshairNode.AddObserver(
                slicer.vtkMRMLCrosshairNode.CursorPositionModifiedEvent, self.processEvent)
            self.roi_point_node = util.AddNewNodeByClass("vtkMRMLMarkupsFiducialNode")
            self.roi_point_node.SetName("ultrasound_roi_point")
            display_node = util.GetDisplayNode(self.roi_point_node)
            display_node.SetPointLabelsVisibility(False)
            display_node.SetVisibility(False)
            interactionNode = slicer.app.applicationLogic().GetInteractionNode()
            selectionNode = slicer.app.applicationLogic().GetSelectionNode()
            selectionNode.SetReferenceActivePlaceNodeClassName("vtkMRMLMarkupsFiducialNode")
            selectionNode.SetActivePlaceNodeID(self.roi_point_node.GetID())
            interactionNode.SetCurrentInteractionMode(interactionNode.Place)
            self.roi_point_node.AddObserver(slicer.vtkMRMLMarkupsNode.PointPositionDefinedEvent, self.on_define_roi)

        else:
            CrosshairNode.RemoveObserver(self.CrosshairNodeObserverTag)
            util.singleShot(10, lambda: util.RemoveNodeByName("ultrasound_roi_point"))

    def switch_to_mode(self):
        self.color_bar.switch_to_mode(self.mode)

    def processEvent(self, observee, event):
        insideView = False
        xyz = [0.0, 0.0, 0.0]
        ras = [0.0, 0.0, 0.0]
        CrosshairNode = slicer.mrmlScene.GetFirstNodeByClass('vtkMRMLCrosshairNode')
        insideView = CrosshairNode.GetCursorPositionRAS(ras)
        sliceNode = CrosshairNode.GetCursorPositionXYZ(xyz)
        sliceLogic = None
        if sliceNode:
            if self.ui.comboBox_2.currentText == "R60":
                self.show_circle(sliceNode, xyz, 120, 100, 16, 10, 16)
            elif self.ui.comboBox_2.currentText == "L40":
                self.show_rect(sliceNode, xyz, 120, 100, 16)

    def get_cursor_angle(self, xyz):
        red_slice_widget = slicer.app.layoutManager().sliceWidget("Red")
        center_x = red_slice_widget.width / 2
        center_y = red_slice_widget.height + 100
        vector1 = [xyz[0] - center_x, xyz[1] - center_y]
        vector2 = [0, 1]
        dot_product = np.dot(vector1, vector2)
        norm_vector1 = np.linalg.norm(vector1)
        norm_vector2 = np.linalg.norm(vector2)
        cos_theta = dot_product / (norm_vector1 * norm_vector2)
        theta_radians = np.arccos(np.clip(cos_theta, -1.0, 1.0))
        theta_degrees = np.degrees(theta_radians)
        if xyz[0] < center_x:
            theta_degrees = 360 - theta_degrees
        return theta_degrees

    def tickEvent(self, value):
        map_info = {}
        info_list_str = value.split("*V* ")
        txt = ""
        for row in info_list_str:
            if row == "":
                continue
            key_value_pair_list = row.split("*U* ")
            assert (len(key_value_pair_list) == 2)
            key = key_value_pair_list[0]
            value = key_value_pair_list[1]
            map_info[key] = value
        if 'fps_b' in map_info:
            txt = txt + "B FPS:" + map_info['fps_b'] + "      "
        if 'fps_t' in map_info:
            txt = txt + "T FPS:" + map_info['fps_t'] + "      "
        if 'fps_pdi' in map_info:
            txt = txt + "P FPS:" + map_info['fps_pdi']

    def show_circle(self, sliceNode, xyz, rectWidth, rectHeight, rectInter, rectTopInter, rectBottomInter):
        sliceName = sliceNode.GetName()
        red_slice_widget = slicer.app.layoutManager().sliceWidget("Red")
        angle = self.get_cursor_angle(xyz) - 180
        if self.widget_cursor != None:
            red_slice_widget.layout().removeWidget(self.widget_cursor)
            self.widget_cursor.deleteLater()
            self.widget_cursor = None
        if sliceName != "Red":
            return
        self.widget_cursor = qt.QLabel()
        pixmap1 = qt.QPixmap(rectWidth, rectHeight)
        pixmap1.fill(qt.Qt.transparent)

        painter = qt.QPainter(pixmap1)
        painter.setRenderHint(qt.QPainter.Antialiasing)  # 设置反锯齿
        tmp_inter = 20
        bottom_left = qt.QPointF(tmp_inter, rectHeight - 10 - tmp_inter)  # 左下角
        bottom_right = qt.QPointF(rectWidth - tmp_inter, rectHeight - 10 - tmp_inter)  # 右下角
        top_right = qt.QPointF(rectWidth - rectInter - tmp_inter, tmp_inter)  # 右上角
        top_left = qt.QPointF(rectInter + tmp_inter, tmp_inter)  # 左上角
        path = qt.QPainterPath()
        path.moveTo(top_left)
        path.quadTo(rectWidth / 2, top_right.y() + rectTopInter, top_right.x(), top_right.y())

        path.lineTo(bottom_right.x(), bottom_right.y())

        path.quadTo(rectWidth / 2, bottom_right.y() + rectBottomInter, bottom_left.x(), bottom_left.y())

        path.lineTo(top_left.x(), top_left.y())
        painter.strokePath(path, qt.QPen(qt.Qt.white, 2))
        painter.end()
        transform = qt.QTransform()
        transform.rotate(angle)
        pixmap1 = pixmap1.transformed(transform)
        self.widget_cursor.setPixmap(pixmap1)
        self.widget_cursor.setGeometry(0, 0, rectWidth, rectHeight + rectBottomInter)
        self.widget_cursor.setParent(red_slice_widget)

        self.widget_cursor.setAttribute(qt.Qt.WA_TransparentForMouseEvents, True)
        self.widget_cursor.show()
        red_slice_view = red_slice_widget.sliceView()
        height = red_slice_view.height
        flipped_y = height - xyz[1] - rectHeight / 2
        self.widget_cursor.move(xyz[0] - rectWidth / 2, flipped_y)
        pass

    def show_rect(self, sliceNode, xyz, rectWidth, rectHeight, rectInter):
        sliceName = sliceNode.GetName()
        if sliceName != "Red+":
            return
        red_slice_widget = slicer.app.layoutManager().sliceWidget("Red+")
        if self.widget_cursor != None:
            red_slice_widget.layout().removeWidget(self.widget_cursor)
            self.widget_cursor.deleteLater()
            self.widget_cursor = None

        self.widget_cursor = qt.QLabel()
        pixmap1 = qt.QPixmap(rectWidth, rectHeight)
        pixmap1.fill(qt.Qt.transparent)

        painter = qt.QPainter(pixmap1)
        painter.setPen(qt.QColor("red"))
        painter.setRenderHint(qt.QPainter.Antialiasing)  # 设置反锯齿

        tmp_inter = 20
        top_left_x = rectInter + tmp_inter
        top_left_y = tmp_inter

        painter.drawRect(top_left_x, top_left_y, rectWidth / 2, rectHeight / 2)
        painter.end()

        self.widget_cursor.setPixmap(pixmap1)
        self.widget_cursor.setGeometry(0, 0, rectWidth, rectHeight)
        self.widget_cursor.setParent(red_slice_widget)

        self.widget_cursor.setAttribute(qt.Qt.WA_TransparentForMouseEvents, True)

        red_slice_view = red_slice_widget.sliceView()
        height = red_slice_view.height
        flipped_y = height - xyz[1] - rectHeight / 2
        self.widget_cursor.move(xyz[0] - rectWidth / 2, flipped_y)
        self.widget_cursor.show()
        pass

    class ResizableRect(qt.QLabel):
        def __init__(self, parent=None):
            super().__init__(parent)
            self.drag_corner = None
            self.start_pos = None

        def mousePressEvent(self, event):
            if event.button() == qt.Qt.LeftButton:
                for corner in ['top_left', 'top_right', 'bottom_left', 'bottom_right']:
                    if getattr(self, corner).contains(event.pos()):
                        self.drag_corner = corner
                        self.start_pos = event.pos()
                        break

        def mouseMoveEvent(self, event):
            if self.drag_corner:
                delta = event.pos() - self.start_pos
                rect = self.geometry()
                if 'left' in self.drag_corner:
                    rect.setLeft(rect.left() + delta.x())
                if 'right' in self.drag_corner:
                    rect.setRight(rect.right() + delta.x())
                if 'top' in self.drag_corner:
                    rect.setTop(rect.top() + delta.y())
                if 'bottom' in self.drag_corner:
                    rect.setBottom(rect.bottom() + delta.y())
                self.setGeometry(rect)
                self.start_pos = event.pos()

        def mouseReleaseEvent(self, event):
            self.drag_corner = None
            self.start_pos = None

    def start_drawing(self):
        if self.mode != self.MODE_PDI:
            return
        self.rectangle_widget.start_drawing()

    def on_set_power(self):
        power = int(self.ui.edit_power.text)
        if not (1 <= power <= 6):
            util.showWarningText("数值需要设置在1~6之间")
            return
        util.getModuleWidget("RequestStatus").send_cmd(f"UltraImage, SetPower, {power}")

    def set_probes(self, probe):
        self.ui.comboBox_2.addItem(probe)
        pass
