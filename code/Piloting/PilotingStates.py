class PilotingStates:

    # states (static)
    STATE_0_OFF = 0
    STATE_1_INIT = 1
    STATE_2_FLIGHTREADY = 2
    STATE_3_FLIGHT = 3
    STATE_4_UNCONTROLLED = 4
    STATE___RESET = -1

    STATE_NAME = {
        -1: 'STATE___RESET',
        0: 'STATE_0_OFF',
        1: 'STATE_1_INIT',
        2: 'STATE_2_FLIGHTREADY',
        3: 'STATE_3_FLIGHT',
        4: 'STATE_4_UNCONTROLLED',
    }

    def __init__(self):
        pass
