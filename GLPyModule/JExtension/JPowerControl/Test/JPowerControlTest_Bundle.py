def init_bundle(self):
  bundle = {}
  bundle["name"] = "bundle_init_to_open_software"
  bundle["data"] = [
    ["reset_page",    self.reset_page],
    ["open_control_panel",    self.open_control_panel],
    ["start_bundle_1",    self.start_bundle_1],
    ["check_init_connect_status",    self.check_init_connect_status],
    ["add_tick_event_listener",    self.add_tick_event_listener],
    ["connect_power_device",    self.connect_power_device],
    ["open_power_control_software",    self.open_power_control_software],
    ["first_heart_beat",self.first_heart_beat],
    ["after_opened_software_ui",self.after_opened_software_ui],
    ["finished",self.finished]
  ]
  self.bundle_map[bundle["name"]]=bundle
  
  bundle = {}
  bundle["name"] = "open_close_sub_device_butotn"
  bundle["data"] = [
    ["close_water_control_device",    self.close_water_control_device],
    ["open_water_control_device",self.open_water_control_device],
    ["close_ndi_control_device",    self.close_ndi_control_device],
    ["open_ndi_control_device",self.open_ndi_control_device],
    ["close_pc_control_device",    self.close_pc_control_device],
    ["open_pc_control_device",self.open_pc_control_device],
    ["close_pa_control_device",self.close_pa_control_device],
    ["open_pa_control_device",self.open_pa_control_device],
    ["close_robot_control_device",self.close_robot_control_device],
    ["open_robot_control_device",self.open_robot_control_device],
    ["open_r1_device",self.open_r1_device],
    ["close_r1_device",self.close_r1_device],
    ["open_r2_device",self.open_r2_device],
    ["close_r2_device",self.close_r2_device],
    ["open_r3_device",self.open_r3_device],
    ["close_r3_device",self.close_r3_device],
    ["open_r4_device",self.open_r4_device],
    ["close_r4_device",self.close_r4_device],
    ["finished",    self.finished]      
  ]
  self.bundle_map[bundle["name"]]=bundle
  
  bundle = {}
  bundle["name"] = "close_and_open_software_bundle"
  bundle["data"] = [
    ["after_close_software",    self.after_close_software],
    ["after_open_software",    self.after_open_software],
    ["after_close_software",    self.after_close_software],
    ["after_open_software",    self.after_open_software],
    ["finished",self.finished]
  ]
  self.bundle_map[bundle["name"]]=bundle
  
  bundle = {}
  bundle["name"] = "test_fan"
  bundle["data"] = [
    ["set_fan_80",    self.set_fan_80],
    ["set_fan_30", self.set_fan_30],
    ["finished",self.finished]
  ]
  self.bundle_map[bundle["name"]]=bundle
  
  
  
  
  
 
   