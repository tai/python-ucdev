#!/usr/bin/env python
# -*- coding: utf-8 -*-

usage = """
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

import sys
import time

from argparse import ArgumentParser
from cy7c65211 import *
from nrf24 import *

import logging
log = logging.getLogger(__name__)

from IPython import embed

def main(ctx):
    dll = "cyusbserial"
    lib = CyUSBSerial(lib = dll)

    # find device
    found = list(lib.find(vid=int(ctx.opt.vid, 16), pid=int(ctx.opt.pid, 16)))

    if len(found) < 1:
        log.warn("No device found.")
        sys.exit(1)
    elif len(found) > 1 and ctx.opt.nth is None:
        log.warn("Found multiple devices. Use --nth option to specify one.")
        sys.exit(1)
    dev = found[ctx.opt.nth if ctx.opt.nth else 0]

    # setup
    io = CyGPIO(dev)
    rf = nRF24(CySPI(dev), CE=io.pin(0), IRQ=io.pin(1))

    rf.reset(MODE_ESB|DIR_SEND)
    rf.TX_ADDR    = int(ctx.opt.addr, 16)
    rf.RX_ADDR_P0 = int(ctx.opt.addr, 16)
    rf.RF_CH      = ctx.opt.freq - 2400

    # send loop
    buf = sys.stdin.read(32)
    while buf is not None:
        if buf:
            while not rf.FIFO_STATUS.TX_EMPTY:
                rf.flush()
                time.sleep(0.01)
            rf.send(buf)
        buf = sys.stdin.read(32)

if __name__ == '__main__' and '__file__' in globals():
    ap = ArgumentParser()
    ap.add_argument('--log', metavar='LV',  default='DEBUG')
    ap.add_argument('--vid', metavar='VID', default='0x04b4')
    ap.add_argument('--pid', metavar='PID', default='0x0004')
    ap.add_argument('--nth', metavar='N', type=int)
    ap.add_argument('--addr', metavar='ADDR', default='0xB3B4B5B6C2')
    ap.add_argument('--freq', metavar='FREQ', type=int, default=2405)
    ap.add_argument('args', nargs='*')

    # parse args
    ctx = lambda:0
    ctx.opt = ap.parse_args()

    # setup logger
    logging.basicConfig(level=eval('logging.' + ctx.opt.log))

    main(ctx)
