def init_bundle(self):
  bundle = {}
  bundle["name"] = "bundle_init_to_open_software"
  bundle["data"] = [
    ["reset_page",    self.reset_page],
    ["open_control_panel",    self.open_control_panel],
    ["start_bundle_1",    self.start_bundle_1],
    ["check_init_connect_status",    self.check_init_connect_status],
    ["add_tick_event_listener",    self.add_tick_event_listener],
    ["after_connect",    self.after_connect],
    ["open_ultrasound_control_software",    self.open_ultrasound_control_software],
    ["first_heart_beat",self.first_heart_beat],
    ["after_opened_software_ui",self.after_opened_software_ui],
    ["after_close_software",self.after_close_software],
    ["after_open_software",self.after_open_software],
    ["after_set_30_power_software",self.after_set_30_power_software],
    ["close_pa",self.close_pa],
    ["after_set_60_power_software",self.after_set_60_power_software],
    ["close_pa",self.close_pa],
    ["after_set_30_power_software",self.after_set_30_power_software],
    ["close_pa",self.close_pa],
    ["after_set_60_power_software",self.after_set_60_power_software],
    ["finished",self.finished]
  ]
  self.bundle_map[bundle["name"]]=bundle
  