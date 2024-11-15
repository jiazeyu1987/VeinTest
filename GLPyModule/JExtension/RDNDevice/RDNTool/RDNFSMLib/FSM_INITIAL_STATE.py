import slicer.util as util
class StateSub:
    def __init__(self) -> None:
        self.name = util.FSM_INITIAL_STATE
    
    def enter(self):
        print(f"enter state ==> {self.name}")
        util.singleShot(3000,self.send_event)
        
    def send_event(self):
        util.send_fsm_event("finished_initial_state")
    
    def exit(self):
        print(f"leave state ==> {self.name}")
    
    def tickEvent(self,key,map_info):
        pass