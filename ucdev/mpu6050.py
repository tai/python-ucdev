#!/usr/bin/env python
# -*- coding: utf-8-unix -*-

from struct import pack, unpack
from ucdev.register import Value, Register

import logging
log = logging.getLogger(__name__)

from IPython import embed

######################################################################
# I2C MPU-6050 registers
######################################################################

SELF_TEST_X = Register("XA_TEST:3 XG_TEST:5", 0x0D)
SELF_TEST_Y = Register("YA_TEST:3 YG_TEST:5", 0x0E)
SELF_TEST_Z = Register("ZA_TEST:3 ZG_TEST:5", 0x0F)
SELF_TEST_A = Register(":2 XA_TEST:2 YA_TEST:2 ZA_TEST:2", 0x10)
SMPLRT_DIV = Register("SMPLRT_DIV:8", 0x19)
CONFIG = Register(":2 EXT_SYNC_SET:3 DLPF_CFG:3", 0x1A)
GYRO_CONFIG = Register(":3 FS_SEL:2 :3", 0x1B)
ACCEL_CONFIG = Register("XA_ST YA_ST ZA_ST AFS_SEL:2 :3", 0x1C)

FIFO_EN = Register(
    "TEMP_FIFO_EN XG_FIFO_EN YG_FIFO_EN ZG_FIFO_EN " +
    "ACCESS_FIFO_EN SLV2_FIFO_EN SLV1_FIFO_EN SLV0_FIFO_EN", 0x23)
I2C_MST_CTRL = Register(
    "MULT_MST_EN WAIT_FOR_ES SLV_3_FIFO_EN I2C_MST_P_NSR I2C_MSG_CLK:4", 0x24)

I2C_SLV0_ADDR = Register("I2C_SLV0_RW I2C_SLV0_ADDR:7", 0x25)
I2C_SLV0_REG = Register("I2C_SLV0_REG:8", 0x26)
I2C_SLV0_CTRL = Register(
    "I2C_SLV0_EN I2C_SLV0_BYTE_SW I2C_SLV0_REG_DIS " +
    "I2C_SLV0_GRP I2C_SLV0_LEN:4", 0x27)

I2C_SLV1_ADDR = Register("I2C_SLV1_RW I2C_SLV1_ADDR:7", 0x28)
I2C_SLV1_REG = Register("I2C_SLV1_REG:8", 0x29)
I2C_SLV1_CTRL = Register(
    "I2C_SLV1_EN I2C_SLV1_BYTE_SW I2C_SLV1_REG_DIS " +
    "I2C_SLV1_GRP I2C_SLV1_LEN:4", 0x2A)

I2C_SLV2_ADDR = Register("I2C_SLV2_RW I2C_SLV2_ADDR:7", 0x2B)
I2C_SLV2_REG = Register("I2C_SLV2_REG:8", 0x2C)
I2C_SLV2_CTRL = Register(
    "I2C_SLV2_EN I2C_SLV2_BYTE_SW I2C_SLV2_REG_DIS " +
    "I2C_SLV2_GRP I2C_SLV2_LEN:4", 0x2D)

I2C_SLV3_ADDR = Register("I2C_SLV3_RW I2C_SLV3_ADDR:7", 0x2E)
I2C_SLV3_REG = Register("I2C_SLV3_REG:8", 0x2F)
I2C_SLV3_CTRL = Register(
    "I2C_SLV3_EN I2C_SLV3_BYTE_SW I2C_SLV3_REG_DIS " +
    "I2C_SLV3_GRP I2C_SLV3_LEN:4", 0x30)

I2C_SLV4_ADDR = Register("I2C_SLV4_RW I2C_SLV4_ADDR:7", 0x31)
I2C_SLV4_REG = Register("I2C_SLV4_REG:8", 0x32)
I2C_SLV4_DO = Register("I2C_SLV4_DO:8", 0x33)
I2C_SLV4_CTRL = Register(
    "I2C_SLV4_EN I2C_SLV4_INT_EN I2C_SLV4_REG_DIS I2C_MST_DLY:5", 0x34)
I2C_SLV4_DI = Register("I2C_SLV4_DI:8", 0x35)

I2C_MST_STATUS = Register(
    "PASS_THROUGH I2C_SLV4_DONE I2C_LOST_ARB I2C_SLV4_NACK " +
    "I2C_SLV3_NACK I2C_SLV2_NACK I2C_SLV1_NACK I2C_SLV0_NACK", 0x36)

INT_PIN_CFG = Register(
    "INT_LEVEL INT_OPEN LATCH_INT_EN INT_RD_CLEAR " +
    "FSYNC_INT_LEVEL FSYNC_INT_EN I2C_BYPASS_EN :", 0x37)
INT_ENABLE = Register(":3 FIFO_OFLOW_EN I2C_MST_INT_EN :2 DATA_RDY_EN", 0x38)
INT_STATUS = Register(":3 FIFO_OFLOW_INT I2C_MST_INT :2 DATA_RDY_EN", 0x3A)

ACCEL_XOUT_H = Register("ACCEL_XOUT:8", 0x3B)
ACCEL_XOUT_L = Register("ACCEL_XOUT:8", 0x3C)
ACCEL_YOUT_H = Register("ACCEL_YOUT:8", 0x3D)
ACCEL_YOUT_L = Register("ACCEL_YOUT:8", 0x3E)
ACCEL_ZOUT_H = Register("ACCEL_ZOUT:8", 0x3F)
ACCEL_ZOUT_L = Register("ACCEL_ZOUT:8", 0x40)

TEMP_OUT_H = Register("TEMP_OUT:8", 0x41)
TEMP_OUT_L = Register("TEMP_OUT:8", 0x42)

GYRO_XOUT_H = Register("GYRO_XOUT:8", 0x43)
GYRO_XOUT_L = Register("GYRO_XOUT:8", 0x44)
GYRO_YOUT_H = Register("GYRO_YOUT:8", 0x45)
GYRO_YOUT_L = Register("GYRO_YOUT:8", 0x46)
GYRO_ZOUT_H = Register("GYRO_ZOUT:8", 0x47)
GYRO_ZOUT_L = Register("GYRO_ZOUT:8", 0x48)

EXT_SENS_DATA_00 = Register("EXT_SENS_DATA_00:8", 0x49)
EXT_SENS_DATA_01 = Register("EXT_SENS_DATA_01:8", 0x4A)
EXT_SENS_DATA_02 = Register("EXT_SENS_DATA_02:8", 0x4B)
EXT_SENS_DATA_03 = Register("EXT_SENS_DATA_03:8", 0x4C)
EXT_SENS_DATA_04 = Register("EXT_SENS_DATA_04:8", 0x4D)
EXT_SENS_DATA_05 = Register("EXT_SENS_DATA_05:8", 0x4E)
EXT_SENS_DATA_06 = Register("EXT_SENS_DATA_06:8", 0x4F)
EXT_SENS_DATA_07 = Register("EXT_SENS_DATA_07:8", 0x50)
EXT_SENS_DATA_08 = Register("EXT_SENS_DATA_08:8", 0x51)
EXT_SENS_DATA_09 = Register("EXT_SENS_DATA_09:8", 0x52)
EXT_SENS_DATA_10 = Register("EXT_SENS_DATA_10:8", 0x53)
EXT_SENS_DATA_11 = Register("EXT_SENS_DATA_11:8", 0x54)
EXT_SENS_DATA_12 = Register("EXT_SENS_DATA_12:8", 0x55)
EXT_SENS_DATA_13 = Register("EXT_SENS_DATA_13:8", 0x56)
EXT_SENS_DATA_14 = Register("EXT_SENS_DATA_14:8", 0x57)
EXT_SENS_DATA_15 = Register("EXT_SENS_DATA_15:8", 0x58)
EXT_SENS_DATA_16 = Register("EXT_SENS_DATA_16:8", 0x59)
EXT_SENS_DATA_17 = Register("EXT_SENS_DATA_17:8", 0x5A)
EXT_SENS_DATA_18 = Register("EXT_SENS_DATA_18:8", 0x5B)
EXT_SENS_DATA_19 = Register("EXT_SENS_DATA_19:8", 0x5C)
EXT_SENS_DATA_20 = Register("EXT_SENS_DATA_20:8", 0x5D)
EXT_SENS_DATA_21 = Register("EXT_SENS_DATA_21:8", 0x5E)
EXT_SENS_DATA_22 = Register("EXT_SENS_DATA_22:8", 0x5F)
EXT_SENS_DATA_23 = Register("EXT_SENS_DATA_23:8", 0x60)

I2C_SLV0_DO = Register("I2C_SLV0_DO:8", 0x63)
I2C_SLV1_DO = Register("I2C_SLV1_DO:8", 0x64)
I2C_SLV2_DO = Register("I2C_SLV2_DO:8", 0x65)
I2C_SLV3_DO = Register("I2C_SLV3_DO:8", 0x66)

I2C_MST_DELAY_CTRL = Register(
    "DELAY_ES_SHADOW :2 I2C_SLV4_DLY_EN I2C_SLV3_DLY_EN " +
    "I2C_SLV2_DLY_EN I2C_SLV1_DLY_EN I2C_SLV0_DLY_EN", 0x67)

SIGNAL_PATH_RESET = Register(":5 GYRO_RESET ACCEL_RESET TMP_RESET", 0x68)
USER_CTRL = Register(
    ": FIFO_EN I2C_MST_EN I2C_IF_DIS : FIFO_RESET " + 
    "I2C_MST_RESET SIG_COND_RESET", 0x6A)

PWR_MGMT_1 = Register("DEVICE_RESET SLEEP CYCLE : TEMP_DIS CLKSEL:3", 0x6B)
PWR_MGMT_2 = Register(
    "LP_WAKE_CTRL:2 STBY_XA STBY_YA STBY_ZA STBG_XG STBY_YG STBY_ZG", 0x6C)

FIFO_COUNTH = Register("FIFO_COUNT:8", 0x72)
FIFO_COUNTL = Register("FIFO_COUNT:8", 0x73)
FIFO_R_W = Register("FIFO_DATA:8", 0x74)

WHO_AM_I = Register(": WHO_AM_I:6 :", 0x75)

######################################################################

class MPU6050(object):
    def __init__(self, i2c, address=0x68):
        self.i2c = i2c
        self.cfg = i2c.prepare(slaveAddress=address, isStopBit=1, isNakBit=1)

    def read(self, len=1):
        buf = "\x00" * len
        return self.i2c.read(self.cfg, buf)

    def write(self, data):
        return self.i2c.write(self.cfg, data)

    def get_reg(self, reg, len=1):
        self.write(pack('<B', reg))
        tmp = self.read(len)
        return reg(tmp) if isinstance(reg, Register) else tmp

    def set_reg(self, reg, *arg, **kw):
        tmp = reg(*arg, **kw).value
        return self.write(pack('<BB', reg, tmp.uint))

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

add_register(MPU6050)

# export symbols
__all__  = [i for i in list(locals()) if i.isupper()]
__all__ += [i for i in list(locals()) if i.startswith("MPU")]
