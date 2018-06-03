#!/bin/env python
# -*- coding: utf-8-unix -*-
"""
I2C driver for Si4702 FM radio tuner chip.

This chip can be controlled by either SPI or I2C, and
this driver takes care of I2C part. It's not really an I2C,
but made close enough to be driven by I2C master.

It turned out the setup I have forces me to take complicated
sequence to enter I2C mode. So this driver is not well tested.

"""

from struct import pack, unpack
from ucdev.register import Value, Register

import logging
log = logging.getLogger(__name__)

from IPython import embed

######################################################################
# Si4702 registers
#
# Register configuration of Si4702-B16 and Si4702-03-C19 differs,
# but "C" rev seems to be upper compatible.
######################################################################

DEVICEID   = Register("PN:4 MFGID:12", 0x00)
CHIPID     = Register("REV:6 DEV:4 FIRMWARE:6", 0x01)
POWERCFG   = Register(
    "DSMUTE DMUTE MONO : RDSM SKMODE SEEKUP SEEK : DISABLE :5 ENABLE", 0x02)
CHANNEL    = Register("TUNE :5 CHAN:10", 0x03)
SYSCONFIG1 = Register(
    "RDSIEN STCIEN : RDS DE AGCD :2 BLNDADJ:2 GPIO3:2 GPIO2:2 GPIO1:2", 0x04)
SYSCONFIG2 = Register("SEEKTH:8 BAND:2 SPACE:2 VOLUME:4", 0x05)
SYSCONFIG3 = Register("SMUTER:2 SMUTEA:2 :3 VOLEXT SKSNR:4 SKCNT:4", 0x06)
TEST1      = Register("XOSCEN AHIZEN :14", 0x07)
TEST2      = Register(":16", 0x08)
BOOTCONFIG = Register(":16", 0x09)
STATUSRSSI = Register("RDSR STC SF_BL AFCRL RDSS BLERA:2 ST RSSI:8", 0x0A)
READCHAN   = Register("BLERB:2 BLERC:2 BLERD:2 READCHAN:10", 0x0B)
RDSA       = Register("RDSA:16", 0x0C)
RDSB       = Register("RDSB:16", 0x0D)
RDSC       = Register("RDSC:16", 0x0E)
RDSD       = Register("RDSD:16", 0x0F)

######################################################################

class SI4702(object):
    def __init__(self, i2c, address=0b0010000):
        self.i2c = i2c

        #
        # AN230 - 2.3. 2-Wire Control Interface
        #
        # The control word is latched internally on rising SCLK edges
        # and is eight bits in length, comprised of a seven bit device
        # address equal to 0010000b and a read/write bit (read = 1 and
        # write = 0). The ordering of the control word is A6:A0, R/W as
        # shown below. The device remains in the read or write state
        # until the STOP condition is received.
        #
        self.cfg = i2c.prepare(slaveAddress=address, isStopBit=1, isNakBit=1)

        # Read registers into "shadow registers" to apply further writes.
        self.sreg = self.get_all_regs()

    def read(self, len=1):
        buf = bytearray(len)
        return self.i2c.read(self.cfg, buf)

    def write(self, data):
        return self.i2c.write(self.cfg, data)

    def get_all_regs(self):
        #
        # AN230 - 2.3. 2-Wire Control Interface
        #
        # Device register addresses are incremented by an internal
        # address counter, starting at the upper byte of register 0Ah,
        # followed by the lower byte of register 0Ah, and wrapping
        # back to 00h at the end of the register file.
        #
        tmp = self.read(32)
        buf = list(unpack('>16H', tmp))
        loc = (0x0 - 0xA) & 0xF
        return buf[loc:] + buf[:loc]

    def get_reg(self, reg, size=None):
        regs = self.get_all_regs()
        val = regs[reg]

        return reg(val) if isinstance(reg, Register) else val

    def set_reg(self, reg, *arg, **kw):
        # update shadow buffer
        newval = reg(*arg, **kw).value.uint

        self.sreg = self.get_all_regs()
        self.sreg[reg] = newval

        #
        # AN230 - 2.3. 2-Wire Control Interface
        #
        # Device register addresses are incremented by an internal
        # address counter, starting with the upper byte of register
        # 02h, followed by the lower byte of register 02h, and
        # wrapping back to 00h at the end of the register file.
        #

        #
        # As decribe above, I always need to start writing from
        # 02h register. So except 02h register itself, I do a full
        # writeback to all R/W registers, from 02h to 09h (inclusive).
        #
        if reg == 0x2:
            # register 02h can be written independently
            return self.write(pack('>H', newval))
        else:
            # do a full writeback to 02h - 09h
            return self.write(pack('>8H', *self.sreg[0x2:(0x9 + 1)]))

def add_register(cls):
    def makeprop(reg):
        def fget(self):
            tmp = self.get_reg(reg)
            def update_hook(v):
                self.set_reg(reg, v)
            tmp.subscribe(update_hook)
            return tmp
        def fset(self, v):
            self.set_reg(reg, v)
        return property(fget, fset)

    for name, reg in globals().items():
        if not hasattr(cls, name) and isinstance(reg, Register):
            setattr(cls, name, makeprop(reg))

add_register(SI4702)

# export symbols
__all__  = [i for i in list(locals()) if i.isupper()]
__all__ += [i for i in list(locals()) if i.startswith("SI47")]
