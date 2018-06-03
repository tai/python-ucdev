#!/usr/bin/env python
# -*- coding: utf-8 -*-

usage = """
nRF24 sniffer

ref:
- http://yveaux.blogspot.jp/2014/07/nrf24l01-sniffer-part-1.html
- https://github.com/Yveaux/NRF24_Sniffer/

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
    rf.RF_CH = ctx.opt.freq - 2400

    #
    # configure promisc mode
    #
    # While 0x00 is unofficial, it is known to enable "2-byte address
    # match" mode. With this configuration, it is now possible to
    # sniff all nRF24 packet with 2-byte RX_ADDR 0x0055. This is because
    # nRF24 uses radio preamble of 0xAA or 0x55 and default background
    # tends to generate 0x00 byte in the air.
    #
    # Right after radio preamble, nRF24 uses MAC address as a SYNC pattern.
    # This means sniffing allows you to capture MAC address in payload.
    #
    # ref:
    # - http://travisgoodspeed.blogspot.jp/2011/02/promiscuity-is-nrf24l01s-duty.html
    #
    rf.SETUP_AW.AW = max(0, ctx.opt.match - 2)

    #
    # disable CRC
    #
    # In this fake "promisc mode", CRC will never match as we are only
    # matching against part of incoming MAC address (as part of SYNC frame),
    # making CRC computed with remaining part of MAC as payload.
    #
    rf.CONFIG.EN_CRC = 0

    # recv loop
    while True:
        rc, buf = rf.recv(32)
        if not buf: continue

        if ctx.opt.dump == 'mac':
            print("".join(map(lambda v: "%02X" % v, buf[0:5])))
        elif ctx.opt.dump == 'hex':
            print("".join(map(lambda v: "%02X" % v, buf)))
        elif ctx.opt.dump == 'ascii':
            print("".join(map(lambda v: chr(v) if (0x20 < v and v < 0x7e) else ' ', buf)))
        else:
            sys.stdout.write(buf)

def to_int(v):
    return int(v, 0)

if __name__ == '__main__' and '__file__' in globals():
    ap = ArgumentParser()
    ap.add_argument('-D', '--debug', default='INFO')
    ap.add_argument('-V', '--vid', type=to_int, default=0x04b4)
    ap.add_argument('-P', '--pid', type=to_int, default=0x0004)
    ap.add_argument('-n', '--nth', type=int)
    ap.add_argument('-R', '--rx', action='append', type=to_int, default=[])
    ap.add_argument('-M', '--match', type=int, default=2)
    ap.add_argument('-f', '--freq', metavar='FREQ', type=int, default=2405)
    ap.add_argument('-m', '--mode', default='SB')
    ap.add_argument('-r', '--rate')
    ap.add_argument('-d', '--dump', default='raw')
    ap.add_argument('args', nargs='*')

    # parse args
    ctx = lambda:0
    ctx.opt = ap.parse_args()

    # default address(es)
    if len(ctx.opt.rx) == 0: ctx.opt.rx.append(0x0055)
    if len(ctx.opt.rx) == 1: ctx.opt.rx.append(ctx.opt.rx[0])

    # setup logger
    logging.basicConfig(level=eval('logging.' + ctx.opt.debug))

    main(ctx)
