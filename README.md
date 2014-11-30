python-ucdev
============

Python library to access Cypress CY7C65211 USB-to-GPIO/SPI/I2C chip.
Also includes library to access Nordic nRF24L01 wireless tranceiver
over (USB-to-)SPI interface.

## Note
This requires cyusbserial.dll (or libcyusbserial.so) library
provided by Cypress.

## Usage

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

Current development focuses on GPIO and SPI feature to use Nordic
nRF24 wireless tranceiver chip. See sample script nrf24-test.py for the detail.
