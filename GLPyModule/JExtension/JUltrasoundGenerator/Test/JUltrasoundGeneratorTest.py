from Base.JBaseTest import JBaseTest
import vtk, qt, ctk, slicer, os
import slicer.util as util
import time
import psutil,datetime
class JUltrasoundGeneratorTest(JBaseTest):
  key_points = []
  TagMaps = {}
  map_info = {}
  def runTest(self):
    self.module_path = os.path.realpath(__file__)
    self.module_directory = os.path.dirname(os.path.realpath(__file__))
    
    super().runTest()
    self.init_paras()
  
  def init_paras(self):
    # util.mainWindow().setFixedWidth(1920*2)
    # self.get_center_widget().show()
    # ModuleName = "RDNPrepare"
    # width = 320
    # if  util.isPackage():
    #   util.layout_panel("middle_right").hide()
    # else:
    #   util.layout_panel("middle_right").setMaximumWidth(width)
    #   util.layout_panel("middle_right").setMinimumWidth(width)
    #   util.layout_panel("middle_right").show()
    #   util.layout_panel("middle_right").setModule("Data")
    # util.layout_panel("middle_left").setMaximumWidth(width)
    # util.layout_panel("middle_left").setMinimumWidth(width)
    # util.layout_panel("middle_left").setModule(ModuleName)
    # util.layout_panel("middle_left").GetModuleWidget().setMaximumWidth(width)
    # util.layout_panel("middle_left").GetModuleWidget().setMinimumWidth(width)
    # util.layout_panel("middle_left2").setModule("JMeasure")
    # util.layout_panel("middle_left2").show()
    # util.layout_panel("middle_left2").setMaximumWidth(60)
    # util.layout_panel("middle_left2").setMinimumWidth(60)
    
    layoutManager = slicer.app.layoutManager()
    layoutManager.setLayout(809)
    
    self.paramap["open_ultrasound_control_software"] = 200
    self.paramap["default"] = 200
  
  '''
  =============================================================================================
                                                case area
  =============================================================================================
  '''
  
  '''
    进入单元测试页面
  '''
  def reset_page(self):
    slicer.mrmlScene.Clear(0)
    import SampleData
    SampleData.downloadSample("MRHead")
    util.send_event_str(util.SetPage,"5")
   
    self.continue_test(5000)
    
    
  '''
    1.打开电源控制面板
    2.截图保存
  '''
  def open_control_panel(self):
    modulenames = util.moduleNames()
    self.assertIn("JMeasure",modulenames,msg="配置文件里没有加上JMeasure模块")
    widget = util.getModuleWidget("JMeasure")
    measure_tool = widget.get_tool_by_name("usb")
    self.assertIsNotNone(measure_tool)
    measure_tool.btn.setChecked(True)
    util.log_screen_shot(self.module_directory,"open_control_panel.png")
    self.continue_test()
  
  '''
    开始第一组自动化测试
  '''
  def start_bundle_1(self):
    modulenames = util.moduleNames()
    self.assertIn("JUltrasoundGenerator",modulenames,msg="配置文件里没有加上 JUltrasoundGenerator 模块")
    self.continue_test()
    
  
  
  ''' 
  ===========================================================================================================================
    从打开程序到程序与Device开始交互
  ===========================================================================================================================
  '''  
  
  
  
  def check_init_connect_status(self):
    def check_init_connect_status_success_func():
      widget = util.getModuleWidget("JUltrasoundGenerator")
      val = widget.unit.ui.btn_connect.enabled == True
      return val
    self.delay_test("before_connect",check_init_connect_status_success_func,"can't connect io","success_connected_to_io")
  
  
  def test_case(self,in_value):
    super().test_case(in_value)
    if 'tick_gap'in self.paramap:
      util.write_test_log(f"\n\n### Tick {round(self.paramap['tick_gap'], 2)} Second")
    
    if "virtual_memory" in self.paramap:
      memory_now =  psutil.virtual_memory().available
      memory_differ = -(memory_now-self.paramap["virtual_memory"])/ (1024 ** 2)
      util.write_test_log(f"### Memory {round(memory_differ,2)} MB")
  ''' 
  ===========================================================================================================================
    监听接收的数据
  ===========================================================================================================================
  '''
  def add_tick_event_listener(self):
    widget = util.getModuleWidget("RequestStatus")
    self.paramap["virtual_memory"] =  psutil.virtual_memory().available
    widget.connect('on_tick_python(QString)',self.tickEvent)
    self.continue_test()
  
  
  @vtk.calldata_type(vtk.VTK_OBJECT)
  def tickEvent(self,info1):
    if "time_tick" in  self.paramap:
      time_now = time.time()
      tick_gap = time_now-self.paramap["time_tick"]
      self.paramap["time_tick"] = time_now
      self.paramap["tick_gap"] = tick_gap
    else:
      self.paramap["time_tick"] = time.time()
    
      
    
      
    all_info_list = info1.split("&H&, ")
    for row in all_info_list:
      key_pair_list = row.split("*Y*, ")
      if len(key_pair_list)!=2:
        continue
      key = key_pair_list[0]
      value = key_pair_list[1]
      if key == "UltrasoundGenerator":
        self.tickEventultrasound(value)
        
  def tickEventultrasound(self,value):
    self.map_info = {}
    info_list_str = value.split("*V* ")
    for row in info_list_str:
      if row == "":
        continue
      key_value_pair_list = row.split("*U* ")
      assert(len(key_value_pair_list)==2)
      key = key_value_pair_list[0]
      value = key_value_pair_list[1]
      self.map_info[key] = value
    
  
  
  ''' 
  ===========================================================================================================================
    点击连接按钮之后的变化
  ===========================================================================================================================
  '''
  def after_connect(self):
    def connect_ultrasound_device_success_func():
      if "software_status" in self.map_info:
        value = self.map_info["software_status"]
        if value == "-1" :
          return True
    widget = util.getModuleWidget("JUltrasoundGenerator")
    widget.unit.ui.btn_connect.animateClick(0)
    self.delay_test("after_connect_device",connect_ultrasound_device_success_func,"can't connect ultrasound device","success connected to ultrasound device")
    

  ''' 
  ===========================================================================================================================
    点击打开软件之后三秒内的UI变化
  ===========================================================================================================================
  '''
  def open_ultrasound_control_software(self):
    def open_ultrasound_control_software_success_func():
      print(self.map_info)
      if "connect_status" in self.map_info:
        value = self.map_info["connect_status"]
        if value == "1":
            return True
    widget = util.getModuleWidget("JUltrasoundGenerator")
    widget.unit.ui.btn_software_status.animateClick(0)
    self.delay_test("open_ultrasound_control_software",open_ultrasound_control_software_success_func,"can't open software","success open software")

  
  def first_heart_beat(self):
    def first_heart_beat_success_func():
      if "heart_beat" in self.map_info and self.map_info["heart_beat"] != "nan":
        chararray = self.map_info["heart_beat"].split(" ")
        if len(chararray) == 65:
          return True
    widget = util.getModuleWidget("JUltrasoundGenerator")
    widget.unit.ui.btn_software_status.animateClick(0)
    self.delay_test("after_first_heart_beat",first_heart_beat_success_func,"firat heart beat fail","firat heart beat success")
  
  def after_opened_software_ui(self):
    widget = util.getModuleWidget("JUltrasoundGenerator")
    self.assertEqual(widget.unit.ui.btn_connect.text == "已连接",True)
    #self.assertEqual(widget.unit.ui.btn_close_software.enabled,False)
    self.assertEqual(widget.unit.ui.btn_write_switch.enabled,False)
    self.assertEqual(widget.unit.ui.btn_software_status.enabled,False)
    
    self.continue_test()
  
  
  def after_close_software(self):
    def success_func():
      widget = util.getModuleWidget("JUltrasoundGenerator")
      val1 = widget.unit.ui.btn_write_switch.enabled == True
      val2 = widget.unit.ui.btn_close_software.enabled == False
      val3 = widget.unit.ui.btn_software_status.enabled == True
      val4 = widget.unit.ui.btn_connect.enabled == False
      return val1 and val2 and val3 and val4
    widget = util.getModuleWidget("JUltrasoundGenerator")
    widget.unit.ui.btn_close_software.animateClick(0)
    self.delay_test("after_close_software",success_func,f"close software fail","close software success")
  
  def after_open_software(self):
    def success_func():
      widget = util.getModuleWidget("JUltrasoundGenerator")
      val1 = widget.unit.ui.btn_write_switch.enabled == False
      val2 = widget.unit.ui.btn_close_software.enabled == True
      val3 = widget.unit.ui.btn_software_status.enabled == False
      val4 = widget.unit.ui.btn_connect.enabled == False
      return val1 and val2 and val3 and val4
    widget = util.getModuleWidget("JUltrasoundGenerator")
    widget.unit.ui.btn_software_status.animateClick(0)
    self.delay_test("after_open_software",success_func,f"open software fail","open software success")
  
  def after_set_30_power_software(self):
    def success_func():
      if "heart_beat" in self.map_info and self.map_info["heart_beat"] != "nan":
        chararray = self.map_info["heart_beat"].split(" ")
        PA_setting_ug_H = chararray[8]
        PA_setting_ug_L = chararray[9]
        power = (int(PA_setting_ug_H,16)*256+int(PA_setting_ug_L,16))
        PA_output_ug_H = chararray[11]
        PA_output_ug_L = chararray[12]
        output_power = int(PA_output_ug_H,16)*256+int(PA_output_ug_L,16)
        if power == 307 and 297 < output_power < 317:
          return True
    widget = util.getModuleWidget("JUltrasoundGenerator")
    self.assertEqual(widget.ui.btn_start.text == "开启",True)
    widget.ui.le_power.setText("30")
    widget.ui.btn_setting_power.animateClick(0)
    widget.ui.btn_start.animateClick(0)
    self.paramap["after_set_30_power_software"] = 1000
    self.delay_test("after_set_30_power_software",success_func,f"set 30 power fail","set 30 power success")
  
  def close_pa(self):
    def success_func():
      widget = util.getModuleWidget("JUltrasoundGenerator")
      if(widget.ui.btn_start.text == "开启"):
        return True
    widget = util.getModuleWidget("JUltrasoundGenerator")
    self.assertEqual(widget.ui.btn_start.text == "关闭",True)
    widget.ui.btn_start.animateClick(0)
    self.delay_test("close_pa",success_func,f"close pa fail","close pa success")
  
  def after_set_60_power_software(self):
    def success_func():
      if "heart_beat" in self.map_info and self.map_info["heart_beat"] != "nan":
        chararray = self.map_info["heart_beat"].split(" ")
        PA_setting_ug_H = chararray[8]
        PA_setting_ug_L = chararray[9]
        power = (int(PA_setting_ug_H,16)*256+int(PA_setting_ug_L,16))
        PA_output_ug_H = chararray[11]
        PA_output_ug_L = chararray[12]
        output_power = int(PA_output_ug_H,16)*256+int(PA_output_ug_L,16)
        if power == 614 and 604 < output_power < 624:
          return True
    widget = util.getModuleWidget("JUltrasoundGenerator")
    self.assertEqual(widget.ui.btn_start.text == "开启",True)
    widget.ui.le_power.setText("60")
    widget.ui.btn_setting_power.animateClick(0)
    widget.ui.btn_start.animateClick(0)
    self.paramap["after_set_60_power_software"] = 1000
    self.delay_test("after_set_60_power_software",success_func,f"set 60 power fail","set 60 power success")
    
  ''' 
  ===========================================================================================================================
    测试结束
  ===========================================================================================================================
  '''
  def finished(self):
    self.continue_test()