#!/usr/bin/env python
# -*- coding: utf-8-unix -*-

from bitstring import *
from register import Register

W = Register("PHASE:5 POWER_DOWN CONTROL:2 FREQ:32", 0x00)

"""
Usage:
  spi  = CySPI(dev)
  gpio = CyGPIO(dev)
  dds  = AD9850(spi, RESET=gpio.pin(0))
  dds.reset()
  dds.send(FREQ=0x0000FFFF, PHASE=0b00000)

"""
class AD9850(object):
    CE = property(lambda s:s.__ce.get(), lambda s,v:s.__ce.set(1 if v else 0))
    RESET = property(lambda s:s.__rs.get(), lambda s,v:s.__rs.set(1 if v else 0))

    def __init__(self, spi, CE=None, RESET=None):
        self.spi = spi
        self.__ce = CE
        self.__rs = RESET
        self.debug = False

    def reset(self, freq=100000):
        self.reset_spi(freq)
        # RESET pulse must be at least (5 * REFCLK) pulse width.
        # This is 500ns when REFCLK == 10MHz (which is MUCH slower than
        # usual REFCLK), so following should be good enough...
        self.RESET = 0
        self.RESET = 1
        self.RESET = 0

    def reset_spi(self, freq):
        spi = self.spi

        rc = spi.set_config({
                'frequency': freq,
                'dataWidth': 8,
                'protocol': spi.MOTOROLA,
                'isMsbFirst': True,
                'isMaster': True,
                'isContinuousMode': True,
                'isCpha': False,
                'isCpol': False,
                })
        if rc != 0:
            raise Exception("ERROR: SPI init failed=%d" % rc)

    def send(self, *arg, **kw):
        tmp = W(*arg, **kw).value
        tmp.reverse()
        if self.debug:
            print(tmp.bin)
        self.spi.send(tmp.bytes)
