import slicer.util as util


class RDNFSM:
    old_state = None
    state = None
    state_map = {}

    def __init__(self):
        print("RDN FSM Init")
        # origin state
        self.state_map = {}
        from RDNTool.RDNFSMLib import FSM_CHECK_DEVICE_STATE
        self.state_map[util.FSM_CHECK_DEVICE_STATE] = FSM_CHECK_DEVICE_STATE.StateSub()
        from RDNTool.RDNFSMLib import FSM_END_STATE
        self.state_map[util.FSM_END_STATE] = FSM_END_STATE.StateSub()
        from RDNTool.RDNFSMLib import FSM_HAND_EYE_CALIBRATION_STATE
        self.state_map[util.FSM_HAND_EYE_CALIBRATION_STATE] = FSM_HAND_EYE_CALIBRATION_STATE.StateSub()
        from RDNTool.RDNFSMLib import FSM_INITIAL_STATE
        self.state_map[util.FSM_INITIAL_STATE] = FSM_INITIAL_STATE.StateSub()
        from RDNTool.RDNFSMLib import FSM_READY_STATE
        self.state_map[util.FSM_READY_STATE] = FSM_READY_STATE.StateSub()
        from RDNTool.RDNFSMLib import FSM_TREATMENT_STATE
        self.state_map[util.FSM_TREATMENT_STATE] = FSM_TREATMENT_STATE.StateSub()
        self.send_event("init_state")

    def send_event(self, event):
        print("send fsm event:", event)
        if event == 'start_hand_eye_calib':
            self.set_state(util.FSM_HAND_EYE_CALIBRATION_STATE)
        elif event == 'end_hand_eye_calib':
            self.set_state(util.FSM_READY_STATE)
        elif event == 'robot_disconnected':
            if self.state == util.FSM_HAND_EYE_CALIBRATION_STATE:
                self.set_state(util.FSM_READY_STATE)
        elif event == "finished_initial_state":
            self.set_state(util.FSM_CHECK_DEVICE_STATE)
        elif event == "successed_finished_check_device":
            self.set_state(util.FSM_READY_STATE)
        elif event == "init_state":
            self.set_state(util.FSM_INITIAL_STATE)
        elif event == "treat_state":
            self.set_state(util.FSM_TREATMENT_STATE)

    def set_state(self, state):
        tmp = self.state
        self.state = state
        self.old_state = tmp
        if self.old_state:
            self.state_map[self.old_state].exit()
        if self.state:
            self.state_map[self.state].enter()
        util.send_event_str(util.ChangeFSMState, self.state)

    def run(self):
        while self.state != util.FSM_END_STATE:
            getattr(self, self.state.lower())()

    def tickEvent(self, key, map_info):
        # print(f"fsm state {self.state}")
        self.state_map[self.state].tickEvent(key, map_info)
