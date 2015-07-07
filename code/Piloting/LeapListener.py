# https://developer.leapmotion.com/documentation/python/devguide/Sample_Tutorial.html
# https://developer.leapmotion.com/documentation/python/devguide/Leap_Frames.html

import os
import sys
import inspect

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
from Piloting import PilotingStates, PilotingConfiguration

class LeapListener(Leap.Listener):

    def __init__(self):
        super(LeapListener, self).__init__()

        self.current_state = PilotingStates.PilotingStates.STATE_0_OFF
        self.last_state = self.current_state

        self.cfc = None

        self.piloting_configuration = None

    def set_cfc(self, cfc):
        self.cfc = cfc
        self.piloting_configuration = PilotingConfiguration.PilotingConfiguration(self.cfc)

    def on_init(self, controller):
        print "LeapListener: init"

    def on_connect(self, controller):
        print "LeapListener: connected (mostly need to wait on crazyflie...)"

    def on_disconnect(self, controller):
        # Note: not dispatched when running in a debugger.
        print "LeapListener: disconnected"

    def on_exit(self, controller):
        print "LeapListener: shut down"

    def on_frame(self, controller):

        # check on connection loss of crazyflie -> stop system (STATE_0_OFF is dead)
        if self.current_state != PilotingStates.PilotingStates.STATE_0_OFF and self.cfc.is_connected is False:
            self.current_state = PilotingStates.PilotingStates.STATE_0_OFF
            print "Controller was stopped, because connection to crazyflie was lost"

        # log state change
        if self.current_state != self.last_state:
            print "STATE: " + PilotingStates.PilotingStates.STATE_NAME[self.last_state] + " => " + PilotingStates.PilotingStates.STATE_NAME[self.current_state]
            self.last_state = self.current_state

        frame = controller.frame()

        '''
        print "Frame id: %d, timestamp: %d, hands: %d, fingers: %d, tools: %d, gestures: %d" % (
          frame.id, frame.timestamp, len(frame.hands), len(frame.fingers), len(frame.tools), len(frame.gestures())
        )
        '''

        # flight control
        if len(frame.hands) == 1:
            # for hand in frame.hands:
            hand = frame.hands[0]

            # check if next state is handled
            if self.current_state in self.piloting_configuration.state_handler:
                self.piloting_configuration.state_handler[self.current_state].handle(hand)
                self.current_state = self.piloting_configuration.state_handler[self.current_state].next_state

        elif len(frame.hands) > 1:
            print 'More than one hand detected! Pls, only use one hand.'

        else:
            # stay in off state until drone was connected
            if self.cfc.is_connected is True:
                # no hands -> reset if not flight
                self.piloting_configuration.state_handler[PilotingStates.PilotingStates.STATE_1_INIT].reset_control()
                self.current_state = self.piloting_configuration.state_handler[PilotingStates.PilotingStates.STATE_1_INIT].next_state
