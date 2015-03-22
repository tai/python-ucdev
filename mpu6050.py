#!/bin/env python
# -*- coding: utf-8 -*-

from bitstring import *

# MPU-6050 registers
SELF_TEST_X = 13
SELF_TEST_Y = 14
SELF_TEST_Z = 15
SELF_TEST_A = 16

SMPRT_DIV = 25
CONFIG = 26
GYRO_CONFIG = 27
ACCEL_CONFIG = 28
FIFO_EN = 35
I2C_MST_CTRL = 36

I2C_SLV0_ADDR = 37
I2C_SLV0_REG  = 38
I2C_SLV0_CTRL = 39

I2C_SLV1_ADDR = 40
I2C_SLV1_REG  = 41
I2C_SLV1_CTRL = 42

I2C_SLV2_ADDR = 43
I2C_SLV2_REG  = 44
I2C_SLV2_CTRL = 45

I2C_SLV3_ADDR = 46
I2C_SLV3_REG  = 47
I2C_SLV3_CTRL = 48

I2C_SLV4_ADDR = 49
I2C_SLV4_REG  = 50
I2C_SLV4_DO   = 51
I2C_SLV4_CTRL = 52
I2C_SLV4_DI   = 53

I2C_MST_STATUS = 54

INT_PIN_CFG = 55
INT_ENABLE = 56
INT_STATUS = 58

ACCEL_XOUT_H = 59
ACCEL_XOUT_L = 60
ACCEL_YOUT_H = 61
ACCEL_YOUT_L = 62
ACCEL_ZOUT_H = 63
ACCEL_ZOUT_L = 64

TEMP_OUT_H = 65
TEMP_OUT_L = 66

GYRO_XOUT_H = 67
GYRO_XOUT_L = 68
GYRO_YOUT_H = 69
GYRO_YOUT_L = 70
GYRO_ZOUT_H = 71
GYRO_ZOUT_L = 72

EXT_SENS_DATA_00 = 73
EXT_SENS_DATA_01 = 74
EXT_SENS_DATA_02 = 75
EXT_SENS_DATA_03 = 76
EXT_SENS_DATA_04 = 77
EXT_SENS_DATA_05 = 78

EXT_SENS_DATA_06 = 79
EXT_SENS_DATA_07 = 80
EXT_SENS_DATA_08 = 81
EXT_SENS_DATA_09 = 82
EXT_SENS_DATA_10 = 83
EXT_SENS_DATA_11 = 84

EXT_SENS_DATA_12 = 85
EXT_SENS_DATA_13 = 86
EXT_SENS_DATA_14 = 87
EXT_SENS_DATA_15 = 88
EXT_SENS_DATA_16 = 89
EXT_SENS_DATA_17 = 90

EXT_SENS_DATA_18 = 91
EXT_SENS_DATA_19 = 92
EXT_SENS_DATA_20 = 93
EXT_SENS_DATA_21 = 94
EXT_SENS_DATA_22 = 95
EXT_SENS_DATA_23 = 96

I2C_SLV0_DO = 99
I2C_SLV1_DO = 100
I2C_SLV2_DO = 101
I2C_SLV3_DO = 102

I2C_MST_DELAY_CTRL = 103
SIGNAL_PATH_RESET = 104
USER_CTRL = 106

PWR_MGMT_1 = 107
PWR_MGMT_2 = 108

FIFO_COUNT_H = 114
FIFO_COUNT_L = 115
FIFO_R_W = 116

WHO_AM_I = 117

class ValueObject():
    pass

class MPU6050():
    def __init__(self, i2c, address=0x68):
        self.i2c = i2c
        self.cfg = i2c.prepare(slaveAddress=address, isStopBit=1, isNakBit=1)

    def read(self, len=1):
        buf = "\x00" * len
        return self.i2c.read(self.cfg, buf)

    def write(self, data):
        return self.i2c.write(self.cfg, data)

    def get_reg(self, reg, len=1):
        self.write(pack('<B', reg).bytes)
        return self.read(len)

    def set_reg(self, reg, val):
        return self.write(pack('<BB', reg, val).bytes)

