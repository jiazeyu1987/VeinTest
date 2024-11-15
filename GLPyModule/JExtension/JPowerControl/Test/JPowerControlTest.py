from Base.JBaseTest import JBaseTest
import vtk, qt, ctk, slicer, os
import slicer.util as util
import time
import psutil,datetime
class JPowerControlTest(JBaseTest):
  key_points = []
  TagMaps = {}
  map_info = {}
  def runTest(self):
    self.module_path = os.path.realpath(__file__)
    self.module_directory = os.path.dirname(os.path.realpath(__file__))
    
    super().runTest()
    self.init_paras()
  
  def init_paras(self):
    self.paramap["set_fan_80"] = 2000
    self.paramap["set_fan_30"] = 2000
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
    layoutManager = slicer.app.layoutManager()
    layoutManager.setLayout(809)
    self.continue_test(1111)
    
    
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
    self.assertIn("JPowerControl",modulenames,msg="配置文件里没有加上JPowerControl模块")
    self.continue_test()
    
  
  
  ''' 
  ===========================================================================================================================
    从打开程序到程序与Device开始交互
  ===========================================================================================================================
  '''  
  
  
  
  def check_init_connect_status(self):
    def check_init_connect_status_success_func():
      widget = util.getModuleWidget("JPowerControl")
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
      if key == "Power":
        self.tickEventPower(value)
        
  def tickEventPower(self,value):
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
  def connect_power_device(self):
    def connect_power_device_success_func():
      if "connect_status" in self.map_info:
        value = self.map_info["connect_status"]
        if value != "-1" and value != -2:
          return True
    widget = util.getModuleWidget("JPowerControl")
    widget.unit.ui.btn_connect.animateClick(0)
    self.delay_test("after_connect_device",connect_power_device_success_func,"can't connect power device","success connected to power device")
    

  ''' 
  ===========================================================================================================================
    点击打开软件之后三秒内的UI变化
  ===========================================================================================================================
  '''
  def open_power_control_software(self):
    def open_power_control_software_success_func():
      if "software_status" in self.map_info:
        value = self.map_info["software_status"]
        if value == "-1":
          pass
        elif value == "-2":
          pass
        else:
          infolist = value.split(" ")
          if int(infolist[5], 16) == 1:
            return True
    widget = util.getModuleWidget("JPowerControl")
    widget.unit.ui.btn_software_status.animateClick(0)
    self.delay_test("after_open_software",open_power_control_software_success_func,"can't open software","success open software")

  
  def first_heart_beat(self):
    def first_heart_beat_success_func():
      if "heart_beat" in self.map_info and self.map_info["heart_beat"] != "nan":
        chararray = self.map_info["heart_beat"].split(" ")
        if len(chararray) == 65:
          return True
    widget = util.getModuleWidget("JPowerControl")
    widget.unit.ui.btn_software_status.animateClick(0)
    self.delay_test("after_first_heart_beat",first_heart_beat_success_func,"firat heart beat fail","firat heart beat success")
  
  def after_opened_software_ui(self):
    widget = util.getModuleWidget("JPowerControl")
    self.assertEqual(widget.unit.ui.btn_connect.text == "已连接",True)
    #self.assertEqual(widget.unit.ui.btn_close_software.enabled,False)
    self.assertEqual(widget.unit.ui.btn_write_switch.enabled,False)
    self.assertEqual(widget.unit.ui.btn_software_status.enabled,False)
    
    self.assertEqual(widget.ui.btn_water_power.text == "关闭",True)
    self.assertEqual(widget.ui.btn_ndi_power.text == "关闭",True)
    self.assertEqual(widget.ui.btn_pc_power.text == "关闭",True)
    self.assertEqual(widget.ui.btn_robot_control_1.text == "打开",True)
    self.assertEqual(widget.ui.btn_robot_control_2.text == "打开",True)
    self.assertEqual(widget.ui.btn_robot_control_3.text == "打开",True)
    self.assertEqual(widget.ui.btn_robot_control_4.text == "打开",True)
    self.assertEqual(widget.ui.btn_pa_power.text == "关闭",True)
    self.assertEqual(widget.ui.btn_robot_power.text == "关闭",True)
    self.continue_test()
  
  def close_water_control_device(self):
    btn = util.getModuleWidget("JPowerControl").ui.btn_water_power
    self.assertEqual(btn.text == "关闭",True)
    btn.animateClick(0)
    self._close_one_subdevice_button("close_water_power",btn)
  
  def open_water_control_device(self):
    btn = util.getModuleWidget("JPowerControl").ui.btn_water_power
    self.assertEqual(btn.text == "打开",True)
    btn.animateClick(0)
    self._open_one_subdevice_button("open_water_power",btn)
    
  def close_ndi_control_device(self):
    btn = util.getModuleWidget("JPowerControl").ui.btn_ndi_power
    self.assertEqual(btn.text == "关闭",True)
    btn.animateClick(0)
    self._close_one_subdevice_button("close_ndi_power",btn)
  
  def open_ndi_control_device(self):
    btn = util.getModuleWidget("JPowerControl").ui.btn_ndi_power
    self.assertEqual(btn.text == "打开",True)
    btn.animateClick(0)
    self._open_one_subdevice_button("open_ndi_power",btn)
    
  def close_pc_control_device(self):
    btn = util.getModuleWidget("JPowerControl").ui.btn_pc_power
    self.assertEqual(btn.text == "关闭",True)
    btn.animateClick(0)
    self._close_one_subdevice_button("close_pc_power",btn)
  
  def open_pc_control_device(self):
    btn = util.getModuleWidget("JPowerControl").ui.btn_pc_power
    self.assertEqual(btn.text == "打开",True)
    btn.animateClick(0)
    self._open_one_subdevice_button("open_pc_power",btn)
  
  def close_pa_control_device(self):
    btn = util.getModuleWidget("JPowerControl").ui.btn_pa_power
    self.assertEqual(btn.text == "关闭",True)
    btn.animateClick(0)
    self._close_one_subdevice_button("close_pa_power",btn)
  
  def open_pa_control_device(self):
    btn = util.getModuleWidget("JPowerControl").ui.btn_pa_power
    self.assertEqual(btn.text == "打开",True)
    btn.animateClick(0)
    self._open_one_subdevice_button("open_pa_power",btn)  
    
  def close_robot_control_device(self):
    btn = util.getModuleWidget("JPowerControl").ui.btn_robot_power
    self.assertEqual(btn.text == "关闭",True)
    btn.animateClick(0)
    self._close_one_subdevice_button("close_robot_power",btn)
  
  def open_robot_control_device(self):
    btn = util.getModuleWidget("JPowerControl").ui.btn_robot_power
    self.assertEqual(btn.text == "打开",True)
    btn.animateClick(0)
    self._open_one_subdevice_button("open_robot_power",btn)  
    
  
  def close_r1_device(self):
    btn = util.getModuleWidget("JPowerControl").ui.btn_robot_control_1
    self.assertEqual(btn.text == "关闭",True)
    btn.animateClick(0)
    self._close_one_subdevice_button("close_robot_control_1",btn)
  
  def open_r1_device(self):
    btn = util.getModuleWidget("JPowerControl").ui.btn_robot_control_1
    self.assertEqual(btn.text == "打开",True)
    btn.animateClick(0)
    self._open_one_subdevice_button("open_robot_control_1",btn) 
    
  def close_r2_device(self):
    btn = util.getModuleWidget("JPowerControl").ui.btn_robot_control_2
    self.assertEqual(btn.text == "关闭",True)
    btn.animateClick(0)
    self._close_one_subdevice_button("close_robot_control_2",btn)
  
  def open_r2_device(self):
    btn = util.getModuleWidget("JPowerControl").ui.btn_robot_control_2
    self.assertEqual(btn.text == "打开",True)
    btn.animateClick(0)
    self._open_one_subdevice_button("open_robot_control_2",btn) 
    
  def close_r3_device(self):
    btn = util.getModuleWidget("JPowerControl").ui.btn_robot_control_3
    self.assertEqual(btn.text == "关闭",True)
    btn.animateClick(0)
    self._close_one_subdevice_button("close_robot_control_3",btn)
  
  def open_r3_device(self):
    btn = util.getModuleWidget("JPowerControl").ui.btn_robot_control_3
    self.assertEqual(btn.text == "打开",True)
    btn.animateClick(0)
    self._open_one_subdevice_button("open_robot_control_3",btn) 
    
  def close_r4_device(self):
    btn = util.getModuleWidget("JPowerControl").ui.btn_robot_control_4
    self.assertEqual(btn.text == "关闭",True)
    btn.animateClick(0)
    self._close_one_subdevice_button("close_robot_control_4",btn)
  
  def open_r4_device(self):
    btn = util.getModuleWidget("JPowerControl").ui.btn_robot_control_4
    self.assertEqual(btn.text == "打开",True)
    btn.animateClick(0)
    self._open_one_subdevice_button("open_robot_control_4",btn) 
    
    
    
  def _close_one_subdevice_button(self,key,btn):
    def success_func():
      if btn.text == "打开":
        return True
    self.delay_test(key,success_func,f"close {key} fail","close {key} success") 
  
  def _open_one_subdevice_button(self,key,btn):
    def success_func():
      if btn.text == "关闭":
        return True
    self.delay_test(key,success_func,f"open {key} fail","open {key} success")
    
    
    
  def after_close_software(self):
    def success_func():
      widget = util.getModuleWidget("JPowerControl")
      val1 = widget.unit.ui.btn_write_switch.enabled == True
      val2 = widget.unit.ui.btn_close_software.enabled == False
      val3 = widget.unit.ui.btn_software_status.enabled == True
      val4 = widget.unit.ui.btn_connect.enabled == False
      return val1 and val2 and val3 and val4
    widget = util.getModuleWidget("JPowerControl")
    widget.unit.ui.btn_close_software.animateClick(0)
    self.delay_test("after_close_software",success_func,f"close software fail","close software success")
  
  def after_open_software(self):
    def success_func():
      widget = util.getModuleWidget("JPowerControl")
      val1 = widget.unit.ui.btn_write_switch.enabled == False
      val2 = widget.unit.ui.btn_close_software.enabled == True
      val3 = widget.unit.ui.btn_software_status.enabled == False
      val4 = widget.unit.ui.btn_connect.enabled == False
      return val1 and val2 and val3 and val4
    widget = util.getModuleWidget("JPowerControl")
    widget.unit.ui.btn_software_status.animateClick(0)
    self.delay_test("after_open_software",success_func,f"open software fail","open software success")
    
    
  def set_fan_80(self):
    def success_func():
      stringlist = self.map_info["heart_beat"]
      chararray = stringlist.split(" ")
      fan_speed_h = chararray[13]
      fan_speed_l = chararray[14]
      fan_speed = int(fan_speed_h, 16)*255 + int(fan_speed_l, 16)
      if fan_speed > 190 and fan_speed < 210:
        return True
    widget = util.getModuleWidget("JPowerControl")
    widget.ui.le_fan.setText(80)
    widget.ui.btn_setting_fan.animateClick(0)
    self.delay_test("set_fan_80",success_func,f"set_fan_80 fail","set_fan_80 success")
  
  def set_fan_30(self):
    def success_func():
      stringlist = self.map_info["heart_beat"]
      chararray = stringlist.split(" ")
      fan_speed_h = chararray[13]
      fan_speed_l = chararray[14]
      fan_speed = int(fan_speed_h, 16)*255 + int(fan_speed_l, 16)
      if fan_speed > 80 and fan_speed < 90:
        return True
    widget = util.getModuleWidget("JPowerControl")
    widget.ui.le_fan.setText(30)
    widget.ui.btn_setting_fan.animateClick(0)
    self.delay_test("set_fan_30",success_func,f"set_fan_30 fail","set_fan_30 success")
    
  ''' 
  ===========================================================================================================================
    测试结束
  ===========================================================================================================================
  '''
  def finished(self):
    self.continue_test()