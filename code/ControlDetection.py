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
lib_dir = os.path.abspath(os.path.join(src_dir, 'lib'))
sys.path.insert(0, lib_dir)

import Leap
from Leap import CircleGesture, KeyTapGesture, ScreenTapGesture, SwipeGesture

# global vars
fist_detected = 0

class SampleListener(Leap.Listener):

    def on_init(self, controller):
        print "Initialized"

    def on_connect(self, controller):
        print "Connected"
        controller.enable_gesture(Leap.Gesture.TYPE_SWIPE)

    def on_disconnect(self, controller):
        # Note: not dispatched when running in a debugger.
        print "Disconnected"

    def on_exit(self, controller):
        print "Exited"

    def on_frame(self, controller):
        # print "Frame available"
        frame = controller.frame()

        '''
        print "Frame id: %d, timestamp: %d, hands: %d, fingers: %d, tools: %d, gestures: %d" % (
          frame.id, frame.timestamp, len(frame.hands), len(frame.fingers), len(frame.tools), len(frame.gestures())
        )
        '''
        global fist_detected
        if len(frame.hands) == 1:
            for hand in frame.hands:
                if hand.grab_strength == 1 and fist_detected == 0:
                    fist_detected = 1
                    print 'fist dedected! dron will fly, if you open your hand...'
                elif fist_detected == 1 and hand.grab_strength == 0:
                    fist_detected = 0
                    print 'hand position initialized! drone control is activated'
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

