import slicer.util as util


class DeviceStatusMonitor:
    CONNECTED = 1
    DISCONNECTED = -1
    RECONNECT_THRESHOLD = -11

    def __init__(self) -> None:
        self.connect_info = {}
        self.old_state = [0, 0, 0, 0, 0]
        self.check_list = ["Power", "UltraImage", "UltrasoundGenerator", "UR", "WaterControl"]

    def enter(self):
        self.connect_info = {}

    def get_connect_status(self, key, map_info):
        if key not in self.connect_info:
            self.connect_info[key] = self.DISCONNECTED
        if key == "UR" and map_info.get("connect_status", self.DISCONNECTED) == "3":
            self._update_connection_status(key)
        elif key in ["UltrasoundGenerator", "Power", "WaterControl"] and map_info.get("heart_beat",
                                                                                      self.DISCONNECTED) != self.DISCONNECTED:
            self._update_connection_status(key)
        else:
            self._decrease_connection_status(key)

    def _update_connection_status(self, key):
        if self.connect_info[key] < 0:
            util.send_event_str(util.ChangeToConnectState, key)
            if key == "WaterControl":
                util.getModuleWidget("JWaterControl").open_24V_power()
        self.connect_info[key] = self.CONNECTED
        util.hardware_state[key] = self.connect_info[key]

    def _decrease_connection_status(self, key):
        if self.connect_info[key] == self.CONNECTED:
            util.send_event_str(util.ChangeToDisConnectState, key)
            self.connect_info[key] = 0
        self.connect_info[key] -= 1
        util.hardware_state[key] = self.connect_info[key]

    def update_ui(self):
        new_state = [0, 0, 0, 0, 0]
        for i, key in enumerate(self.check_list):
            new_state[i] = 1 if self.connect_info.get(key) == self.CONNECTED else 0
        new_state[0] = 1
        new_state[1] = 1

        if new_state != self.old_state:
            util.getModuleWidget("UltrasoundBoot").set_check_state(new_state)
            self.old_state = new_state

    def always_reconnect(self):
        # print(self.connect_info)
        # print(util.map_info["heart_beat"])
        for key in self.connect_info:
            # print("key is " + key)
            if self.connect_info[key] < self.RECONNECT_THRESHOLD:
                util.send_event_str(util.ReconnectEvent, key)
                self.connect_info[key] = -1

    def all_connected(self):
        return all(self.connect_info.get(key) == self.CONNECTED for key in self.check_list)
