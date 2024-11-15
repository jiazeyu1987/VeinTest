import slicer.util as util
class StateSub:
    def __init__(self) -> None:
        self.name = util.FSM_HAND_EYE_CALIBRATION_STATE
    
    def enter(self):
        print(f"enter state ==> {self.name}")
        util.getModuleWidget("RequestStatus").send_cmd(f"IME, SetGapMax, 10")
        util.getModuleWidget("RequestStatus").send_cmd(f"UR, SetGapMax, 10")
    
    def exit(self):
        print(f"leave state ==> {self.name}")
    
    def tickEvent(self,key,map_info):
        pass