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
from RDNTool.UltraSoundSettingPanel import UltraSoundSettingPanel


#
# RDNDevice
#

class RDNDevice(ScriptedLoadableModule):

    def __init__(self, parent):
        ScriptedLoadableModule.__init__(self, parent)
        self.parent.title = "RDNDevice"  # TODO: make this more human readable by adding spaces
        self.parent.categories = [
            "RDN"]  # TODO: set categories (folders where the module shows up in the module selector)
        self.parent.dependencies = []  # TODO: add here list of module names that this module requires
        self.parent.contributors = ["jia ze yu"]  # TODO: replace with "Firstname Lastname (Organization)"
        # TODO: update with short description of the module and a link to online module documentation
        self.parent.helpText = """

"""
        # TODO: replace with organization, grant and thanks
        self.parent.acknowledgementText = """

"""


#
# RDNDeviceWidget
#

class RDNDeviceWidget(JBaseExtensionWidget):
    timer = None
    check_sequence = ['robot', 'ndi']
    check_index = 0
    check_map = {}
    old_waring_txt = ""
    warning_label = None
    first_init = False
    first_init_pdi = False

    def setup(self):
        super().setup()
        #print("RDNDeviceWidget setup")
        widget = util.getModuleWidget("RequestStatus")
        # widget.connect('on_tick(QString)',self.tickEvent)
        widget.connect('on_tick_python(QString)', self.tickEvent)
        self.TagMaps[19870831] = slicer.mrmlScene.AddObserver(19870831, self.tickEvent)
        # self.add_handler(util.DOUBLE_CAMERA_TYPE_NDI)
        # self.add_handler(util.ROBOT_ARM_TYPE_ELIBOT)
        self.add_handler(util.ROBOT_ARM_TYPE_UR)
        # self.add_handler(util.DOUBLE_CAMERA_TYPE_IME)
        self.add_handler("Power")
        # self.add_handler("Register")
        # self.add_handler("Device")
        self.add_handler("System")
        self.add_handler("WaterControl")
        self.add_handler("UltrasoundGenerator")

        util.global_data_map['UltraSoundSettingPanel'] = UltraSoundSettingPanel(self)
        util.global_data_map['UltraSoundSettingPanel'].show()
        util.singleShot(100, self.init_later)
        util.singleShot(300, self.init_later2)
        # self.add_colorbar()

    def test(self):
        pass

    def init_later(self):
        self.add_handler("UltraImage")

    def init_later2(self):
        util.getModuleWidget("RequestStatus").send_cmd(f"UltraImage, Init")
        # util.getModuleWidget("RequestStatus").send_cmd(f"UltraImage, SetActivateProbe, L40")
        # util.getModuleWidget("RequestStatus").send_cmd(f"UltraImage, SetPreset, Liver")
        # util.getModuleWidget("RequestStatus").send_cmd(f"UltraImage, SetGapMax, 1")
        # util.getModuleWidget("RequestStatus").send_cmd(f"UltraImage, SetLiveGain, {int(100)}")
        # util.getModuleWidget("RequestStatus").send_cmd(f"UltraImage, SetDepth, {16}")
        # util.getModuleWidget("RequestStatus").send_cmd(f"UltraImage, setDebugMode, SaveToBin")
        # util.getModuleWidget("RequestStatus").send_cmd(f"UltraImage, setDebugMode, SaveToPng")
        # util.getModuleWidget("RequestStatus").send_cmd(f"UltraImage, setDebugMode, SaveToPng2")

        # util.getModuleWidget("RequestStatus").send_cmd(f"UltraImage, CaculateBModeFPS")
        # util.getModuleWidget("RequestStatus").send_cmd(f"UltraImage, CaculateTModeFPS")
        # util.getModuleWidget("RequestStatus").send_cmd(f"UltraImage, CaculatePDIModeFPS")
        # util.getModuleWidget("RequestStatus").send_cmd(f"UltraImage, SaveToBinFlag")
        # probe_info = util.getModuleWidget("RequestStatus").send_cmd(f"UltraImage, GetProbe").split(",")
        # util.global_data_map['UltraSoundSettingPanel'].set_probes(probe_info[1])
        # #print(f"depth is -----{util.global_data_map['ultra_depth']}")

        # from RDNTool.ConnectInfo import ConnectInfo
        # info = ConnectInfo()

        # qwidget = qt.QWidget()
        # qwidget.setParent(slicer.app.layoutManager().sliceWidget("Red"))
        # qwidget.setParent(slicer.app.layoutManager().threeDWidget(0).threeDView())
        # util.addWidget2(qwidget,info.uiWidget)
        # qwidget.geometry = qt.QRect(30,700,80,360)
        # qwidget.show()
        return
        # 更改键盘鼠标操作类型
        threeDViewWidget = slicer.app.layoutManager().threeDWidget(0)
        view = threeDViewWidget.threeDView()
        viewNode = view.mrmlViewNode()
        renderer = view.renderWindow().GetRenderers().GetItemAsObject(0)
        camera = renderer.GetActiveCamera()
        cameraDisplayableManager = view.displayableManagerByClassName("vtkMRMLCameraDisplayableManager")
        cameraWidget = cameraDisplayableManager.GetCameraWidget()
        # cameraWidget.SetEventTranslation(slicer.vtkMRMLAbstractWidget.WidgetStateIdle, vtk.vtkCommand.LeftButtonDoubleClickEvent, vtk.vtkEvent.NoModifier, 3)

        EventTranslators = cameraWidget.GetEventTranslator(slicer.vtkMRMLAbstractWidget.WidgetStateIdle)
        EventTranslators.ClearEvents()

        cameraWidget.SetEventTranslationClickAndDrag(slicer.vtkMRMLAbstractWidget.WidgetStateIdle,
                                                     vtk.vtkCommand.LeftButtonPressEvent, vtk.vtkEvent.NoModifier,
                                                     slicer.vtkMRMLAbstractWidget.WidgetStateRotate,
                                                     slicer.vtkMRMLAbstractWidget.WidgetEventRotateStart,
                                                     slicer.vtkMRMLAbstractWidget.WidgetEventRotateEnd)

    def add_colorbar(self):
        uiWidget = slicer.util.loadUI(self.resourcePath('UI/ColorBarUI.ui'))
        ui = slicer.util.childWidgetVariables(uiWidget)
        colorbar_size = [10 * 3, 256 * 3]
        ui.label_2.setFixedSize(colorbar_size[0], colorbar_size[1])
        util.add_pixelmap_to_label(self.resourcePath('UI/colorbar1.jpg'), ui.label_2)
        qwidget = qt.QWidget()
        qwidget.setParent(slicer.app.layoutManager().sliceWidget("Red"))
        util.addWidget2(qwidget, uiWidget)
        qwidget.geometry = qt.QRect(50, 50, colorbar_size[0], colorbar_size[1] + 30)
        qwidget.show()

    def add_test_ultrasound_data2(self):
        volume = util.EnsureFirstNodeByNameByClass("ultrasound_volueC", "vtkMRMLVectorVolumeNode")
        image_path = self.resourcePath("TestData/imageDataC.bin")
        from PIL import Image
        import io

        # 定义数据的类型和形状
        dtype = np.uint8  # 假设每个数据项为float32类型
        shape = (640, 480, 4)  # 目标数组的形状

        # 从.bin文件中读取数据
        with open(image_path, 'rb') as f:
            data = np.fromfile(f, dtype=dtype)
        # 确保数据大小正确
        #print(data.size)
        # 重塑数组为所需形状
        numpy_data = data.reshape(480, 640, 4)
        numpy_data = numpy_data[::-1, ::-1]
        numpy_data = numpy_data[np.newaxis, :, :, :]
        util.updateVolumeFromArray(volume, numpy_data)

        util.GetDisplayNode(volume).SetViewNodeIDs(["vtkMRMLSliceNodeRed"])

        redSliceLogic = slicer.app.layoutManager().sliceWidget("Red").sliceLogic()
        redSliceLogic.GetSliceCompositeNode().SetForegroundVolumeID(volume.GetID())
        redSliceLogic.GetSliceNode().SetOrientationToAxial()
        redSliceLogic.SetSliceOffset(0)
        redSliceLogic.GetSliceNode().SetSliceVisible(False)
        redSliceLogic.FitSliceToAll()
        redSliceLogic.GetSliceCompositeNode().SetForegroundOpacity(0.3)
        return

    def on_draw_focus_line(self):
        horizonal_gap = 200
        horizonal_gap2 = 0
        cred = 1
        cgreen = 0
        cblue = 0
        shape = [640, 480, 200]
        # 假设我们已经有了Volume Node，这里我们用'volumeNode'来表示
        volumeNode = util.EnsureFirstNodeByNameByClass("ultrasound_volue", util.vtkMRMLScalarVolumeNode)
        # 获取IJK到RAS的变换矩阵
        ijkToRASMatrix = vtk.vtkMatrix4x4()
        volumeNode.GetIJKToRASMatrix(ijkToRASMatrix)
        # 体素的IJK坐标
        ijkCoordinates = [shape[1] - horizonal_gap2, shape[0], 0, 1]  # 齐次坐标，最后的1是为了矩阵乘法
        # 将IJK坐标转换为RAS坐标
        rasCoordinates = [0, 0, 0, 1]  # 初始化RAS坐标
        ijkToRASMatrix.MultiplyPoint(ijkCoordinates, rasCoordinates)

        p1 = util.EnsureFirstNodeByNameByClass("ultra_focus_line_start_point", util.vtkMRMLMarkupsFiducialNode,
                                               delete=True)
        p1.AddControlPointWorld(vtk.vtkVector3d(rasCoordinates[0], rasCoordinates[1], rasCoordinates[2]))

        ijkCoordinates = [horizonal_gap, shape[0], 0, 1]  # 齐次坐标，最后的1是为了矩阵乘法
        # 将IJK坐标转换为RAS坐标
        rasCoordinates = [0, 0, 0, 1]  # 初始化RAS坐标
        ijkToRASMatrix.MultiplyPoint(ijkCoordinates, rasCoordinates)

        p2 = util.EnsureFirstNodeByNameByClass("ultra_focus_line_start_2point", util.vtkMRMLMarkupsFiducialNode,
                                               delete=True)
        p2.AddControlPointWorld(vtk.vtkVector3d(rasCoordinates[0], rasCoordinates[1], rasCoordinates[2]))

        ijkCoordinates = [300, shape[2], 0, 1]  # 齐次坐标，最后的1是为了矩阵乘法
        # 将IJK坐标转换为RAS坐标
        rasCoordinates = [0, 0, 0, 1]  # 初始化RAS坐标
        ijkToRASMatrix.MultiplyPoint(ijkCoordinates, rasCoordinates)

        p3 = util.EnsureFirstNodeByNameByClass("ultra_focus_line_start_3point", util.vtkMRMLMarkupsFiducialNode,
                                               delete=True)
        p3.AddControlPointWorld(vtk.vtkVector3d(rasCoordinates[0], rasCoordinates[1], rasCoordinates[2]))
        self.hide_label(p1)
        self.hide_label(p2)
        self.hide_label(p3)
        util.HideNode(p1)
        util.HideNode(p2)
        util.GetDisplayNode(p3).SetGlyphType(1)
        util.GetDisplayNode(p3).SetActiveColor(cred, cgreen, cblue)
        util.GetDisplayNode(p3).SetSelectedColor(cred, cgreen, cblue)
        util.GetDisplayNode(p3).SetGlyphScale(5)
        util.GetDisplayNode(p3).SetTextScale(0)
        line1 = util.EnsureFirstNodeByNameByClass("ultra_focus_line_1", util.vtkMRMLMarkupsLineNode, delete=True)
        self.draw_line(line1, p1, p3, thickness=0.1, red=cred, green=cgreen, blue=cblue)
        line2 = util.EnsureFirstNodeByNameByClass("ultra_focus_line_2", util.vtkMRMLMarkupsLineNode, delete=True)
        self.draw_line(line2, p2, p3, thickness=0.1, red=cred, green=cgreen, blue=cblue)
        util.GetDisplayNode(line1).SetOpacity(0.5)
        util.GetDisplayNode(line2).SetOpacity(0.5)
        util.GetDisplayNode(p3).SetOpacity(0.5)
        line1.SetLocked(1)
        line2.SetLocked(1)
        p3.SetLocked(1)

    def add_test_ultrasound_data(self):
        is_MODE_PDI = util.global_data_map['UltraSoundSettingPanel'].mode == "MODE_PDI"
        # #print("add_test_ultrasound_data")
        volume = util.EnsureFirstNodeByNameByClass("ultrasound_volue", "vtkMRMLVectorVolumeNode")
        pdi_volume = util.EnsureFirstNodeByNameByClass("ultrasound_pdi", "vtkMRMLVectorVolumeNode")

        dimensions = volume.GetImageData().GetDimensions()
        width = dimensions[0]
        height = dimensions[1]
        # #print(f"height and width is---{height},{width}")

        redSliceLogic = slicer.app.layoutManager().sliceWidget("Red").sliceLogic()
        # info = util.getModuleWidget("RequestStatus").send_synchronize_cmd("UltraImage, GetMITI")
        # util.global_data_map['UltraSoundSettingPanel'].label_info.update_info(info)
        if not self.first_init:
            # util.global_data_map['UltraSoundSettingPanel'].on_ctkSliderWidgetChanged(3)
            # #print("first initialization add ultrasound data")
            util.GetDisplayNode(volume).SetViewNodeIDs(["vtkMRMLSliceNodeRed"])
            util.GetDisplayNode(pdi_volume).SetViewNodeIDs(["vtkMRMLSliceNodeRed"])

            redSliceLogic.GetSliceCompositeNode().SetBackgroundVolumeID(volume.GetID())

            displaynode = util.GetDisplayNode(volume)
            displaynode.AutoWindowLevelOff()
            displaynode.SetWindow(100)
            displaynode.SetLevel(50)
            displaynode = util.GetDisplayNode(pdi_volume)
            displaynode.AutoWindowLevelOff()
            displaynode.SetWindow(60)
            displaynode.SetLevel(40)
            displaynode.SetAutoThreshold(False)
            displaynode.SetApplyThreshold(True)
            displaynode.SetThreshold(0, 255)

            self.first_init = True
        else:
            # #print("continuing add ultrasound data")
            volume.Modified()
            compositeNode = redSliceLogic.GetSliceCompositeNode()
            compositeNode.SetBackgroundVolumeID(volume.GetID())
            redSliceLogic.FitSliceToAll()
            redSliceLogic.SetSliceOffset(0)

            ijkToRasMatrix = vtk.vtkMatrix4x4()
            volume.GetIJKToRASMatrix(ijkToRasMatrix)
            # 定义四个角的顶点在IJK坐标系中的位置
            corners_ijk = [
                [0, 0, 0, 1],  # 左上角
                [width - 1, 0, 0, 1],  # 右上角
                [0, height - 1, 0, 1],  # 左下角
                [width - 1, height - 1, 0, 1]  # 右下角
            ]
            # 从IJK坐标系转换到RAS坐标系
            ijkToRasMatrix = vtk.vtkMatrix4x4()
            volume.GetIJKToRASMatrix(ijkToRasMatrix)
            corners_ras = []
            for corner in corners_ijk:
                ras_point = [0, 0, 0, 1.0]
                ijkToRasMatrix.MultiplyPoint(corner, ras_point)
                corners_ras.append(ras_point)
            # return
            rasToXyMatrix = vtk.vtkMatrix4x4()
            sliceNode = slicer.app.layoutManager().sliceWidget("Red").mrmlSliceNode()
            tmp = sliceNode.GetXYToRAS()
            rasToXyMatrix.DeepCopy(tmp)
            rasToXyMatrix.Invert()  # We need the inverse of the XY to RAS matrix
            corners_xy = []
            for ras in corners_ras:
                xy_point = [0, 0, 0, 1.0]
                rasToXyMatrix.MultiplyPoint(ras, xy_point)
                corners_xy.append(xy_point)

            # 输出四个角的顶点在XY坐标系中的位置
            # #print("Corners in XY coordinates:")
            # for i, xy in enumerate(corners_xy):
            #     #print(f"Corner {i+1}: {xy[:2]}")
            # util.global_data_map['UltraSoundSettingPanel'].focus_widget.update_pos(corners_xy[0][:2], corners_xy[1][:2])
            util.GetDisplayNode(volume).SetViewNodeIDs(["vtkMRMLSliceNodeRed"])

            if is_MODE_PDI:
                util.ShowNode(pdi_volume)
                pdi_volume.Modified()
                compositeNode.SetForegroundVolumeID(pdi_volume.GetID())
                compositeNode.SetForegroundOpacity(0.6)
                #util.GetDisplayNode(pdi_volume).SetViewNodeIDs(["vtkMRMLSliceNodeRed"])

                if not self.first_init_pdi:
                    try:
                        pdi_image = pdi_volume.GetImageData()
                        #print('start write pdi_volume!', pdi_image)
                        dim = pdi_image.GetDimensions()
                        #print(dim)
                        w_png = vtk.vtkPNGWriter()
                        w_png.SetInputData(pdi_volume.GetImageData())
                        w_png.SetFileName('D:/2/tmp/testPDI.png')
                        w_png.Write()
                    except:
                        #print('output pdi_volume error!')
                        pass
                    self.first_init_pdi = True
            else:
                util.HideNode(pdi_volume)
                compositeNode.SetForegroundVolumeID(None)

            slicer.app.layoutManager().sliceWidget("Red").sliceView().forceRender()
        return

    def add_tmp_file(self):
        volume = util.EnsureFirstNodeByNameByClass("ultrasound_pdi", "vtkMRMLVectorVolumeNode")
        image_path = "D:/2/tmp_pdi.bin"
        # image_path = r"D:\Branch\puray\GLPyModule\JExtension\RDNDevice\Resources\TestData\imageDataC.bin"
        from PIL import Image
        import io

        # 定义数据的类型和形状
        dtype = np.uint8  # 假设每个数据项为float32类型
        shape = (640, 480, 4)  # 目标数组的形状

        # 从.bin文件中读取数据
        with open(image_path, 'rb') as f:
            data = np.fromfile(f, dtype=dtype)
        # 确保数据大小正确
        # 重塑数组为所需形状
        numpy_data = data.reshape(480, 640, 4)
        numpy_data = numpy_data[::-1, ::-1]
        numpy_data = numpy_data[np.newaxis, :, :, :]
        util.updateVolumeFromArray(volume, numpy_data)

        util.GetDisplayNode(volume).SetViewNodeIDs(["vtkMRMLSliceNodeRed"])

        redSliceLogic = slicer.app.layoutManager().sliceWidget("Red").sliceLogic()
        redSliceLogic.GetSliceCompositeNode().SetForegroundVolumeID(volume.GetID())
        redSliceLogic.GetSliceCompositeNode().SetForegroundOpacity(1)

    def OnArchiveLoaded(self, _a, _b):
        #print("RDNDeviceWidget::OnArchiveLoaded")
        # util.singleShot(1000,self.init_OnArchiveLoaded)
        pass

    def init_OnArchiveLoaded(self):
        util.getModuleWidget("RequestStatus").send_cmd(f"IME, SetGapMax, 31")
        util.getModuleWidget("RequestStatus").send_cmd(f"UR, SetGapMax, 31")
        # util.getModuleWidget("JIMEConnector").connect_IME()
        # util.getModuleWidget("JURRobotArm").on_robot_arm_connect()
        util.getModuleWidget("RequestStatus").send_cmd(f"Register, SetGapMax, 40")
        # util.singleShot(20000,lambda: util.getModuleWidget("RequestStatus").bind_subthreads(["UR","IME","Register"],True))
        # util.singleShot(60000,lambda: util.getModuleWidget("RequestStatus").bind_subthreads(["UR","IME","Register"],False))

    def bind_subthreads(self):
        val = util.getModuleWidget("RequestStatus").bind_subthreads(["UR", "IME"], True)
        #print(val)

    def add_handler(self, key):
        if key in [util.DOUBLE_CAMERA_TYPE_IME, util.DOUBLE_CAMERA_TYPE_NDI]:
            util.double_camera_type = key
        if key in [util.ROBOT_ARM_TYPE_ELIBOT, util.ROBOT_ARM_TYPE_UR]:
            util.robot_arm_type = key
        util.getModuleWidget("RequestStatus").add_handler(key)

    def init_label(self):
        if self.warning_label is None:
            self.warning_label = qt.QLabel()
            qwidget = qt.QWidget()
            qwidget.setParent(slicer.app.layoutManager().sliceWidget("Red"))
            self.warning_label.setAlignment(qt.Qt.AlignCenter)
            util.addWidget2(qwidget, self.warning_label)

            qwidget.geometry = util.getModuleWidget("RDNTreat").treat_layout.get_warning_layout()
            qwidget.show()

    def get_warning_layout(self):
        widget_width = 300
        widget_height = 50
        return qt.QRect((self.width - widget_width) / 2, self.gap, widget_width, widget_height)

    @vtk.calldata_type(vtk.VTK_OBJECT)
    def tickEvent(self, info1):
        try:
            self._tickEvent(info1)
        except Exception as e:
            util.write_rdn_communicate_log(e.__str__())

    def _tickEvent(self, info1):
        #print(info1)
        all_info_list = info1.split("&H&, ")
        for row in all_info_list:
            key_pair_list = row.split("*Y*, ")
            #print("CAAAA:",len(key_pair_list),key_pair_list[0])
            if len(key_pair_list) != 2:
                continue
            key = key_pair_list[0]
            value = key_pair_list[1]
            #print("21")
            map_info = {}
            info_list_str = value.split("*V* ")
            for row in info_list_str:
                if row == "":
                    continue
                key_value_pair_list = row.split("*U* ")
                assert (len(key_value_pair_list) == 2)
                key1 = key_value_pair_list[0]
                value1 = key_value_pair_list[1]
                map_info[key1] = value1
            #print("31")
            util.write_rdn_communicate_log(key + "->" + map_info.__str__())
            #print("41")
            # #print(f"key is {key} and value is {map_info.__str__()}")
            #if 'fsm' in util.global_data_map:
            #    util.global_data_map['fsm'].tickEvent(key, map_info)

            # if key == "IME":
            #     util.getModuleWidget("JIMEConnector").tickEvent(value)
            # elif key == "NDI":
            #     util.getModuleWidget("JNDIConnector").tickEvent(value)
            #     pass
            # elif key == "Elibot":
            #     util.getModuleWidget("JRobotArm").tickEvent(value)
            #     pass
            #print("51",key=="UltrasoundGenerator",key)
            if key == "UR":
                util.getModuleWidget("JURRobotArm").tickEvent(value)
                pass
            elif key == "USBHid":
                util.getModuleWidget("JUSBConnector").tickEvent(value)
                pass
            elif key == "Register":
                util.getModuleWidget("RDNTreat").OnRDNCurveUpdate(value)
                pass
            #elif key == "System":
               # util.getModuleWidget("JSystemInfo").tickEvent(value)
                #pass
            elif key == "Power":
                util.getModuleWidget("JPowerControl").tickEvent(value)
                pass
            elif key == "UltrasoundGenerator":
                util.getModuleWidget("JUltrasoundGenerator").tickEvent(value)
            elif key == "WaterControl":
                util.getModuleWidget("JWaterControl").tickEvent(value)
                pass
            elif key == "UltraImage":
                self.add_test_ultrasound_data()
                # util.global_data_map['UltraSoundSettingPanel'].tickEvent(value)
                pass
            elif key == "Device":
                pass
