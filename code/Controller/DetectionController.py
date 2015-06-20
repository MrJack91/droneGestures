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
from Piloting import LeapListener


class DetectionController:

    def __init__(self, cfc):
        """
        :param cfc: the crazyflie controller object
        :return:
        """
        # atexit.register(self.cleanup)

        self.controller = Leap.Controller()

        # Init leap listener, for receiving events
        self.listener = LeapListener.LeapListener()
        self.listener.set_cfc(cfc)

        self.controller.add_listener(self.listener)

    def cleanup(self):
        try:
            self.controller.remove_listener(self.listener)
        except NameError:
            pass
        finally:
            print 'DetectionController: shut down'

