from BaseStateHandler import BaseStateHandler
import LeapListener

import time

class StateInitHandler(BaseStateHandler):
    
    def __init__(self, current_state):
        super(StateInitHandler, self).__init__(current_state)
        self.timeref = None
    
    def handleState(self, hand):
        super(StateInitHandler, self).handleState(hand)

        # STATE 1: init drone control
        if self.hand.grab_strength == 1 and self.timeref is None:
            # found fist

            # remember time -> fist must be hold for 2 seconds
            self.timeref = time.time()
            print 'fist dedected! hold it for 2s...'

        elif self.hand.grab_strength == 1 and self.timeref is not None:
            # fist must be holded for minimum 2 s
            if time.time() - self.timeref > 2:
                print 'fist is valid! drone will fly, if you open your hand...'
                self.next_state = LeapListener.LeapListener.STATE_2_FLIGHTREADY
                self.timeref = None

        elif self.hand.grab_strength == 0 and self.timeref is not None:
            # fist was losed before 2s -> restart init process
            # todo fix this not accessable via statehandler
            self.reset_control()

        return self.next_state