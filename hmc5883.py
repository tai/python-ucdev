#!/bin/env python
# -*- coding: utf-8 -*-

from bitstring import *

# HMC5883 registers

CRA  =  0 # 00  Configuration Register A Read/Write
CRB  =  1 # 01  Configuration Register B Read/Write
MR   =  2 # 02  Mode Register  Read/Write
DXRA =  3 # 03  Data Output X MSB Register  Read
DXRB =  4 # 04  Data Output X LSB Register  Read
DYRA =  5 # 05  Data Output Z MSB Register  Read
DYRB =  6 # 06  Data Output Z LSB Register  Read
DZRA =  7 # 07  Data Output Y MSB Register  Read
DZRB =  8 # 08  Data Output Y LSB Register  Read
SR   =  9 # 09  Status Register  Read
IRA  = 10 # 10  Identification Register A  Read
IRB  = 11 # 11  Identification Register B  Read
IRC  = 12 # 12  Identification Register C  Read

MODE_CONTINUOUS = 0
MODE_SINGLE     = 1

class ValueObject():
    pass

class HMC5883():
    def __init__(self, i2c, address=0x1E):
        self.i2c = i2c
        self.cfg = i2c.prepare(slaveAddress=address, isStopBit=0, isNakBit=0)

    def get_reg(self, reg):
        self.write(pack('<B', reg).bytes)
        return self.read(1)

    def set_reg(self, reg, val):
        return self.write(pack('<BB', reg, val).bytes)

    def read(self, len=1):
        buf = "\x00" * len
        return self.i2c.read(self.cfg, buf)

    def write(self, data):
        return self.i2c.write(self.cfg, data)

    def set_mode(self, mode=MODE_SINGLE):
        self.set_reg(MR, mode)

    def get_data(self):
        self.write(pack('<B', DXRA).bytes)
        raw = self.read(6)
        ret = ValueObject()
        ret.DXR = Bits(bytes=raw[0:2])
        ret.DZR = Bits(bytes=raw[2:4])
        ret.DYR = Bits(bytes=raw[4:6])
        return ret

    def get_id(self):
        self.write(pack('<B', IRA).bytes)
        return Bits(bytes=self.read(3))
