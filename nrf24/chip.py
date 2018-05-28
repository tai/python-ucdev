# -*- coding: utf-8 -*-
"""Access interface for Nordic Semiconductor nRF24L01/nRF24L01+.

This module provides access to Nordic Semiconductor nRF24L01/nRF24L01+
device over a SPI/GPIO bus. Access to both underlying buses needs to
be provided by other modules, such as CySPI/CyGPIO class included in
ucdev.cyusbserial module. GPIO is needed to control CE pin, which
controls TX/RX.

Typical usage:

  from ucdev.cyusbserial import *
  from ucdev.nrf24 import *

  # load external library for accessing SPI/GPIO bus
  dll = "c:/app/Cypress/Cypress-USB-Serial/library/lib/cyusbserial.dll"
  lib = CyUSBSerial(lib = dll)
  txd = list(lib.find())

  # initialize nRF24 device
  tx = nRF24(CySPI(txd), CE=CyGPIO(txd).pin(0))
  tx.reset(MODE_ESB|DIR_SEND)
  tx.TX_ADDR = tx.RX_ADDR_P0 = 0x1122334455

  # clear status and send 32bytes of "X"s
  tx.STATUS |= 0
  tx.send("X" * 32)

  # check status
  if not tx.STATUS.TX_DS:
      raise Exception("TX error")

All SPI commands can be called as instance methods, and
all SPI registers and bitfields can be accessed as attributes.
So the interface is nearly transparent, and following code
will work as expected:

  # verbose way to access CONFIG register with R_REGISTER/W_REGISTER command
  reg = tx.R_REGISTER(CONFIG)
  reg.PRIM_RX = 1
  tx.W_REGISTER(CONFIG, reg)

  # same as above
  tx.CONFIG = tx.CONFIG(PRIM_RX=1)

  # same as above
  tx.CONFIG |= CONFIG(PRIM_RX=1)

  # same as above
  tx.CONFIG.PRIM_RX = 1

Note on register access:

You can access register value with both

  reg = tx.CONFIG

and

  reg = tx.CONFIG()

Former returns "live" register instance. That is,

  reg = tx.CONFIG
  reg.PRIM_RX = 1

will do a writeback to CONFIG register of tx device immediately.
This is a feature to support following behavior:

  tx.CONFIG.PRIM_RX = 1

If you do not want "live" instance, you can make a clone a "dead"
instance by doing:

  reg = tx.CONFIG()
  reg.PRIM_RX = 1

This only updates PRIM_RX value of cloned "reg" register, and will
not change actual register value of tx instance.

"""

__author__ = 'Taisuke Yamada <tai@remove-if-not-spam.rakugaki.org>'

import sys, os, time
from struct import pack, unpack
from register import Value, Register

# SPI registers
CONFIG = Register(": MASK_RX_DR MASK_TX_DS MASK_MAX_RT EN_CRC CRCO PWR_UP PRIM_RX", 0x00)
EN_AA = Register(":2 ENAA_P5 ENAA_P4 ENAA_P3 ENAA_P2 ENAA_P1 ENAA_P0", 0x01)
EN_RXADDR = Register(":2 ERX_P5 ERX_P4 ERX_P3 ERX_P2 ERX_P1 ERX_P0", 0x02)
SETUP_AW  = Register(":6 AW:2", 0x03)
SETUP_RETR = Register("ARD:4 ARC:4", 0x04)
RF_CH = Register(": RF_CH:7", 0x05)
RF_SETUP = Register(":3 PLL_LOCK RF_DR RF_PWR:2 LNA_HCURR", 0x06)
STATUS = Register(": RX_DR TX_DS MAX_RT RX_P_NO:3 TX_FULL", 0x07)
OBSERVE_TX = Register("PLOG_CNT:4 ARC_CNT:4", 0x08)
CD = Register(":7 CD", 0x09)
RX_ADDR_P0 = Register("RX_ADDR_P0:40", 0x0A)
RX_ADDR_P1 = Register("RX_ADDR_P1:40", 0x0B)
RX_ADDR_P2 = Register("RX_ADDR_P2:8", 0x0C)
RX_ADDR_P3 = Register("RX_ADDR_P3:8", 0x0D)
RX_ADDR_P4 = Register("RX_ADDR_P4:8", 0x0E)
RX_ADDR_P5 = Register("RX_ADDR_P5:8", 0x0F)
TX_ADDR = Register("TX_ADDR:40", 0x10)
RX_PW_P0 = Register(":2 RX_PW_P0:6", 0x11)
RX_PW_P1 = Register(":2 RX_PW_P1:6", 0x12)
RX_PW_P2 = Register(":2 RX_PW_P2:6", 0x13)
RX_PW_P3 = Register(":2 RX_PW_P3:6", 0x14)
RX_PW_P4 = Register(":2 RX_PW_P4:6", 0x15)
RX_PW_P5 = Register(":2 RX_PW_P5:6", 0x16)
FIFO_STATUS = Register(": TX_REUSE TX_FULL TX_EMPTY :2 RX_FULL RX_EMPTY", 0x17)
DYNPD = Register(":2 DPL_P5 DPL_P4 DPL_P3 DPL_P2 DPL_P1 DPL_P0", 0x1C)
FEATURE = Register(":5 EN_DPL EN_ACK_PAY EN_DYN_ACK", 0x1D)

class Command(Value):
    pass

# SPI commands
R_REGISTER = Command(0x00)
W_REGISTER = Command(0x20)
R_RX_PAYLOAD = Command(0x61)
W_TX_PAYLOAD = Command(0xA0)
FLUSH_TX = Command(0xE1)
FLUSH_RX = Command(0xE2)
REUSE_TX_PL = Command(0xE3)
ACTIVATE = Command(0x50)
R_RX_PL_WID = Command(0x60)
W_ACK_PAYLOAD = Command(0xA8)
W_TX_PAYLOAD_NOACK = Command(0xB0)
NOP = Command(0xFF)

DIR_OFFSET = 0
DIR_MASK   = 1<<DIR_OFFSET
DIR_SEND   = 0<<DIR_OFFSET
DIR_RECV   = 1<<DIR_OFFSET

MODE_OFFSET = 1
MODE_MASK = 3<<MODE_OFFSET
MODE_TEST = 0<<MODE_OFFSET
MODE_ESB  = 1<<MODE_OFFSET
MODE_SB   = 2<<MODE_OFFSET
MODE_BLE  = 3<<MODE_OFFSET

######################################################################

class nRF24API(object):
    def __init__(self, spi):
        self.spi = spi

    def NOP(self):
        spi = self.spi
        ret = spi.send(pack("<B", NOP))
        return STATUS(ret[0])

    def R_REGISTER(self, reg):
        spi = self.spi

        if reg in (RX_ADDR_P0, RX_ADDR_P1, TX_ADDR):
            ret = spi.send(pack("<B5x", R_REGISTER | reg))
        else:
            ret = spi.send(pack("<B1x", R_REGISTER | reg))

        # endian for nRF24 is (LSByte-first, MSBit-first)
        tmp = ret[1:]
        tmp.reverse()

        if isinstance(reg, Register):
            return STATUS(ret[0]), reg(tmp)
        else:
            return STATUS(ret[0]), tmp

    # Usage:
    #   nrf.W_REGISTER(REG)
    #   nrf.W_REGISTER(REG, VALUE)
    #   nrf.W_REGISTER(REG, FIELD1=123, FIELD2=234, ...)
    #
    def W_REGISTER(self, reg, *arg, **kw):
        spi = self.spi
        tmp = reg(*arg, **kw).value
        tmp.byteswap()
        ret = spi.send(pack("<B", W_REGISTER | reg) + tmp.bytes)
        return STATUS(ret[0])

    def R_RX_PAYLOAD(self, length=32):
        spi = self.spi
        ret = spi.send(pack("<B{0}x".format(length), R_RX_PAYLOAD))
        tmp = ret[1:]
        tmp.reverse()
        return STATUS(ret[0]), tmp

    def W_TX_PAYLOAD(self, data):
        spi = self.spi
        tmp = bytearray(str(data))
        tmp.reverse()
        ret = spi.send(pack("<B", W_TX_PAYLOAD) + tmp)
        return STATUS(ret[0])

    def FLUSH_TX(self):
        spi = self.spi
        ret = spi.send(pack("<B", FLUSH_TX))
        return STATUS(ret[0])

    def FLUSH_RX(self):
        spi = self.spi
        ret = spi.send(pack("<B", FLUSH_RX))
        return STATUS(ret[0])

    def REUSE_TX_PL(self):
        spi = self.spi
        ret = spi.send(pack("<B", REUSE_TX_PL))
        return STATUS(ret[0])

    def ACTIVATE(self, data=0x73):
        spi = self.spi
        ret = spi.send(pack("<BB", ACTIVATE, data))
        return STATUS(ret[0])

    def R_RX_PL_WID(self):
        spi = self.spi
        ret = spi.send(pack("<B1x", R_RX_PL_WID))
        return STATUS(ret[0]), ret[1]

    def W_ACK_PAYLOAD(self, data, pipe=0):
        spi = self.spi
        tmp = bytearray(str(data))
        tmp.reverse()
        ret = spi.send(pack("<B", W_ACK_PAYLOAD | pipe) + tmp)
        return STATUS(ret[0])

    def W_TX_PAYLOAD_NOACK(self, data):
        spi = self.spi
        tmp = bytearray(str(data))
        tmp.reverse()
        ret = spi.send(pack("<B", W_TX_PAYLOAD_NOACK) + tmp)
        return STATUS(ret[0])

def add_command(cls):
    # TODO:
    # - Add parameters to Command objects so API can be generated automatically.
    def makefunc(cmd):
        def apifunc(self):
            # TODO: Not implemented
            pass
        return apifunc

    for name, cmd in globals().items():
        if not hasattr(cls, name) and isinstance(cmd, Command):
            setattr(cls, name, makefunc(cmd))

add_command(nRF24API)

######################################################################

class nRF24(nRF24API):
    # Non-SPI pins for extra control.
    # NOTE:
    # - CSN pin is (or should be) managed in SPI class, not here.
    CE  = property(lambda s:s.__ce.get(), lambda s,v:s.__ce.set(1 if v else 0))
    IRQ = property(lambda s:s.__irq.get())

    def __init__(self, spi, CE=None, IRQ=None):
        self.debug = False
        self.spi   = spi
        self.__ce  = CE
        self.__irq = IRQ

    # NOTE:
    # - Here, I'm treating __repr__ like __str__ as my goal is to improve
    #   interactive usability of this class under ipython.
    def __repr__(self):
        name = self.__class__.__name__
        return "{0}{1}".format(name, str(self.STATUS))

    def reset(self, mode=MODE_ESB|DIR_RECV, freq=100000):
        self.reset_spi(freq)
        self.reset_mode(mode)

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

    def reset_mode(self, mode):
        if mode & MODE_MASK == MODE_TEST:
            self.CONFIG = CONFIG(PWR_UP=1)
            time.sleep(1.5/1000.0) # max 1.5ms from power-down mode
            self.CONFIG.PRIM_RX = 0

            self.EN_AA = 0
            self.SETUP_RETR = 0
            self.RF_SETUP.PLL_LOCK = 1
            self.TX_ADDR = 0xFFFFFFFFFF
            self.W_TX_PAYLOAD("\xFF" * 32)

            self.CONFIG.EN_CRC = 0

        elif mode & MODE_MASK == MODE_ESB:
            is_rx = mode & DIR_MASK == DIR_RECV

            self.CONFIG = CONFIG(PWR_UP=1, EN_CRC=1, PRIM_RX=int(is_rx))
            time.sleep(1.5/1000.0)

            #
            # Now, configure registers.
            #
            # As node might switch send/recv role later, so whenever possible,
            # just configure all registers regardless of current role.
            #

            # Enable all addresses by default
            # Turn it off in application if power consumption is an issue.
            self.EN_RXADDR = 0xFF
            self.EN_AA = 0xFF

            # NOTE:
            # - P0 should be 0 by default as P0 only receives ACK by default.
            # - Update this in application code if using ACK-with-PAYLOAD.
            self.RX_PW_P0 = 0
            for i in range(1, 6):
                setattr(self, "RX_PW_P" + str(i), 32)

            # other parameters
            self.SETUP_RETR.ARC = 3
            self.RF_SETUP = self.RF_SETUP(PLL_LOCK=0, RF_DR=1)

            # extra features
            self.FEATURE = FEATURE(EN_DPL=1, EN_ACK_PAY=1, EN_DYN_ACK=1)
            self.ACTIVATE()

            # enable recv-mode immediately
            if is_rx:
                self.CE = 1

        elif mode & MODE_MASK == MODE_SB:
            is_rx = mode & DIR_MASK == DIR_RECV

            self.CONFIG = CONFIG(PWR_UP=1, EN_CRC=1, PRIM_RX=int(is_rx))

            time.sleep(1.5/1000.0)

            self.EN_RXADDR = 0xFF
            self.EN_AA = 0
            self.SETUP_RETR = 0
            self.RF_SETUP = self.RF_SETUP(PLL_LOCK=0, RF_DR=0)

            if is_rx:
                self.CE = 1

        elif mode & MODE_MASK == MODE_BLE:
            # TODO: BLE mode is not yet implemented
            self.CONFIG = CONFIG(PWR_UP=1, EN_CRC=0, PRIM_RX=0)

            time.sleep(1.5/1000.0)

            self.TXADDR = ""
            self.EN_AA = 0
            self.SETUP_RETR = 0
            self.RF_SETUP = self.RF_SETUP(PLL_LOCK=0, RF_DR=0)
            self.FEATURE = 0

    def flush(self):
        self.CE = 1
        self.STATUS |= 0
        while not self.FIFO_STATUS.TX_EMPTY and not self.STATUS.MAX_RT:
            # NOTE:
            # - Minimal processing time is 10[us] + 130[us] + transfer time.
            #   That's ~144[us] for 1byte payload @ 2Mbps configuration.
            # - Here, I'll just wait 1[ms] as that should be long enough.
            #   Sleeping for us duration is not that accurate anyway.
            time.sleep(1/1000.0)
        self.CE = 0

    def queue(self, data=None):
        if data:
            self.W_TX_PAYLOAD(data)
        else:
            self.REUSE_TX_PL()

    def send(self, data=None):
        self.queue(data)
        self.flush()

    def recv(self, length=None):
        if self.FIFO_STATUS.RX_EMPTY:
            return None,None
        if length is None:
            ret, length = self.R_RX_PL_WID()
        return self.R_RX_PAYLOAD(length)

def add_register(cls):
    def makeprop(reg):
        def fget(self):
            tmp = self.R_REGISTER(reg)[1]
            #
            # Here, a hook is registered to support following usage:
            #
            #   device.REGISTER.FIELD = new_value
            #
            # A hook is registered to an object (= RegisterValue instance)
            # returned by device.REGISTER access, and that hook updates
            # actual register of the originating device if any of its fields
            # is updated.
            #
            # In Python, I can also accomplish this by decorating
            # property methods (or even __setattr__) in class hierarchy,
            # but that seemed to be too hacky. So I ended up with this
            # observer pattern. Not sure if this is "Pythonic".
            #
            def update_hook(v):
                self.W_REGISTER(reg, v)
            tmp.subscribe(update_hook)
            return tmp
        def fset(self, v):
            self.W_REGISTER(reg, v)
        return property(fget, fset)

    for name, reg in globals().items():
        if not hasattr(cls, name) and isinstance(reg, Register):
            setattr(cls, name, makeprop(reg))

add_register(nRF24)

######################################################################

# export ALLCAPS and nRF24* symbols
__all__  = [i for i in list(locals()) if i.isupper()]
__all__ += [i for i in list(locals()) if i.startswith("nRF24")]
