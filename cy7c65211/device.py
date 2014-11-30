# -*- coding: utf-8 -*-

import sys, os
import platform
from cffi import FFI

import header
from common import *

class CyUSBSerial(object):
    __self = None

    def __new__(cls, lib=None, ffi=None):
        if not cls.__self:
            if not ffi:
                ffi = FFI()
            obj = super(CyUSBSerial, cls).__new__(cls)
            obj.ffi = ffi
            obj.ffi.cdef(header.src)
            obj.api = ffi.dlopen(lib if lib else "cyusbserial")

            # initialize if API exists
            if hasattr(obj.api, 'CyLibraryInit'):
                rc = obj.api.CyLibraryInit()
                if rc != obj.api.CY_SUCCESS:
                    raise Exception("ERROR: CyLibraryInit=%d" % rc)

            cls.__self = obj
        return cls.__self

    def __del__(self):
        # finalize if API exists
        if self.api and hasattr(self.api, 'CyLibraryExit'):
            self.api.CyLibraryExit()

    def find(self, finder=None, vid=None, pid=None):
        ffi, api = self.ffi, self.api

        os = platform.system()
        nr = ffi.new("UINT8 *")
        rc = api.CyGetListofDevices(nr)

        info = ffi.new("CY_DEVICE_INFO *")

        for devno in range(0, nr[0]):
            rc = api.CyGetDeviceInfo(devno, info)

            if os == 'Windows' and info.deviceBlock != api.SerialBlock_SCB0:
                continue

            found = True

            if finder:
                found = finder(info)
            elif vid or pid:
                iv = info.vidPid.vid
                ip = info.vidPid.pid

                found = (vid, pid) in ((iv, ip), (iv, None), (None, ip))

            if found:
                yield CyUSBSerialDevice(self, devno, 0)

######################################################################

class CyUSBSerialDevice(object):
    def __init__(self, lib, devno, ifnum):
        self.lib   = lib
        self.devno = devno
        self.ifnum = ifnum
        self.dev   = None

        self.raise_on_error = True

        # import API symbols from the library
        dummy = self.CY_SUCCESS
        self.__dict__.update(lib.api.__dict__)

    # delegate API calls to the library
    def __getattr__(self, key):
        lib, api = self.lib, self.lib.api
        val = getattr(api, key)

        # wrap API so device handle is handled automatically
        if callable(val):
            def wrap(self, name, func):
                def wrapper(*args, **kwargs):
                    # automatically open handle on first call
                    if not self.dev:
                        self.open()

                    # delegate API call
                    rc = func(self.dev, *args, **kwargs)

                    if self.raise_on_error and rc != api.CY_SUCCESS:
                        sym = self.err_to_sym(rc)
                        msg = "ERROR: {0}={1}, {2}".format(name, rc, sym)
                        raise Exception(msg)

                    # invalidate handle to force reopen on next call
                    elif name in ('CyCyclePort', 'CyResetDevice'):
                        self.dev = None

                    return rc
                return wrapper
            val = wrap(self, key, val)

        # save as local attribute to help ipython completion
        setattr(self, key, val)

        return val

    def __del__(self, *args):
        self.close()

    def err_to_sym(self, rc):
        for k, v in vars(self.lib.api).items():
            if k.startswith("CY_ERROR") and v == rc:
                return k
        return "UNKNOWN"

    def open(self):
        lib, ffi, api = self.lib, self.lib.ffi, self.lib.api
        rc = api.CY_SUCCESS
        if not self.dev:
            dev = ffi.new("CY_HANDLE *")
            rc  = api.CyOpen(self.devno, self.ifnum, dev)
            self.dev = dev[0]
        return rc

    def close(self):
        lib, ffi, api = self.lib, self.lib.ffi, self.lib.api
        if self.dev:
            api.CyClose(self.dev)
            self.dev = None

######################################################################

class CySPI(SPI):
    MOTOROLA = TI = NS = None

    # Used for GPIO-based chip-select
    CSN = property(lambda s:s.__csn.get() if s.__csn else None,
                   lambda s,v:s.__csn.set(1 if v else 0) if s.__csn else None)

    def __init__(self, dev, CSN=None):
        if not isinstance(dev, CyUSBSerialDevice):
            msg = "ERROR: Not a CyUSBSerialDevice object: %s" % str(dev)
            raise Exception(msg)
        self.dev = dev
        self.__csn = CSN
        self.debug = False

        # FIXME:
        # - These should be set on load-time, not run-time.
        CySPI.MOTOROLA = dev.lib.api.CY_SPI_MOTOROLA
        CySPI.TI       = dev.lib.api.CY_SPI_TI
        CySPI.NS       = dev.lib.api.CY_SPI_NS

    def set_config(self, config):
        dev = self.dev
        ffi = dev.lib.ffi
        api = dev.lib.api
        cfg = ffi.new("CY_SPI_CONFIG *", config)
        return dev.CySetSpiConfig(cfg)

    def get_config(self):
        dev = self.dev
        ffi = dev.lib.ffi
        api = dev.lib.api

        cfg = ffi.new("CY_SPI_CONFIG *")
        rc  = dev.CyGetSpiConfig(cfg)
        if rc != api.CY_SUCCESS:
            raise Exception("ERROR: CyGetSpiConfig=%d" % rc)

        ret = {}
        for k, v in ffi.typeof(cfg[0]).fields:
            ret[k] = getattr(cfg, k)
        return ret

    def send(self, data, timeout=1000):
        dev = self.dev
        ffi = dev.lib.ffi

        wlen = len(data)
        wbuf = ffi.new("UCHAR[%d]" % wlen, str(data))
        wcdb = ffi.new("CY_DATA_BUFFER *", (wbuf, wlen, 0))

        rlen = len(data)
        rbuf = ffi.new("UCHAR[%d]" % rlen)
        rcdb = ffi.new("CY_DATA_BUFFER *", (rbuf, rlen, 0))

        if self.debug:
            print "w:", " ".join(["{:08b}".format(i) for i in wbuf])

        self.CSN = 1
        rc = dev.CySpiReadWrite(rcdb, wcdb, timeout)
        self.CSN = 0

        if self.debug:
            print "r:", " ".join(["{:08b}".format(i) for i in rbuf])

        return bytearray(ffi.buffer(rcdb.buffer, rcdb.transferCount)[0:])

######################################################################

class CyGPIO(GPIO):
    def __init__(self, dev):
        if not isinstance(dev, CyUSBSerialDevice):
            msg = "ERROR: Not a CyUSBSerialDevice object: %s" % str(dev)
            raise Exception(msg)
        self.dev = dev

    def set(self, pin, val):
        dev = self.dev
        api = dev.lib.api

        ret = dev.CySetGpioValue(pin, val)
        if ret != api.CY_SUCCESS:
            sym = dev.err_to_sym(ret)
            msg = "ERROR: CySetGpioValue={0}, {1}".format(ret, sym)
            raise Exception(msg)

    def get(self, pin):
        dev = self.dev
        api = dev.lib.api
        ffi = dev.lib.ffi

        val = ffi.new("UINT8 *")
        ret = dev.CyGetGpioValue(pin, val)
        if ret != api.CY_SUCCESS:
            sym = dev.err_to_sym(ret)
            msg = "ERROR: CyGetGpioValue={0}, {1]".format(ret, sym)
            raise Exception(msg)
        return val[0]

######################################################################

__all__ = []
for k,v in locals().items():
    if hasattr(v, '__module__') and v.__module__ == __name__:
        __all__.append(k)
