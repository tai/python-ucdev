#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
To run and test this script, you must have 2 sets of CY7C65211+nRF24L01
pairs. One is used as a transmitter, and another is used as a receiver.

Connection betwen CY7C65211 and nRF24L01 must be done as below:

Cypress       nRF24L01
----------------------
 GPIO 0 <---> CE
 GPIO 1 <---> IRQ
   SSEL <---> CSN
   MISO <---> MO
   MOSI <---> MI
   SCLK <---> SCK

"""

from __future__ import print_function

import sys, os
import time
from threading import *
from IPython import embed

from cy7c65211 import *
from nrf24 import *

##
## Test to make nRF24 run under test mode, which continuously
## generate carrier signal.
##
def carrier(tx, seconds=3, freq=2405):
    tx.reset(MODE_TEST)
    tx.RF_CH = freq - 2400

    t0 = time.time()
    td = 0
    while seconds <= 0 or td < seconds:
        tx.send()
        td = time.time() - t0

##
## Test to run one-time only send/recv test
##
def pingpong(rx, tx, msg):
    tx.send(msg.ljust(32))
    time.sleep(1)
    got = rx.recv()
    print("RX:", got)

##
## Test to run multithreaded send/recv test
##
def pingpong_th(rx, tx, msg):
    def run_rx(rx):
        rx.quit = False
        while not rx.quit:
            while rx.FIFO_STATUS.RX_EMPTY and not rx.quit:
                time.sleep(1)

            got = rx.recv()
            if got:
                print("RX:", got)

    def run_tx(tx):
        count = 3
        while count > 0:
            count -= 1
            time.sleep(1)
            if tx.FIFO_STATUS.TX_EMPTY:
                tx.send(msg.ljust(32))
            else:
                tx.flush()

    rt = Thread(target=run_rx, args=(rx,))
    rt.start()

    st = Thread(target=run_tx, args=(tx,))
    st.start()

    st.join

##
## Initialize devices as transmitter/receiver.
##
def init(rx, tx, pipe=0xB3B4B5B6C3, freq=2405):
    tx.reset(MODE_ESB|DIR_SEND)
    rx.reset(MODE_ESB|DIR_RECV)

    tx.TX_ADDR    = pipe
    tx.RX_ADDR_P0 = pipe
    rx.RX_ADDR_P1 = pipe

    tx.RF_CH = rx.RF_CH = freq - 2400
    print("Using F0 ={0}Mhz".format(freq))

######################################################################

#dll = "c:/app/Cypress/Cypress-USB-Serial/library/lib/cyusbserial.dll"
dll = "cyusbserial"
lib = CyUSBSerial(lib = dll)

rxd, txd = list(lib.find(vid=0x04b4))

rp = CyGPIO(rxd)
tp = CyGPIO(txd)
rx = nRF24(CySPI(rxd), CE=rp.pin(0), IRQ=rp.pin(1))
tx = nRF24(CySPI(txd), CE=tp.pin(0), IRQ=tp.pin(1))

## Initialize devices with given MAC
init(rx, tx, pipe=0xB3B4B5B6C2)

## data to send/recv
msg = "hello, nrf24"

#carrier(tx)
#pingpong(rx, tx, msg)
pingpong_th(rx, tx, msg)

embed()
