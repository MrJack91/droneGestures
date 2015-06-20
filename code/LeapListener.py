# https://developer.leapmotion.com/documentation/python/devguide/Sample_Tutorial.html
# https://developer.leapmotion.com/documentation/python/devguide/Leap_Frames.html


import os
import sys
import inspect
import thread
import time

'''
# import for all kind of devices (win, osx, linux)
src_dir = os.path.dirname(inspect.getfile(inspect.currentframe()))
arch_dir = 'lib/x64' if sys.maxsize > 2**32 else 'lib/x86'
sys.path.insert(0, os.path.abspath(os.path.join(src_dir, arch_dir)))
'''

# lib only for os x
src_dir = os.path.dirname(inspect.getfile(inspect.currentframe()))
lib_dir = os.path.abspath(os.path.join(src_dir, 'lib/leap'))
sys.path.insert(0, lib_dir)

import Leap
import StateHandler
from StateHandler import StateInitHandler

class LeapListener(Leap.Listener):

    # states (static)
    STATE_0_OFF = 0
    STATE_RESET = -1
    STATE_1_INIT = 1
    STATE_2_FLIGHTREADY = 2
    STATE_3_FLIGHT = 3
    STATE_4_UNCONTROLLED = 4

    def __init__(self):
        super(LeapListener, self).__init__()

        self.STATE_NAME = {
            -1: 'STATE_RESET',
            0: 'STATE_0_OFF',
            1: 'STATE_1_INIT',
            2: 'STATE_2_FLIGHTREADY',
            3: 'STATE_3_FLIGHT',
            4: 'STATE_4_UNCONTROLLED',
        }

        self.MAX_THRUST = 40000                     # max possible 60000

        # runtime params
        self.current_state = self.STATE_0_OFF
        self.last_state = self.current_state
        self.relative_no_power = 0
        self.relative_no_power_security = 20        # additional space for no powering (2cm)

        self.timeref = None

        self.STATE_RESET_has_fist = False
        self.STATE_RESET_has_open_hand = False

        self.state_1_init = StateHandler.StateInitHandler.StateInitHandler(self.STATE_1_INIT)


    def set_cfc(self, cfc):
        self.cfc = cfc

    def on_init(self, controller):
        print "LeapListener: init"

    def on_connect(self, controller):
        print "LeapListener: connected"
        #controller.enable_gesture(Leap.Gesture.TYPE_SWIPE)

    def on_disconnect(self, controller):
        # Note: not dispatched when running in a debugger.
        print "LeapListener: disconnected"

    def on_exit(self, controller):
        print "LeapListener: shut down"

    def on_frame(self, controller):

        # first frame activate init state
        if self.current_state == self.STATE_0_OFF:
            self.current_state = self.STATE_RESET

        # log state change
        if self.current_state != self.last_state:
            print "STATE: " + self.STATE_NAME[self.last_state] + " => " + self.STATE_NAME[self.current_state]
            self.last_state = self.current_state

        frame = controller.frame()

        '''
        print "Frame id: %d, timestamp: %d, hands: %d, fingers: %d, tools: %d, gestures: %d" % (
          frame.id, frame.timestamp, len(frame.hands), len(frame.fingers), len(frame.tools), len(frame.gestures())
        )
        '''

        if len(frame.hands) == 1:
            for hand in frame.hands:

                # handle very state
                if self.current_state == self.STATE_RESET:
                    # state reset -> open hand and fist must be recognised (to avoid mistakenly next init)
                    if hand.grab_strength == 1 and self.STATE_RESET_has_fist is False:
                        self.STATE_RESET_has_fist = True
                        print 'RESET: found fist'
                    elif hand.grab_strength == 0 and self.STATE_RESET_has_open_hand is False:
                        self.STATE_RESET_has_open_hand = True
                        print 'RESET: found open hand'

                    # set init if both hand are traced
                    if self.STATE_RESET_has_fist and self.STATE_RESET_has_open_hand:
                        self.reset_init()

                elif self.current_state == self.STATE_1_INIT:

                    #self.state_1_init.handleState(hand)
                    #test = StateHandler.StateInitHandler.StateInitHandler(self.STATE_1_INIT)
                    self.current_state = self.state_1_init.handleState(hand)

                    '''
                    # STATE 1: init drone control
                    if hand.grab_strength == 1 and self.timeref is None:
                        # found fist

                        # remember time -> fist must be hold for 2 seconds
                        self.timeref = time.time()
                        print 'fist dedected! hold it for 2s...'

                    elif hand.grab_strength == 1 and self.timeref is not None:
                        # fist must be holded for minimum 2 s
                        if time.time() - self.timeref > 2:
                            print 'fist is valid! drone will fly, if you open your hand...'
                            self.current_state = self.STATE_2_FLIGHTREADY
                            self.timeref = None

                    elif hand.grab_strength == 0 and self.timeref is not None:
                        # fist was losed before 2s -> restart init process
                        self.reset_control()
                    '''

                elif self.current_state == self.STATE_2_FLIGHTREADY:
                    # STATE 2: flightready
                    if hand.grab_strength == 0:
                        # find open hand on allowed height

                        if hand.palm_position.y > 100 and hand.palm_position.y < 350:
                            self.current_state = self.STATE_3_FLIGHT
                            print 'hand position initialized! drone control is activated.'
                            self.relative_no_power = hand.palm_position.y + self.relative_no_power_security
                        else:
                            # change state to init -> renew fist gesture
                            self.current_state = self.STATE_1_INIT
                            print "your hand position is to low. " \
                                  "use space between 100 and 350 mm over the leap motion sensor. " \
                                  "do fist again."

                elif self.current_state == self.STATE_3_FLIGHT:
                    # STATE 3: flight mode
                    if hand.grab_strength == 1:
                        # stop flight without delay
                        if self.check_cf():
                            self.cfc.cf.commander.send_setpoint(0, 0, 0, 0)
                            time.sleep(0.1)

                        self.current_state = self.STATE_RESET

                    else:
                        # flight control

                        # Get the hand's normal vector and direction
                        normal = hand.palm_normal
                        direction = hand.direction

                        # set flight command values
                        thrust = ((hand.palm_position.y - self.relative_no_power) * 50000 / 200) + 10000 # 50000 max thrust over 200 mm
                        if thrust > self.MAX_THRUST:
                            thrust = self.MAX_THRUST
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

                elif self.current_state == self.STATE_4_UNCONTROLLED:
                    # STATE 4: uncontrolled flight (hand was losed)
                    pass

        elif len(frame.hands) > 1:
            print 'More than one hand detected! Pls, only use one hand.'

        else:
            # no hands -> reset if not flight
            self.reset_control()

    def reset_control(self):
        self.timeref = None
        self.current_state = self.STATE_RESET

    def reset_init(self):
        self.current_state = self.STATE_1_INIT
        # reset variables
        self.STATE_RESET_has_fist = False
        self.STATE_RESET_has_open_hand = False

    def check_cf(self):
        """ check if the crazyflie properly connected
        :return: if true: access can get via self.cfc.cf
        """
        if self.cfc.cf is not None:
            return True
        else:
            return False
