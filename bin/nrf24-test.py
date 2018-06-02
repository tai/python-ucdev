#!/usr/bin/env python
# -*- coding: utf-8 -*-

usage = """
nRF24 test carrier wave

To run and test this script, connection betwen CY7C65211 and nRF24L01
must be done as below:

Cypress       nRF24L01
----------------------
 GPIO 0 <---> CE
 GPIO 1 <---> IRQ
   SSEL <---> CSN
   MISO <---> MO
   MOSI <---> MI
   SCLK <---> SCK

"""

import os
import sys
import time

from argparse import ArgumentParser
from ucdev.cy7c65211 import *
from ucdev.nrf24 import *

import logging
log = logging.getLogger(__name__)

from IPython import embed

def find_dev(ctx):
    dll = os.getenv("CYUSBSERIAL_DLL") or "cyusbserial"
    lib = CyUSBSerial(lib=dll)
    found = list(lib.find(vid=ctx.opt.vid, pid=ctx.opt.pid))
    return found[ctx.opt.nth]

def main(ctx):
    dev = find_dev(ctx)
    io = CyGPIO(dev)
    rf = nRF24(CySPI(dev), CE=io.pin(0), IRQ=io.pin(1))

    # set carrier wave test mode
    rf.reset(MODE_TEST)

    log.info("Carrier wave at {ctx.opt.freq}[MHz]".format(**locals()))
    rf.RF_CH = ctx.opt.freq - 2400
    rf.CE = 1

    # loop
    while True:
        sys.stdout.write('.')
        sys.stdout.flush()
        time.sleep(1)

def to_int(v):
    return int(v, 0)

if __name__ == '__main__' and '__file__' in globals():
    ap = ArgumentParser()
    ap.add_argument('-D', '--debug', default='INFO')
    ap.add_argument('-V', '--vid', type=to_int, default=0x04b4)
    ap.add_argument('-P', '--pid', type=to_int, default=0x0004)
    ap.add_argument('-n', '--nth', type=int)
    ap.add_argument('-f', '--freq', type=int, default=2405)
    ap.add_argument('args', nargs='*')

    # parse args
    ctx = lambda:0
    ctx.opt = ap.parse_args()

    # setup logger
    logging.basicConfig(level=eval('logging.' + ctx.opt.debug))

    main(ctx)
