#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function

import os
import sys
import time

from struct import pack, unpack
from argparse import ArgumentParser

from ucdev.cy7c65211 import CyUSBSerial, CyI2C
from ucdev.mpu6050 import *

from IPython import embed

import logging
log = logging.getLogger(__name__)

def find_dev(ctx):
    #dll = "c:/app/Cypress/Cypress-USB-Serial/library/lib/cyusbserial.dll"
    dll = os.getenv("CYUSBSERIAL_DLL") or "cyusbserial"
    lib = CyUSBSerial(lib=dll)
    found = list(lib.find(vid=ctx.opt.vid, pid=ctx.opt.pid))
    return found[ctx.opt.nth]

def main(ctx):
    dev = find_dev(ctx)
    i2c = CyI2C(dev)
    mpu = MPU6050(i2c, address=ctx.opt.addr)

    print(mpu.WHO_AM_I)
    print(mpu.PWR_MGMT_1)

    # powerup
    mpu.PWR_MGMT_1.SLEEP = 0

    # dump accel data for some time
    for i in range(ctx.opt.time * 10):
        print(mpu.ACCEL_XOUT_H)
        time.sleep(0.1)
    print("=== Data dump done. Entering IPython ===")

    embed()

def to_int(v):
    return int(v, 0)

if __name__ == '__main__' and '__file__' in globals():
    ap = ArgumentParser()
    ap.add_argument('-D', '--debug', default='INFO')
    ap.add_argument('-V', '--vid', type=to_int, default=0x04b4)
    ap.add_argument('-P', '--pid', type=to_int, default=0x0004)
    ap.add_argument('-A', '--addr', type=to_int, default=0x68)
    ap.add_argument('-n', '--nth', type=int, default=0)
    ap.add_argument('-t', '--time', type=int, default=1)
    ap.add_argument('args', nargs='*')

    # parse args
    ctx = lambda:0
    ctx.opt = ap.parse_args()

    # setup logger
    logging.basicConfig(level=eval('logging.' + ctx.opt.debug))

    main(ctx)

