#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function

import os
import sys
import time

from struct import pack, unpack
from argparse import ArgumentParser

from ucdev.cy7c65211 import CyUSBSerial, CyI2C
from ucdev.si4702 import *

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
    si = SI4702(i2c)

    # enable internal oscillator before powerup
    si.TEST1.XOSCEN = 1
    time.sleep(0.5)

    # clear RDS data (see errata)
    si.RDSD = 0x0000

    # power on
    si.POWERCFG = POWERCFG(ENABLE=1, DISABLE=0)
    time.sleep(0.1)

    print(si.DEVICEID)
    print(si.CHIPID)

    # set region to Japan, and maximize volume
    si.SYSCONFIG2 = SYSCONFIG2(BAND=0b01, SPACE=0b01, VOLUME=0xF)

    # NOTE:
    # Freq = SPACE * CHAN + Limit, where:
    # - Limit = 76MHz if BAND=0b01
    # - SPACE = 0.1MHz if SPACE=0b01
    si.CHANNEL = CHANNEL(TUNE=1, CHAN=int((ctx.opt.freq - 76.0) / 0.1))

    # STC bit gets set after SEEK=1 or TUNE=1 operation starts.
    # It must be cleared by having both SEEK=0 and TUNE=0.
    while not si.STATUSRSSI.STC:
        time.sleep(0.1)
    si.CHANNEL.TUNE = 0

    # disable mute
    si.POWERCFG.DMUTE = 1

    embed()

def to_int(v):
    return int(v, 0)

if __name__ == '__main__' and '__file__' in globals():
    ap = ArgumentParser()
    ap.add_argument('-D', '--debug', default='INFO')
    ap.add_argument('-V', '--vid', type=to_int, default=0x04b4)
    ap.add_argument('-P', '--pid', type=to_int, default=0x0004)
    ap.add_argument('-n', '--nth', type=int, default=0)
    ap.add_argument('-f', '--freq', type=float, default=80.0)
    ap.add_argument('args', nargs='*')

    # parse args
    ctx = lambda:0
    ctx.opt = ap.parse_args()

    # setup logger
    logging.basicConfig(level=eval('logging.' + ctx.opt.debug))

    main(ctx)

