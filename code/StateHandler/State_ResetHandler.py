
from BaseStateHandler import BaseStateHandler
from Piloting import PilotingStates

class State_ResetHandler(BaseStateHandler):
    
    def __init__(self, piloting_configuration, cfc, current_state):
        super(State_ResetHandler, self).__init__(piloting_configuration, cfc, current_state)
        self.has_fist = False
        self.has_open_hand = False

    def handle(self, hand):
        super(State_ResetHandler, self).handle(hand)

        # state reset -> open hand and fist must be recognised (to avoid mistakenly next init)
        if self.hand.grab_strength == 1 and self.has_fist is False:
            self.has_fist = True
            print 'RESET: found fist'
        elif self.hand.grab_strength == 0 and self.has_open_hand is False:
            self.has_open_hand = True
            print 'RESET: found open hand'

        # set init if both hand are traced
        if self.has_fist and self.has_open_hand:
            self.next_state = PilotingStates.PilotingStates.STATE_1_INIT
            # reset variables
            self.has_fist = False
            self.has_open_hand = False

        return self.next_state
