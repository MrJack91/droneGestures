# -*- coding: utf-8 -*-
#
#     ||          ____  _ __
#  +------+      / __ )(_) /_______________ _____  ___
#  | 0xBC |     / __  / / __/ ___/ ___/ __ `/_  / / _ \
#  +------+    / /_/ / / /_/ /__/ /  / /_/ / / /_/  __/
#   ||  ||    /_____/_/\__/\___/_/   \__,_/ /___/\___/
#
#  Copyright (C) 2014 Bitcraze AB
#
#  Crazyflie Nano Quadcopter Client
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.

#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA  02110-1301, USA.


import time
import sys
from threading import Thread

sys.path.append("lib/crazyflie")
import cflib
from cflib.crazyflie import Crazyflie

import logging
logging.basicConfig(level=logging.ERROR)

'''
import cflib.crtp
from cfclient.utils.logconfigreader import LogConfig
from cflib.crazyflie import Crazyflie
'''

class CrazyflieController:

    def __init__(self):
        print 'CrazyflieController: init'
        self._cf = None
        # atexit.register(self.cleanup)

    def cleanup(self):
        if self._cf is not None:
            # try to access crazyflie -> will throw NameError if undefined
            self._cf.commander.send_setpoint(0, 0, 0, 0)
            # wait to send signal
            time.sleep(0.1)
            self._cf.close_link()

        print 'CrazyflieController: shut down'

    def connect(self):
        # Initialize the low-level drivers (don't list the debug drivers)
        cflib.crtp.init_drivers(enable_debug_driver=False)
        # Scan for Crazyflies
        print "CrazyflieController: scanning interfaces for crazyflies..."
        available = cflib.crtp.scan_interfaces()

        if len(available) > 0:
            print "CrazyflieController: crazyflies found:"
            for i in available:
                print i[0]

            #le = CrazyflieController(available[0][0])
            #link_uri = available[0][0]

            # hard code to correct one, because there are sometimes disturbing signals
            link_uri = 'radio://0/80/250K'

        else:
            print "CrazyflieController: no crazyflies found, cannot connect"
            return False

        self._cf = Crazyflie()

        self._cf.connected.add_callback(self._connected)
        self._cf.disconnected.add_callback(self._disconnected)
        self._cf.connection_failed.add_callback(self._connection_failed)
        self._cf.connection_lost.add_callback(self._connection_lost)

        # connect to drone
        self._cf.open_link(link_uri)

    def _connected(self, link_uri):
        """ This callback is called form the Crazyflie API when a Crazyflie
        has been connected and the TOCs have been downloaded."""

        print "CrazyflieController: connected to %s" % link_uri

        '''
        # The definition of the logconfig can be made before connecting
        self._lg_stab = LogConfig(name="debug", period_in_ms=50)
        self._lg_stab.add_variable("gyro.x", "float")
        self._lg_stab.add_variable("gyro.y", "float")
        self._lg_stab.add_variable("gyro.z", "float")

        self._lg_stab.add_variable("stabilizer.roll", "float")
        self._lg_stab.add_variable("stabilizer.pitch", "float")
        self._lg_stab.add_variable("stabilizer.yaw", "float")
        self._lg_stab.add_variable("stabilizer.thrust", "uint16_t")

        # Adding the configuration cannot be done until a Crazyflie is
        # connected, since we need to check that the variables we
        # would like to log are in the TOC.
        try:
            self._cf.log.add_config(self._lg_stab)
            # This callback will receive the data
            self._lg_stab.data_received_cb.add_callback(self._stab_log_data)
            # This callback will be called on errors
            self._lg_stab.error_cb.add_callback(self._stab_log_error)
            # Start the logging
            self._lg_stab.start()
        except KeyError as e:
            print "Could not start log configuration," \
                  "{} not found in TOC".format(str(e))
        except AttributeError:
            print "Could not add Stabilizer log config, bad configuration."
        '''

    '''
    def _stab_log_error(self, logconf, msg):
        """Callback from the log API when an error occurs"""
        print "Error when logging %s: %s" % (logconf.name, msg)

    def _stab_log_data(self, timestamp, data, logconf):
        """Callback froma the log API when data arrives"""


        print " DEBUG thrust: %f, pitch: %f, roll: %f, yaw: %f" % (
                    data['stabilizer.thrust'],
                    data['stabilizer.pitch'],
                    data['stabilizer.roll'],
                    data['stabilizer.yaw']
        )


        # print "[%d][%s]: %s" % (timestamp, logconf.name, data)
    '''



    def _connection_failed(self, link_uri, msg):
        """Callback when connection initial connection fails (i.e no Crazyflie at the speficied address)"""
        print "CrazyflieController: connection to %s failed: %s" % (link_uri, msg)

    def _connection_lost(self, link_uri, msg):
        """Callback when disconnected after a connection has been made (i.e Crazyflie moves out of range)"""
        print "CrazyflieController: connection to %s lost: %s" % (link_uri, msg)

    def _disconnected(self, link_uri):
        """Callback when the Crazyflie is disconnected (called in all cases)"""
        print "CrazyflieController: disconnected from %s" % link_uri

'''
    def _ramp_motors(self):
        thrust_mult = 1
        thrust_step = 500
        thrust = 10000
        pitch = 0
        roll = 0
        yawrate = 0

        #Unlock startup thrust protection
        self._cf.commander.send_setpoint(0, 0, 0, 0)

        while thrust >= 10000:
            self._cf.commander.send_setpoint(roll, pitch, yawrate, thrust)
            time.sleep(0.1)
            if thrust >= 15000:
                thrust_mult = -1
            thrust += thrust_step * thrust_mult
        self._cf.commander.send_setpoint(0, 0, 0, 0)
        # Make sure that the last packet leaves before the link is closed
        # since the message queue is not flushed before closing
        time.sleep(0.1)
        self._cf.close_link()
'''
