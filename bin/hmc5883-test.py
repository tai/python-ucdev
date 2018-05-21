#!/usr/bin/env python
# -*- coding: utf-8 -*-

from cy7c65211 import *
from hmc5883 import *
from IPython import embed

#dll = "c:/app/Cypress/Cypress-USB-Serial/library/lib/cyusbserial.dll"
dll = "cyusbserial"
lib = CyUSBSerial(lib = dll)
dev = lib.find().next()
ffi = lib.ffi

i2c = CyI2C(dev)
i2c.debug = 1

hmc = HMC5883(i2c)

embed()
