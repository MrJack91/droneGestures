import time

from BaseStateHandler import BaseStateHandler
from Piloting import PilotingStates

class State1InitHandler(BaseStateHandler):
    
    def __init__(self, piloting_configuration, cfc, current_state):
        super(State1InitHandler, self).__init__(piloting_configuration, cfc, current_state)
        self.time_ref = None
    
    def handle(self, hand):
        super(State1InitHandler, self).handle(hand)

        # STATE 1: init drone control
        if self.hand.grab_strength == 1 and self.time_ref is None:
            # found fist

            # remember time -> fist must be hold for 2 seconds
            self.time_ref = time.time()
            print 'Fist dedected! Hold it for 2s...'

        elif self.hand.grab_strength == 1 and self.time_ref is not None:
            # fist must be holded for minimum 2 s
            if time.time() - self.time_ref > 2:
                print 'Fist is valid! Drone will fly, if you open your hand...'
                self.next_state = PilotingStates.PilotingStates.STATE_2_FLIGHTREADY
                self.time_ref = None

        elif self.hand.grab_strength == 0 and self.time_ref is not None:
            # fist was losed before 2s -> restart init process
            # todo fix this not accessable via statehandler
            self.reset_control()

        return self.next_state

    def reset_control(self):
        """
        Reset all. Restart the controll initialization process
        :return:
        """
        # stop flight without delay
        if self.check_cf():
            self.cfc.cf.commander.send_setpoint(0, 0, 0, 0)
            time.sleep(0.1)
        self.time_ref = None
        self.next_state = PilotingStates.PilotingStates.STATE___RESET
