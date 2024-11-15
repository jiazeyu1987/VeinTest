import slicer.util as util


class StateSub:
    connect_info = {}
    reconnect_info = {}
    check_list = ["IME", "UR"]
    reconnect_threshold = -20
    reconnect_max_count = 3

    def __init__(self) -> None:
        self.name = util.FSM_READY_STATE

    def enter(self):
        print(f"enter state ==> {self.name}")
        return
        # util.getModuleWidget("RequestStatus").send_cmd(f"IME, SetGapMax, 120")
        # util.getModuleWidget("RequestStatus").send_cmd(f"UR, SetGapMax, 100")
        # util.getModuleWidget("RequestStatus").send_cmd(f"Device, SetGapMax, 80")
        # self.connect_info = {}

    def exit(self):
        print(f"leave state ==> {self.name}")

    def tickEvent(self, key, map_info):
        if key not in self.connect_info:
            self.connect_info[key] = 0
            self.reconnect_info[key] = 0

        if key not in ["UR"] and "connect_status" in map_info and map_info["connect_status"] == "1":
            self.connect_info[key] = 1
            self.reconnect_info[key] = 0
        elif key in ["UR"] and "connect_status" in map_info and int(map_info["connect_status"]) == 3:
            self.connect_info[key] = 1
            self.reconnect_info[key] = 0
        else:
            self.connect_info[key] -= 1

        for key in self.check_list:
            if key in self.connect_info and self.connect_info[key] < self.reconnect_threshold:
                util.send_event_str(util.ReconnectEvent, key)
                self.reconnect_info[key] -= 1
                if self.reconnect_info[key] < - self.reconnect_max_count:
                    util.showWarningText(f"the {key} can't connect ,please check device and restart")
                    print("Shut the system down")
                    util.getModuleWidget("RequestStatus").shutdown()
                self.connect_info[key] = -1

        for key in self.check_list:
            if key in self.connect_info and self.connect_info[key] == 1:
                pass
            else:
                return
