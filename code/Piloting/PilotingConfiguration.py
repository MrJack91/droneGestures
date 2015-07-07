
import PilotingStates
from StateHandler import State_ResetHandler, State1InitHandler, State2FlightreadyHandler, State3FlightHandler

class PilotingConfiguration():
    """
    Contains information to current piloting configuration (controll settings)
    """

    def __init__(self, cfc):
        self.MAX_THRUST = 60000                     # max possible 60000

        # runtime params
        self.relative_no_power = 0
        self.relative_no_power_security = 20        # additional space for no powering (2cm)

        #: :type dict of (StateHandler.BaseStateHandler)
        self.state_handler = {
            PilotingStates.PilotingStates.STATE___RESET:         State_ResetHandler.State_ResetHandler(self, cfc, PilotingStates.PilotingStates.STATE___RESET),
            PilotingStates.PilotingStates.STATE_1_INIT:          State1InitHandler.State1InitHandler(self, cfc, PilotingStates.PilotingStates.STATE_1_INIT),
            PilotingStates.PilotingStates.STATE_2_FLIGHTREADY:   State2FlightreadyHandler.State2FlightreadyHandler(self, cfc, PilotingStates.PilotingStates.STATE_2_FLIGHTREADY),
            PilotingStates.PilotingStates.STATE_3_FLIGHT:        State3FlightHandler.State3FlightHandler(self, cfc, PilotingStates.PilotingStates.STATE_3_FLIGHT)
        }
        # self.state_handler[PilotingStates.PilotingStates.STATE_1_INIT].
