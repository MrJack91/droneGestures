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

# global vars
STATE_0_OFF = 0
STATE_1_INIT = 1
STATE_2_FLIGHTREADY = 2
STATE_3_FLIGHT = 3
STATE_4_UNCONTROLLED = 4

# runtime params
current_state = STATE_0_OFF
relative_no_power = 0
relative_no_power_security = 20     # additional space for no powering (2cm)

class SampleListener(Leap.Listener):

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

        global current_state, relative_no_power, relative_no_power_security,\
                STATE_1_INIT, STATE_2_FLIGHTREADY, STATE_3_FLIGHT, STATE_4_UNCONTROLLED


        # first frame activate init state
        if current_state == STATE_0_OFF:
            current_state = STATE_1_INIT

        # print "Frame available"
        frame = controller.frame()

        '''
        print "Frame id: %d, timestamp: %d, hands: %d, fingers: %d, tools: %d, gestures: %d" % (
          frame.id, frame.timestamp, len(frame.hands), len(frame.fingers), len(frame.tools), len(frame.gestures())
        )
        '''

        if len(frame.hands) == 1:
            for hand in frame.hands:

                if hand.grab_strength == 1 and current_state == STATE_1_INIT:
                    # find fist

                    current_state = STATE_2_FLIGHTREADY
                    print 'fist dedected! drone will fly, if you open your hand...'

                elif hand.grab_strength == 0 and current_state == STATE_2_FLIGHTREADY:
                    # find open hand on allowed height

                    if hand.palm_position.y > 100 or hand.palm_position.y < 350:
                        current_state = STATE_3_FLIGHT
                        print 'hand position initialized! drone control is activated'
                        relative_no_power = hand.palm_position.y + relative_no_power_security

                elif current_state == STATE_3_FLIGHT and hand.grab_strength == 1:
                    # stop flight mode and change to init

                    current_state = STATE_1_INIT

                elif current_state == STATE_3_FLIGHT:
                    # flight control

                    # Get the hand's normal vector and direction
                    normal = hand.palm_normal
                    direction = hand.direction

                    # print hand.palm_position    # (-273.733, 205.244, -56.3546) | x, y, z



                    '''
                    # Calculate the hand's pitch, roll, and yaw angles
                    print "  pitch: %f degrees, roll: %f degrees, yaw: %f degrees" % (
                        direction.pitch * Leap.RAD_TO_DEG,
                        normal.roll * Leap.RAD_TO_DEG,
                        direction.yaw * Leap.RAD_TO_DEG)
                    '''

                    # set flight command values
                    thrust = ((hand.palm_position.y - relative_no_power) * 50000 / 200) + 10000 # 50000 max thrust over 200 mm
                    if thrust > 60000:
                        thrust = 60000
                    elif thrust < 10000:
                        thrust = 0

                    pitch = direction.pitch * Leap.RAD_TO_DEG
                    roll = normal.roll * Leap.RAD_TO_DEG
                    yaw = direction.yaw * Leap.RAD_TO_DEG

                    print " COMMAND thrust: %f, pitch: %f, roll: %f, yaw: %f" % (
                        thrust,
                        pitch,
                        roll,
                        yaw)


                # print 'grab_strength', hand.grab_strength
        elif len(frame.hands) > 1:
            print 'only use 1 hand!'


def main():

    listener = SampleListener()
    controller = Leap.Controller()

    # Have the sample listener receive events from the controller
    controller.add_listener(listener)

    # Keep this process running until Enter is pressed
    print "Press Enter to quit..."
    try:
        sys.stdin.readline()
    except KeyboardInterrupt:
        pass
    finally:
        # Remove the sample listener when done
        controller.remove_listener(listener)

if __name__ == "__main__":
    main()

