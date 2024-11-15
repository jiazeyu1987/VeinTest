import slicer
from slicer.ScriptedLoadableModule import *
from slicer.util import VTKObservationMixin
from ConfigTools.URController import URController
from ConfigTools.DetailInfo import HistoryDetailPanel
from ConfigTools.WaterBladder import WaterBladder
import qt
import slicer.util as util
import os


#
# VeinConfig
#


class VeinConfig(ScriptedLoadableModule):
    """Uses ScriptedLoadableModule base class, available at:
    https://github.com/Slicer/Slicer/blob/main/Base/Python/slicer/ScriptedLoadableModule.py
    """

    def __init__(self, parent):
        ScriptedLoadableModule.__init__(self, parent)
        self.parent.title = "VeinConfig"  # TODO: make this more human readable by adding spaces
        # TODO: set categories (folders where the module shows up in the module selector)
        self.parent.categories = ["Examples"]
        self.parent.dependencies = []  # TODO: add here list of module names that this module requires
        self.parent.contributors = [
            "John Doe (AnyWare Corp.)"]  # TODO: replace with "Firstname Lastname (Organization)"
        # TODO: update with short description of the module and a link to online module documentation
        # _() function marks text as translatable to other languages
        self.parent.helpText = ("""
This is an example of scripted loadable module bundled in an extension.
See more information in <a href="https://github.com/organization/projectname#LineIntensityProfile">module documentation</a>.
""")
        # TODO: replace with organization, grant and thanks
        self.parent.acknowledgementText = ("""
This file was originally developed by Jean-Christophe Fillion-Robin, Kitware Inc., Andras Lasso, PerkLab,
and Steve Pieper, Isomics, Inc. and was partially funded by NIH grant 3P41RR013218-12S1.
""")


#
# LineIntensityProfileWidget
#


class VeinConfigWidget(ScriptedLoadableModuleWidget, VTKObservationMixin):
    """Uses ScriptedLoadableModuleWidget base class, available at:
    https://github.com/Slicer/Slicer/blob/main/Base/Python/slicer/ScriptedLoadableModule.py
    """

    def __init__(self, parent=None) -> None:
        """Called when the user opens the module the first time and the widget is initialized."""
        ScriptedLoadableModuleWidget.__init__(self, parent)
        VTKObservationMixin.__init__(self)  # needed for parameter node observation
        self.logic = None
        self._parameterNode = None
        self._parameterNodeGuiTag = None

    def setup(self) -> None:
        """Called when the user opens the module the first time and the widget is initialized."""
        ScriptedLoadableModuleWidget.setup(self)

        # Load widget from .ui file (created by Qt Designer).
        # Additional widgets can be instantiated manually and added to self.layout.
        self.uiWidget = slicer.util.loadUI(self.resourcePath("UI/VeinConfig.ui"))
        self.layout.addWidget(self.uiWidget)
        self.ui = slicer.util.childWidgetVariables(self.uiWidget)

        # Set scene in MRML widgets. Make sure that in Qt designer the top-level qMRMLWidget's
        # "mrmlSceneChanged(vtkMRMLScene*)" signal in is connected to each MRML widget's.
        # "setMRMLScene(vtkMRMLScene*)" slot.
        self.uiWidget.setMRMLScene(slicer.mrmlScene)
        self.vein_to_id = dict()

        #self.init_extra_database()
        self.init_ui()

    def init_extra_database(self):
        import sqlite3
        database_path = os.path.join(util.mainWindow().GetProjectBasePath(), "Resources", "Database", "client",
                                     "ctkDICOM.sql")
        # 连接到数据库
        self.conn = sqlite3.connect(database_path)
        # 创建一个游标对象，用于执行 SQL 语句
        self.cursor = self.conn.cursor()

    def init_ui(self):
        # 删除按钮
        self.ui.btn_delete.setEnabled(False)
        self.ui.btn_delete.clicked.connect(self.del_item)

        # 新增血管按钮
        self.ui.btn_add_vein.clicked.connect(self.add_vein)

        # 新增段落按钮
        self.ui.btn_add_segment.setEnabled(False)
        self.ui.btn_add_segment.clicked.connect(self.add_segment)
        self.ui.tabWidget.tabBar().hide()

        left_layout = qt.QVBoxLayout(self.ui.widget_left)

        self.tree = qt.QTreeWidget()
        self.tree.setColumnCount(4)  # 设置四列
        self.tree.setHeaderHidden(True)
        self.tree.itemClicked.connect(self.on_item_clicked)

        font = qt.QFont()
        font.setPointSize(15)
        self.tree.setFont(font)
        self.tree.setIconSize(qt.QSize(30, 30))

        self.plus_icon = self.resourcePath("Icons/plus.svg").replace("\\", "/")
        self.minus_icon = self.resourcePath("Icons/minus.svg").replace("\\", "/")

        # 设置列宽
        self.tree.header().setSectionResizeMode(qt.QHeaderView.Interactive)
        self.tree.setColumnWidth(0, 200)  # 设置第1列宽度
        self.tree.setColumnWidth(1, 100)  # 设置第2列宽度（空列）
        self.tree.setColumnWidth(2, 100)  # 设置第3列宽度（空列）
        self.tree.setColumnWidth(3, 100)  # 设置第4列宽度（按钮列）

        left_layout.addWidget(self.tree)
        left_layout.addWidget(self.ui.shared_textbox)
        self.tree.setStyleSheet(f"""
            QTreeWidget::branch:closed:has-children {{
                image: url({self.plus_icon});
            }}
            QTreeWidget::branch:open:has-children {{
                image: url({self.minus_icon});
            }}
        """)

        # 共享文本框
        self.ui.shared_textbox.setPlaceholderText("Click to edit...")
        left_layout.addWidget(self.ui.shared_textbox)

        # 嵌入机器人控制按钮
        self.UR_controller = URController()
        util.addWidget2(self.ui.widget_mid, self.UR_controller.uiWidget)

        # 超声调整
        self.ul_setting_panel = None
        self.ui.btn_ul_adjust.clicked.connect(self.show_UL_setting_panel)

        self.water_bladder = WaterBladder()
        util.global_data_map['WaterBladder'] = self.water_bladder
        self.water_bladder_show = False

    def enter(self):
        self.tree.clear()
        util.patient_segments_veins.clear()
        self.id = util.global_data_map["patientID"]
        self.cursor.execute(f'SELECT * FROM VeinInfo WHERE PatientID = ?', (self.id,))
        util.global_data_map['is_closed_water'] = False
        items_list = self.cursor.fetchall()

        for item in items_list:
            vein_id, _, vein_name = item
            vein_item = qt.QTreeWidgetItem(self.tree, [vein_name])
            vein_item.setChildIndicatorPolicy(qt.QTreeWidgetItem.ShowIndicator)
            vein_item.setExpanded(False)  # 初始状态下不展开
            self.vein_to_id[vein_name] = vein_id
            self.cursor.execute(f'SELECT * FROM SegmentInfo WHERE VeinID = ?', (vein_id,))
            segment_items_list = self.cursor.fetchall()
            util.patient_segments_veins[vein_name] = {}
            if segment_items_list is None:
                continue

            for item in segment_items_list:
                segment_id, _, segment_name, is_treated, *_ = item
                util.patient_segments_veins[vein_name][segment_name] = segment_id
                segment_item = qt.QTreeWidgetItem(vein_item, [segment_name])
                segment_item.setChildIndicatorPolicy(qt.QTreeWidgetItem.DontShowIndicatorWhenChildless)
                segment_item.setExpanded(False)  # 初始状态下不展开
                self.add_buttons_to_segment(segment_item, is_treated)
        if not self.water_bladder_show:
            self.water_bladder.show()
            self.water_bladder_show = True

    def on_item_clicked(self, item, column):
        if item.parent() is None:  # 判断是否为 Vein 项
            self.ui.btn_add_segment.setEnabled(True)
            self.ui.btn_delete.setEnabled(True)
            self.toggle_vein(item)
        elif item.parent().parent() is None:  # 如果是子项，则为 Segment 项
            self.ui.btn_add_segment.setEnabled(False)
            self.ui.btn_delete.setEnabled(True)
            self.toggle_segment(item)
        else:
            self.ui.btn_add_segment.setEnabled(False)
            self.ui.btn_delete.setEnabled(False)

    def toggle_vein(self, item):
        item.setExpanded(not item.isExpanded())
        # print(f"item expanded flag is {item.isExpanded()}")
        # print(f"item's child count is {item.childCount()}")
        for i in range(item.childCount()):
            child = item.child(i)
            # print(f"child is {child}")
            child.setHidden(not item.isExpanded())

    def toggle_segment(self, item):
        item.setExpanded(not item.isExpanded())
        if item.isExpanded():
            self.display_ultrasound_images(item)
        else:
            self.clear_ultrasound_images(item)

    def display_ultrasound_images(self, item):
        # 这里应根据实际情况加载并显示超声缩略图
        # 例如，动态创建 QLabel 控件并设置图片
        segment_id = util.patient_segments_veins[item.parent().text(0)][item.text(0)]
        self.cursor.execute("SELECT ImageList FROM SegmentInfo WHERE ID = ?", (segment_id,))
        images = self.cursor.fetchone()[0].split(";")
        if images[0] == '':
            return
        for image in images:
            label = qt.QLabel()
            pixmap = qt.QPixmap(image)
            thumbnail_pixmap = pixmap.scaled(100, 100, qt.Qt.KeepAspectRatio)
            label.setPixmap(thumbnail_pixmap)
            ultrasound_item = qt.QTreeWidgetItem(item, ["", "", "", ""])  # 确保有四列空间
            self.tree.setItemWidget(ultrasound_item, 0, label)

    def clear_ultrasound_images(self, item):
        # 清除所有子项（超声缩略图）
        for i in reversed(range(item.childCount())):
            child = item.child(i)
            if self.tree.itemWidget(child, 0) is not None:
                self.tree.removeItemWidget(child, 0)
            item.removeChild(child)

    def del_item(self):
        selected_item = self.tree.selectedItems()[0] if self.tree.selectedItems() else None
        if selected_item is None:
            return
        if selected_item.parent() is None:  # 删除 Vein 和所有子项
            index = self.tree.indexOfTopLevelItem(selected_item)
            self.tree.takeTopLevelItem(index)
            vein_id = self.vein_to_id[selected_item.text(0)]
            self.cursor.execute('DELETE from VeinInfo where id=?', (vein_id,))
            self.cursor.execute('DELETE from SegmentInfo where VeinID=?', (vein_id,))
        elif selected_item.parent().parent() is None:  # 删除当前 Segment
            parent = selected_item.parent()
            index = parent.indexOfChild(selected_item)
            parent.takeChild(index)
            segment_id = util.patient_segments_veins[selected_item.parent().text(0)][selected_item.text(0)]
            self.cursor.execute('DELETE from SegmentInfo where id=?', (segment_id,))
        self.conn.commit()

    def add_vein(self):
        vein_name = f"Vein{self.tree.topLevelItemCount + 1}"
        vein_item = qt.QTreeWidgetItem(self.tree, [vein_name])
        vein_item.setChildIndicatorPolicy(qt.QTreeWidgetItem.ShowIndicator)
        # vein_item.setIcon(0, qt.QIcon(self.plus_icon))
        vein_item.setExpanded(False)  # 初始状态下不展开
        self.cursor.execute('''INSERT INTO VeinInfo (PatientID, VeinName)
        VALUES (?, ?)''', (self.id, vein_name))
        self.vein_to_id[vein_name] = self.cursor.lastrowid
        self.conn.commit()

    def add_segment(self):
        parent_item = self.tree.selectedItems()[0] if self.tree.selectedItems() else None
        if parent_item is None:
            return
        segment_count = parent_item.childCount()
        segment_name = f"Segment{segment_count + 1}"
        parent_item.setExpanded(True)
        vein_id = self.vein_to_id[parent_item.text(0)]
        self.cursor.execute('''INSERT INTO SegmentInfo (VeinID, SegmentName, Pos, Power,Energy,ImageList)
        VALUES (?, ?, ?, ?, ?, ?)''', (vein_id, segment_name, '', '', '', ''))
        segment_id = str(self.cursor.lastrowid)
        self.conn.commit()
        util.patient_segments_veins[parent_item.text(0)] = {segment_name: segment_id}
        segment_item = qt.QTreeWidgetItem(parent_item, [segment_name, "", "", ""])  # 确保有四列空间
        segment_item.setChildIndicatorPolicy(qt.QTreeWidgetItem.DontShowIndicatorWhenChildless)
        segment_item.setExpanded(False)  # 初始状态下不展开
        parent_item.setExpanded(True)
        self.add_buttons_to_segment(segment_item)

    def add_buttons_to_segment(self, item, is_treated=0):
        # 详情按钮
        details_button = qt.QPushButton("详情")
        details_button.setFixedWidth(50)  # 设置按钮宽度

        # 治疗按钮
        treatment_button = qt.QPushButton("治疗")
        treatment_button.setFixedWidth(50)  # 设置按钮宽度

        container = qt.QWidget()
        util.addWidget2(container, details_button)
        util.addWidget2(container, treatment_button)
        util.addWidget2(self.tree, container)

        self.tree.setItemWidget(item, 3, container)  # 将按钮容器添加到第 4 列

        details_button.clicked.connect(lambda: self.show_details(item))
        treatment_button.clicked.connect(lambda: self.go_to_treat(item))
        if is_treated == 1:
            treatment_button.setEnabled(False)

        # 无参数正确写法
        # treatment_button.clicked.connect(self.go_to_treat)
        # 有参数错误写法，这样show_details在connect连接时就执行了
        # details_button.clicked.connect(self.show_details(item))

    def show_details(self, item):
        item_text = item.text(0)
        parent_text = item.parent().text(0)
        vein_info = parent_text + "--" + item_text
        segment_id = util.patient_segments_veins[parent_text][item_text]
        self.cursor.execute("SELECT Pos,Power,Energy,ImageList FROM SegmentInfo WHERE ID = ?", (segment_id,))
        detail_info = self.cursor.fetchone()
        history_detail_panel = HistoryDetailPanel(vein_info, detail_info)
        history_detail_panel.show()

    def go_to_treat(self, item):
        segment_name = item.text(0)
        # vein_name = item.parent().text(0)
        # patientID = util.global_data_map["patientID"]
        segment_id = util.patient_segments_veins[item.parent().text(0)][segment_name]
        util.global_data_map["segmentID"] = segment_id
        # util.global_data_map["segment_id_pic_name"] = (
        #     segment_id, str(patientID) + "_" + vein_name + "_" + segment_name)

        util.send_event_str(util.SetPage, 5)

    # 超声控制面板
    def show_UL_setting_panel(self) -> None:
        if self.ui.btn_ul_adjust.text == "超声调整":
            self.ui.tabWidget.setCurrentIndex(0)
            self.ui.btn_ul_adjust.setText("超声参数")
        else:
            self.ui.tabWidget.setCurrentIndex(1)
            self.ui.btn_ul_adjust.setText("超声调整")
