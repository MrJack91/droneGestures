# https://developer.leapmotion.com/documentation/python/devguide/Sample_Tutorial.html
# https://developer.leapmotion.com/documentation/python/devguide/Leap_Frames.html


import os
import sys
import inspect

# lib only for os x
src_dir = os.path.dirname(inspect.getfile(inspect.currentframe()))
lib_dir = os.path.abspath(os.path.join(src_dir, '../lib/leap'))
sys.path.insert(0, lib_dir)

import Leap
from Piloting import LeapListener


class DetectionController:

    def __init__(self, cfc, debug):
        """
        :param cfc: the crazyflie controller object
        :return:
        """
        # atexit.register(self.cleanup)

        self.controller = Leap.Controller()

        # Init leap listener, for receiving events
        self.listener = LeapListener.LeapListener()
        self.listener.set_cfc(cfc, debug)

        self.controller.add_listener(self.listener)

    def cleanup(self):
        try:
            self.controller.remove_listener(self.listener)
        except NameError:
            pass
        finally:
            print 'DetectionController: shut down'

