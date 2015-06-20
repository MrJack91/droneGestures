import time
import Leap

from BaseStateHandler import BaseStateHandler
from Piloting import PilotingStates

class State3FlightHandler(BaseStateHandler):
    
    def __init__(self, piloting_configuration, cfc, current_state):
        super(State3FlightHandler, self).__init__(piloting_configuration, cfc, current_state)
    
    def handle(self, hand):
        super(State3FlightHandler, self).handle(hand)

        # STATE 3: flight mode
        if self.hand.grab_strength == 1:
            # stop flight without delay
            if self.check_cf():
                self.cfc.cf.commander.send_setpoint(0, 0, 0, 0)
                time.sleep(0.1)

            self.next_state = PilotingStates.PilotingStates.STATE___RESET

        else:
            # flight control

            # Get the hand's normal vector and direction
            normal = self.hand.palm_normal
            direction = self.hand.direction

            # set flight command values
            thrust = ((self.hand.palm_position.y - self.piloting_configuration.relative_no_power) * 50000 / 200) + 10000 # 50000 max thrust over 200 mm
            if thrust > self.piloting_configuration.MAX_THRUST:
                thrust = self.piloting_configuration.MAX_THRUST
            elif thrust < 10000:
                thrust = 0

            pitch = -1 * direction.pitch * Leap.RAD_TO_DEG
            roll = -1 * normal.roll * Leap.RAD_TO_DEG
            yaw = direction.yaw * Leap.RAD_TO_DEG

            '''
            print " COMMAND thrust: %f, pitch: %f, roll: %f, yaw: %f" % (
                thrust,
                pitch,
                roll,
                yaw)
            '''

            if self.check_cf():
                self.cfc.cf.commander.send_setpoint(roll, pitch, yaw, thrust)

        return self.next_state