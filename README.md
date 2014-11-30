python-ucdev
============

Python library to access Cypress CY7C65211 USB-to-GPIO/SPI/I2C chip.
Also includes library to access Nordic nRF24L01 wireless tranceiver
over (USB-to-)SPI interface.

## Usage (CY7C65211)

    >>> from cy7c65211 import CyUSBSerial, CyGPIO, CySPI
    >>> 
    >>> # load DLL provided by Cypress
    >>> dll = "c:/path/to/Cypress-USB-Serial/library/lib/cyusbserial.dll"
    >>> lib = CyUSBSerial(lib = dll)
    >>>
    >>> # use first device found
    >>> dev = lib.find().next()
    >>>
    >>> # access GPIO
    >>> gpio = CyGPIO(dev)
    >>> gpio.set(3, 1)
    >>> ret = gpio.get(3)
    >>>
    >>> # access each GPIO pin
    >>> pin = gpio.pin(3)
    >>> pin.set(1)
    >>> ret = pin.get()
    >>>
    >>> # access SPI
    >>> spi = CySPI(dev)
    >>> ret = spi.send("any-data-to-be-clocked-out")

## Usage (nRF24L01)

    >>> from nrf24 import *
    >>> 
    >>> tx = nRF24(CySPI(dev), CE=CyGPIO(dev).pin(0))
    >>> tx.reset(MODE_SB|DIR_SEND)
    >>> tx.TX_ADDR = tx.RX_ADDR_P0 = 0xB3B4B5B6C2
    >>> tx.send("some-payload-len-of-max-32-bytes")
    >>>
    >>> print tx.FIFO_STATUS.TX_EMPTY
    >>> print tx.CONFIG

## Note
This requires cyusbserial.dll (or libcyusbserial.so) library
provided by Cypress.

Current development focuses on GPIO and SPI features to
use Nordic nRF24 wireless tranceiver chip. See sample script
nrf24-test.py for the detail.
