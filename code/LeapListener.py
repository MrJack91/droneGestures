# https://developer.leapmotion.com/documentation/python/devguide/Sample_Tutorial.html
# https://developer.leapmotion.com/documentation/python/devguide/Leap_Frames.html


import os, sys, inspect, thread, time

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

class LeapListener(Leap.Listener):

    # all this follow params are used for all instances (they are shared)

    # global vars
    STATE_0_OFF = 0
    STATE_1_INIT = 1
    STATE_2_FLIGHTREADY = 2
    STATE_3_FLIGHT = 3
    STATE_4_UNCONTROLLED = 4

    MAX_THRUST = 40000      # max possible 60000

    # runtime params
    current_state = STATE_0_OFF
    relative_no_power = 0
    relative_no_power_security = 20     # additional space for no powering (2cm)

    # reference to crazyflie (for commands)
    cf = None

    def on_init(self, controller):
        print "Initialized"

    def on_connect(self, controller):
        print "Connected"
        #controller.enable_gesture(Leap.Gesture.TYPE_SWIPE)

    def on_disconnect(self, controller):
        # Note: not dispatched when running in a debugger.
        print "Disconnected"

    def on_exit(self, controller):
        print "Exited"

    def on_frame(self, controller):
        # global current_state, relative_no_power, relative_no_power_security,\
        #        STATE_1_INIT, STATE_2_FLIGHTREADY, STATE_3_FLIGHT, STATE_4_UNCONTROLLED, MAX_THRUST

        # first frame activate init state
        if self.current_state == self.STATE_0_OFF:
            self.current_state = self.STATE_1_INIT

        # print "Frame available"
        frame = controller.frame()

        '''
        print "Frame id: %d, timestamp: %d, hands: %d, fingers: %d, tools: %d, gestures: %d" % (
          frame.id, frame.timestamp, len(frame.hands), len(frame.fingers), len(frame.tools), len(frame.gestures())
        )
        '''

        if len(frame.hands) == 1:
            for hand in frame.hands:

                if hand.grab_strength == 1 and self.current_state == self.STATE_1_INIT:
                    # find fist

                    self.current_state = self.STATE_2_FLIGHTREADY
                    print 'fist dedected! drone will fly, if you open your hand...'

                elif hand.grab_strength == 0 and self.current_state == self.STATE_2_FLIGHTREADY:
                    # find open hand on allowed height

                    if hand.palm_position.y > 100 or hand.palm_position.y < 350:
                        # connect to crazyflie
                        link_uri = 'radio://0/80/250K'
                        self.cf._cf.open_link(link_uri)

                        self.current_state = self.STATE_3_FLIGHT
                        print 'hand position initialized! drone control is activated'
                        self.relative_no_power = hand.palm_position.y + self.relative_no_power_security
                    else:
                        print "your hand position is to low. use space between 100 and 350 mm over the leap motion sensor"

                elif self.current_state == self.STATE_3_FLIGHT and hand.grab_strength == 1:
                    # stop flight mode, disconnect drone and change to init
                    time.sleep(0.1)
                    self.cf._cf.close_link()

                    self.current_state = self.STATE_1_INIT

                    # for testing, be sure drone is shut down
                    #exit()

                elif self.current_state == self.STATE_3_FLIGHT:
                    # flight control

                    # Get the hand's normal vector and direction
                    normal = hand.palm_normal
                    direction = hand.direction

                    # set flight command values
                    thrust = ((hand.palm_position.y - relative_no_power) * 50000 / 200) + 10000 # 50000 max thrust over 200 mm
                    if thrust > self.MAX_THRUST:
                        thrust = self.MAX_THRUST
                    elif thrust < 10000:
                        thrust = 0

                    pitch = -1 * direction.pitch * Leap.RAD_TO_DEG
                    roll = -1 * normal.roll * Leap.RAD_TO_DEG
                    yaw = direction.yaw * Leap.RAD_TO_DEG

                    print " COMMAND thrust: %f, pitch: %f, roll: %f, yaw: %f" % (
                        thrust,
                        pitch,
                        roll,
                        yaw)

                    self.cf._cf.commander.send_setpoint(roll, pitch, yaw, thrust)

        elif len(frame.hands) > 1:
            print 'More than one hand detected! Pls, only use one hand.'
