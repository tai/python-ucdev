#!/bin/env python
# -*- coding: utf-8 -*-

"""
To run and test this script, connection betwen CY7C65211 and
AD9850 must be done as below:

Cypress       nRF24L01
----------------------
 GPIO 0 <---> RESET
   SSEL <---> FU_UD
   MOSI <---> DATA
   SCLK <---> W_CLK

"""

import sys, os
import time
from IPython import embed

from cy7c65211 import *
from ad9850 import *

dll = "c:/app/Cypress/Cypress-USB-Serial/library/lib/cyusbserial.dll"
lib = CyUSBSerial(lib = dll)

dev = lib.find().next()
ctl = CyGPIO(dev)
dds = AD9850(CySPI(dev), RESET=ctl.pin(0))
dds.reset()
dds.send(FREQ=0xFFFF)

embed()
