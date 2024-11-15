import slicer.util as util
class StateSub:
    def __init__(self) -> None:
        self.name = util.FSM_END_STATE
    
    def enter(self):
        print(f"enter state ==> {self.name}")
    
    def exit(self):
        print(f"leave state ==> {self.name}")
    
    def tickEvent(self,key,map_info):
        pass