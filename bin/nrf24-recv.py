#!/usr/bin/env python
# -*- coding: utf-8-unix -*-

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

import os
import sys
import time

from argparse import ArgumentParser
from ucdev.cy7c65211 import CyUSBSerial, CyGPIO, CySPI
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

    # set basic mode
    mode  = DIR_RECV
    mode |= eval("MODE_%s" % ctx.opt.mode.upper())
    if ctx.opt.rate:
        mode |= eval("RATE_%s" % ctx.opt.rate.upper())
    rf.reset(mode)

    # set address and channel
    for i,addr in enumerate(ctx.opt.rx):
        log.debug("RX_ADDR_P{i}: {addr:010X}".format(**locals()))
        setattr(rf, "RX_ADDR_P" + str(i), addr)
    if ctx.opt.tx:
        log.debug("TX_ADDR: {ctx.opt.tx:010X}".format(**locals()))
        rf.TX_ADDR = ctx.opt.tx
    rf.RF_CH   = ctx.opt.freq - 2400

    # recv loop
    while True:
        rc, buf = rf.recv()
        if rc and rc.RX_DR and buf:
            sys.stdout.write(buf)

def to_int(v):
    return int(v, 0)

if __name__ == '__main__' and '__file__' in globals():
    ap = ArgumentParser()
    ap.add_argument('-D', '--debug', default='INFO')
    ap.add_argument('-V', '--vid', type=to_int, default=0x04b4)
    ap.add_argument('-P', '--pid', type=to_int, default=0x0004)
    ap.add_argument('-n', '--nth', type=int)
    ap.add_argument('-T', '--tx', type=to_int)
    ap.add_argument('-R', '--rx', action='append', type=to_int, default=[])
    ap.add_argument('-f', '--freq', type=int, default=2405)
    ap.add_argument('-m', '--mode', default='SB')
    ap.add_argument('-r', '--rate')
    ap.add_argument('args', nargs='*')

    # parse args
    ctx = lambda:0
    ctx.opt = ap.parse_args()

    # default RX address(es)
    if len(ctx.opt.rx) == 0:
        ctx.opt.rx = [0xE7E7E7E7E7]
    if len(ctx.opt.rx) == 1 and ctx.opt.mode == 'ESB':
        # NOTE:
        # I had to set RX addr in RX_ADDR_P1, not P0.
        # It seems ESB mode expects P0 to have same address as TX_ADDR to
        # receive Auto-ACK, although it's only used by ESB TX node.
        ctx.opt.rx = [0, ctx.opt.rx[0]]

    # setup logger
    logging.basicConfig(level=eval('logging.' + ctx.opt.debug))

    main(ctx)
