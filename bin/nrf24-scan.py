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

    rf.reset(MODE_SB|DIR_RECV)
    rf.RX_ADDR_P0 = int(ctx.opt.addr, 16)
    rf.RF_CH      = ctx.opt.freq - 2400

    # disable CRC
    rf.CONFIG.EN_CRC = 1

    # set datarate
    if ctx.opt.rate == 2000:
        rf.RF_SETUP.RF_DR = 1
    elif ctx.opt.rate == 1000:
        rf.RF_SETUP.RF_DR = 0

    #
    # pseudo promisc mode
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
    rf.SETUP_AW.AW = 0x00

    # recv loop
    while True:
        rc, buf = rf.recv(32)
        if not buf: continue

        if ctx.opt.dump == 'mac':
            print("".join(map(lambda v: "%02X" % v, buf[0:5])))
        elif ctx.opt.dump == 'hex':
            print("".join(map(lambda v: "%02X" % v, buf)))
        else:
            sys.stdout.write(buf)

if __name__ == '__main__' and '__file__' in globals():
    ap = ArgumentParser()
    ap.add_argument('-L', '--log', metavar='LV',  default='DEBUG')
    ap.add_argument('-v', '--vid', metavar='VID', default='0x04b4')
    ap.add_argument('-p', '--pid', metavar='PID', default='0x0004')
    ap.add_argument('-n', '--nth', metavar='N', type=int)
    ap.add_argument('-d', '--dump', default='raw')
    ap.add_argument('-a', '--addr', metavar='ADDR', default='0x00AA00AA00')
    ap.add_argument('-f', '--freq', metavar='FREQ', type=int, default=2405)
    ap.add_argument('-r', '--rate', metavar='RATE', type=int)
    ap.add_argument('args', nargs='*')

    # parse args
    ctx = lambda:0
    ctx.opt = ap.parse_args()

    # setup logger
    logging.basicConfig(level=eval('logging.' + ctx.opt.log))

    main(ctx)
