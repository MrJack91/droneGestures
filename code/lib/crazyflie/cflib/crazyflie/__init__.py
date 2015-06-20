#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#     ||          ____  _ __
#  +------+      / __ )(_) /_______________ _____  ___
#  | 0xBC |     / __  / / __/ ___/ ___/ __ `/_  / / _ \
#  +------+    / /_/ / / /_/ /__/ /  / /_/ / / /_/  __/
#   ||  ||    /_____/_/\__/\___/_/   \__,_/ /___/\___/
#
#  Copyright (C) 2011-2013 Bitcraze AB
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

"""
The Crazyflie module is used to easily connect/send/receive data
from a Crazyflie.

Each function in the Crazyflie has a class in the module that can be used
to access that functionality. The same design is then used in the Crazyflie
firmware which makes the mapping 1:1 in most cases.
"""

__author__ = 'Bitcraze AB'
__all__ = ['Crazyflie']

import logging
logger = logging.getLogger(__name__)
import time
import datetime
from threading import Thread

from threading import Timer, Lock

from .commander import Commander
from .console import Console
from .param import Param
from .log import Log
from .toccache import TocCache
from .mem import Memory
from .platformservice import PlatformService

import cflib.crtp

from cflib.utils.callbacks import Caller


class State:
    """Stat of the connection procedure"""
    DISCONNECTED = 0
    INITIALIZED = 1
    CONNECTED = 2
    SETUP_FINISHED = 3


class Crazyflie():
    """The Crazyflie class"""

    # Called on disconnect, no matter the reason
    disconnected = Caller()
    # Called on unintentional disconnect only
    connection_lost = Caller()
    # Called when the first packet in a new link is received
    link_established = Caller()
    # Called when the user requests a connection
    connection_requested = Caller()
    # Called when the link is established and the TOCs (that are not cached)
    # have been downloaded
    connected = Caller()
    # Called if establishing of the link fails (i.e times out)
    connection_failed = Caller()
    # Called for every packet received
    packet_received = Caller()
    # Called for every packet sent
    packet_sent = Caller()
    # Called when the link driver updates the link quality measurement
    link_quality_updated = Caller()

    state = State.DISCONNECTED

    def __init__(self, link=None, ro_cache=None, rw_cache=None):
        """
        Create the objects from this module and register callbacks.

        ro_cache -- Path to read-only cache (string)
        rw_cache -- Path to read-write cache (string)
        """
        self.link = link
        self._toc_cache = TocCache(ro_cache=ro_cache,
                                   rw_cache=rw_cache)

        self.incoming = _IncomingPacketHandler(self)
        self.incoming.setDaemon(True)
        self.incoming.start()

        self.commander = Commander(self)
        self.log = Log(self)
        self.console = Console(self)
        self.param = Param(self)
        self.mem = Memory(self)
        self.platform = PlatformService(self)

        self.link_uri = ""

        # Used for retry when no reply was sent back
        self.packet_received.add_callback(self._check_for_initial_packet_cb)
        self.packet_received.add_callback(self._check_for_answers)

        self._answer_patterns = {}

        self._send_lock = Lock()

        self.connected_ts = None

        # Connect callbacks to logger
        self.disconnected.add_callback(
            lambda uri: logger.info("Callback->Disconnected from [%s]", uri))
        self.disconnected.add_callback(self._disconnected)
        self.link_established.add_callback(
            lambda uri: logger.info("Callback->Connected to [%s]", uri))
        self.connection_lost.add_callback(
            lambda uri, errmsg: logger.info("Callback->Connection lost to"
                                            " [%s]: %s", uri, errmsg))
        self.connection_failed.add_callback(
            lambda uri, errmsg: logger.info("Callback->Connected failed to"
                                            " [%s]: %s", uri, errmsg))
        self.connection_requested.add_callback(
            lambda uri: logger.info("Callback->Connection initialized[%s]",
                                    uri))
        self.connected.add_callback(
            lambda uri: logger.info("Callback->Connection setup finished [%s]",
                                    uri))

    def _disconnected(self, link_uri):
        """ Callback when disconnected."""
        self.connected_ts = None

    def _start_connection_setup(self):
        """Start the connection setup by refreshing the TOCs"""
        logger.info("We are connected[%s], request connection setup",
                    self.link_uri)
        self.log.refresh_toc(self._log_toc_updated_cb, self._toc_cache)

    def _param_toc_updated_cb(self):
        """Called when the param TOC has been fully updated"""
        logger.info("Param TOC finished updating")
        self.connected_ts = datetime.datetime.now()
        self.connected.call(self.link_uri)
        # Trigger the update for all the parameters
        self.param.request_update_of_all_params()

    def _mems_updated_cb(self):
        """Called when the memroies has been identified"""
        logger.info("Memories finished updating")
        self.param.refresh_toc(self._param_toc_updated_cb, self._toc_cache)

    def _log_toc_updated_cb(self):
        """Called when the log TOC has been fully updated"""
        logger.info("Log TOC finished updating")
        self.mem.refresh(self._mems_updated_cb)

    def _link_error_cb(self, errmsg):
        """Called from the link driver when there's an error"""
        logger.warning("Got link error callback [%s] in state [%s]",
                       errmsg, self.state)
        if (self.link is not None):
            self.link.close()
        self.link = None
        if (self.state == State.INITIALIZED):
            self.connection_failed.call(self.link_uri, errmsg)
        if (self.state == State.CONNECTED or
                self.state == State.SETUP_FINISHED):
            self.disconnected.call(self.link_uri)
            self.connection_lost.call(self.link_uri, errmsg)
        self.state = State.DISCONNECTED

    def _link_quality_cb(self, percentage):
        """Called from link driver to report link quality"""
        self.link_quality_updated.call(percentage)

    def _check_for_initial_packet_cb(self, data):
        """
        Called when first packet arrives from Crazyflie.

        This is used to determine if we are connected to something that is
        answering.
        """
        self.state = State.CONNECTED
        self.link_established.call(self.link_uri)
        self.packet_received.remove_callback(self._check_for_initial_packet_cb)

    def open_link(self, link_uri):
        """
        Open the communication link to a copter at the given URI and setup the
        connection (download log/parameter TOC).
        """
        self.connection_requested.call(link_uri)
        self.state = State.INITIALIZED
        self.link_uri = link_uri
        try:
            self.link = cflib.crtp.get_link_driver(link_uri,
                                                   self._link_quality_cb,
                                                   self._link_error_cb)

            if not self.link:
                message = "No driver found or malformed URI: {}"\
                    .format(link_uri)
                logger.warning(message)
                self.connection_failed.call(link_uri, message)
            else:
                # Add a callback so we can check that any data is comming
                # back from the copter
                self.packet_received.add_callback(self._check_for_initial_packet_cb)

                self._start_connection_setup()
        except Exception as ex:  # pylint: disable=W0703
            # We want to catch every possible exception here and show
            # it in the user interface
            import traceback
            logger.error("Couldn't load link driver: %s\n\n%s",
                         ex, traceback.format_exc())
            exception_text = "Couldn't load link driver: %s\n\n%s" % (
                             ex, traceback.format_exc())
            if self.link:
                self.link.close()
                self.link = None
            self.connection_failed.call(link_uri, exception_text)

    def close_link(self):
        """Close the communication link."""
        logger.info("Closing link")
        if (self.link is not None):
            self.commander.send_setpoint(0, 0, 0, 0)
        if (self.link is not None):
            self.link.close()
            self.link = None
        self._answer_patterns = {}
        self.disconnected.call(self.link_uri)

    def add_port_callback(self, port, cb):
        """Add a callback to cb on port"""
        self.incoming.add_port_callback(port, cb)

    def remove_port_callback(self, port, cb):
        """Remove the callback cb on port"""
        self.incoming.remove_port_callback(port, cb)

    def _no_answer_do_retry(self, pk, pattern):
        """Resend packets that we have not gotten answers to"""
        logger.debug("Resending for pattern %s", pattern)
        # Set the timer to None before trying to send again
        self.send_packet(pk, expected_reply=pattern, resend=True)

    def _check_for_answers(self, pk):
        """
        Callback called for every packet received to check if we are
        waiting for an answer on this port. If so, then cancel the retry
        timer.
        """
        longest_match = ()
        if len(self._answer_patterns) > 0:
            data = (pk.header,) + pk.datat
            for p in self._answer_patterns.keys():
                logger.debug("Looking for pattern match on %s vs %s", p, data)
                if len(p) <= len(data):
                    if p == data[0:len(p)]:
                        match = data[0:len(p)]
                        if len(match) >= len(longest_match):
                            logger.debug("Found new longest match %s", match)
                            longest_match = match
        if len(longest_match) > 0:
            self._answer_patterns[longest_match].cancel()
            del self._answer_patterns[longest_match]

    def send_packet(self, pk, expected_reply=(), resend=False, timeout=0.2):
        """
        Send a packet through the link interface.

        pk -- Packet to send
        expect_answer -- True if a packet from the Crazyflie is expected to
                         be sent back, otherwise false

        """
        self._send_lock.acquire()
        if self.link is not None:
            if len(expected_reply) > 0 and not resend:
                pattern = (pk.header,) + expected_reply
                logger.debug("Sending packet and expecting the %s pattern back",
                             pattern)
                new_timer = Timer(timeout,
                                  lambda: self._no_answer_do_retry(pk, pattern))
                self._answer_patterns[pattern] = new_timer
                new_timer.start()
            elif resend:
                # Check if we have gotten an answer, if not try again
                pattern = expected_reply
                if pattern in self._answer_patterns:
                    logger.debug("We want to resend and the pattern is there")
                    if self._answer_patterns[pattern]:
                        new_timer = Timer(timeout,
                                          lambda:
                                          self._no_answer_do_retry(
                                              pk, pattern))
                        self._answer_patterns[pattern] = new_timer
                        new_timer.start()
                else:
                    logger.debug("Resend requested, but no pattern found: %s",
                                 self._answer_patterns)
            self.link.send_packet(pk)
            self.packet_sent.call(pk)
        self._send_lock.release()

class _IncomingPacketHandler(Thread):
    """Handles incoming packets and sends the data to the correct receivers"""
    def __init__(self, cf):
        Thread.__init__(self)
        self.cf = cf
        self.cb = []

    def add_port_callback(self, port, cb):
        """Add a callback for data that comes on a specific port"""
        logger.debug("Adding callback on port [%d] to [%s]", port, cb)
        self.add_header_callback(cb, port, 0, 0xff, 0x0)

    def remove_port_callback(self, port, cb):
        """Remove a callback for data that comes on a specific port"""
        logger.debug("Removing callback on port [%d] to [%s]", port, cb)
        for port_callback in self.cb:
            if (port_callback[0] == port and port_callback[4] == cb):
                self.cb.remove(port_callback)

    def add_header_callback(self, cb, port, channel, port_mask=0xFF,
                            channel_mask=0xFF):
        """
        Add a callback for a specific port/header callback with the
        possibility to add a mask for channel and port for multiple
        hits for same callback.
        """
        self.cb.append([port, port_mask, channel, channel_mask, cb])

    def run(self):
        while(True):
            if self.cf.link is None:
                time.sleep(1)
                continue
            pk = self.cf.link.receive_packet(1)

            if pk is None:
                continue

            #All-packet callbacks
            self.cf.packet_received.call(pk)

            found = False
            for cb in self.cb:
                if (cb[0] == pk.port & cb[1] and
                        cb[2] == pk.channel & cb[3]):
                    try:
                        cb[4](pk)
                    except Exception:  # pylint: disable=W0703
                        # Disregard pylint warning since we want to catch all
                        # exceptions and we can't know what will happen in
                        # the callbacks.
                        import traceback
                        logger.warning("Exception while doing callback on port"
                                       " [%d]\n\n%s", pk.port,
                                       traceback.format_exc())
                    if (cb[0] != 0xFF):
                        found = True

            if not found:
                logger.warning("Got packet on header (%d,%d) but no callback "
                               "to handle it", pk.port, pk.channel)
