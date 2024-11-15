import slicer.util as util
from RDNTool.RDNFSMLib.DeviceStatusMonitor import DeviceStatusMonitor


class StateSub:
    monitor = None

    def __init__(self) -> None:
        self.name = util.FSM_CHECK_DEVICE_STATE
        self.monitor = DeviceStatusMonitor()

    def enter(self):
        print(f"enter state ==> {self.name}")
        util.getModuleWidget("RequestStatus").send_cmd(f"Power, SetGapMax, 5")
        util.getModuleWidget("RequestStatus").send_cmd(f"UltrasoundGenerator, SetGapMax, 6")
        # util.getModuleWidget("RequestStatus").send_cmd(f"Device, SetGapMax, 7")
        util.getModuleWidget("RequestStatus").send_cmd(f"WaterControl, SetGapMax, 8")
        # util.getModuleWidget("RequestStatus").send_cmd(f"System, SetGapMax, 9")
        util.getModuleWidget("RequestStatus").send_cmd(f"UR, SetGapMax, 11")
        # util.getModuleWidget("JIMEConnector").connect_IME()
        # util.getModuleWidget("JURRobotArm").on_robot_arm_connect()
        util.send_event_str(util.ReconnectEvent, "Power")
        util.send_event_str(util.ReconnectEvent, "UR")
        util.send_event_str(util.ReconnectEvent, "UltrasoundGenerator")
        util.send_event_str(util.ReconnectEvent, "WaterControl")
        self.monitor.enter()

    def exit(self):
        print(f"leave state ==> {self.name}")

    def tickEvent(self, key, map_info):
        self.monitor.get_connect_status(key, map_info)
        self.monitor.always_reconnect()
        self.monitor.update_ui()
        ### check if needed to reconnect 

        if self.monitor.all_connected():
            util.send_fsm_event("successed_finished_check_device")
