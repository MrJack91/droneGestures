from BaseStateHandler import BaseStateHandler
from Piloting import PilotingStates

class State2FlightreadyHandler(BaseStateHandler):
    
    def __init__(self, piloting_configuration, cfc, current_state):
        super(State2FlightreadyHandler, self).__init__(piloting_configuration, cfc, current_state)
    
    def handle(self, hand):
        super(State2FlightreadyHandler, self).handle(hand)

        if self.hand.grab_strength == 0:
            # find open hand on allowed height

            if self.hand.palm_position.y > 100 and self.hand.palm_position.y < 350:
                self.next_state = PilotingStates.PilotingStates.STATE_3_FLIGHT
                print "Hand position initialized! drone control is activated. (null-ref: " + str(self.hand.palm_position.y) + " mm)"
                self.piloting_configuration.relative_no_power = self.hand.palm_position.y + self.piloting_configuration.relative_no_power_security
            else:
                # change state to init -> renew fist gesture
                self.next_state = PilotingStates.PilotingStates.STATE___RESET
                print "Your hand position (" + str(self.hand.palm_position.y) + " mm) is on an invalid position. " \
                      "Use space between 100 and 350 mm over the leap motion sensor."

        return self.next_state