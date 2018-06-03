python-ucdev
============

Python library to access Cypress CY7C6521x (CY7C65211, CY7C65213, or CY7C65215) USB-Serial bridge (USB to UART/I2C/SPI/GPIO) chip.
Also includes library to access various chips over I2C/SPI. Currently includes driver for

- Nordic nRF24L01 wireless tranceiver (SPI)
- InvenSense MPU-6050 3-axis accelerometer + 3-axis gyroscope (I2C)
- Honeywell HMC5883L 3-axis magnetometer (I2C)
- Si4702 FM radio receiver (I2C for now, additional SPI-mode ongoing)

## Usage (CY7C6521x)

    >>> from ucdev.cy7c65211 import CyUSBSerial, CyGPIO, CySPI
    >>> 
    >>> # load DLL provided by Cypress
    >>> lib = CyUSBSerial(lib="cyusbserial")
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

    >>> from ucdev.nrf24 import *
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
use Nordic nRF24 wireless tranceiver chip. See sample scripts
under bin/ folder for the detail.
