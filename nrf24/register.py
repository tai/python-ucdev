#!/bin/env python
# -*- coding: utf-8 -*-

"""
FOO = Register("A:4 B:4", 0x12)
BAR = Register("B:4 C:4", 0x23)

# evals as int which is a register address
print FOO == 0x12
# each field attribute returns a mask for that field
print FOO.B == 0b00001111
print BAR.B == 0b11110000

# ERROR: Register definition is readonly
FOO.B = 0b10101010

# creates register instance with initial value
foo = FOO(0xAC)
print foo.A == 0xA
print foo.B == 0xC
print foo == 0xAC
foo.B = 0
print foo == 0xA0
"""
import sys, os
from bitstring import Bits, BitArray

"""
Convert various typed values into BitArray value.
"""
def to_bits(val, bitlen):
    if isinstance(val, str) or isinstance(val, bytearray):
        return Bits(bytes=val, length=bitlen)
    elif isinstance(val, Bits):
        return Bits(bytes=val.bytes, length=bitlen)
    elif isinstance(val, RegisterValue):
        return Bits(bytes=val.value.bytes, length=bitlen)
    return Bits(uint=val, length=bitlen)

"""
Installs filter function to limit access to non-existing attribute.

NOTE:
This replaces belonging class of passed object to dynamically
generated subclass of the original class.
"""
def protect_object(obj):
    sub = type("Protected" + type(obj).__name__, (type(obj),), {})

    fset = sub.__setattr__
    def fset_wrap(self, key, val):
        if not hasattr(self, key):
            raise AttributeError("Access denied for key: %s" % key)
        return fset(self, key, val)
    sub.__setattr__ = fset_wrap

    obj.__class__ = sub

"""
Generic class to wrap built-in types with custom attributes.
"""
class Value(object):
    def __new__(cls, arg, **kw):
        return type(cls.__name__, (type(arg), cls, ), kw)(arg)

class Field(Bits):
    # NOTE:
    # Subclassing bitstring.* is a pain, so I'll just workaround it
    # by a factory method.
    @classmethod
    def create(cls, value, masklen, bitlen, offset):
        field = Bits.__new__(cls, uint=value, length=masklen)
        field.__offset = offset
        field.__bitlen = bitlen
        return field

    @property
    def offset(self):
        return self.__offset

    @property
    def bitlen(self):
        return self.__bitlen

class Register(int):
    def __new__(cls, desc, address):
        r_fields = []
        r_bitlen = 0

        # parse register description
        for f in desc.split():
            # expected: f in (":", "HOGE", "HOGE:123", ":123")
            pair = f.split(":")
            if len(pair) == 2:
                f_name, f_bitlen = pair[0], int(pair[1]) if pair[1] else 1
            else:
                f_name, f_bitlen = pair[0], 1

            r_fields.append((f_name, f_bitlen))
            r_bitlen += f_bitlen

        # returns bitmask implemented as readonly property
        def makeprop(r_bitlen, f_bitlen, f_offset):
            value = ((1 << f_bitlen) - 1) << f_offset
            field = Field.create(value, r_bitlen, f_bitlen, f_offset)
            return property(lambda x:field)

        # generate property from register description
        r_fields.reverse()
        kw = {}
        f_offset = 0
        for f_name, f_bitlen in r_fields:
            if len(f_name) > 0:
                kw[f_name] = makeprop(r_bitlen, f_bitlen, f_offset)
            f_offset += f_bitlen
        r_fields.reverse()

        # dynamically generate class for this register configuration
        sub = type(cls.__name__, (cls, ), kw)
        sub.__fields = [k for k,v in r_fields if k]
        sub.__length = r_bitlen

        obj = int.__new__(sub, address)
        protect_object(obj)
        return obj

    @property
    def fields(self):
        return list(self.__fields)

    @property
    def length(self):
        return self.__length

    """
    Returns a new register instance with given initial value.
    """
    def __call__(self, *args, **kwargs):
        reg = RegisterValue(self, 0)
        if args:
            reg.value = args[0]
        for k, v in kwargs.items():
            setattr(reg, k, v)
        return reg

class RegisterValue(object):
    def __new__(cls, reg, value):
        if cls is not RegisterValue:
            return object.__new__(cls)

        def makeprop(field):
            def fget(self):
                fval = (self.__value & field) >> field.offset
                return Bits(uint=fval.uint, length=field.bitlen)
            def fset(self, val):
                curval = self.__value
                newval = to_bits(val, curval.length) << field.offset
                curval ^= field & curval
                self.__value = curval | newval
                self.__notify()
            return property(fget, fset)

        kw = {}
        for f_name in reg.fields:
            field = getattr(reg, f_name)
            kw[f_name] = makeprop(field)

        obj = type(cls.__name__, (cls, ), kw)(reg, value)
        obj.__reg = reg
        obj.__mon = {}
        obj.value = value

        protect_object(obj)
        return obj

    @property
    def length(self):
        return self.__reg.length

    @property
    def value(self):
        return BitArray(bytes=self.__value.tobytes())

    @value.setter
    def value(self, value):
        self.__value = to_bits(value, self.__reg.length)
        self.__notify()

    @property
    def fields(self):
        return self.__reg.fields

    def subscribe(self, func):
        self.__mon[func] = 1

    def unsubscribe(self, func):
        if self.__mon.has_key(func):
            del self.__mon[func]

    def __notify(self, *args, **kwargs):
        for func in self.__mon.keys():
            func(self, *args, **kwargs)

    def __repr__(self):
        rep = []
        for f_name in self.fields:
            field = getattr(self, f_name)
            rep.append("{0}={1}".format(f_name, field))
        return "(" + ", ".join(rep) + ")"

    """
    Returns a new register value instance with the same initial value.
    """
    def __call__(self, *args, **kwargs):
        reg = RegisterValue(self.__reg, args[0] if args else self.value)
        for k, v in kwargs.items():
            setattr(reg, k, v)
        return reg

    def __and__(self, v):
        return self.value & to_bits(v, self.length)

    def __or__(self, v):
        return self.value | to_bits(v, self.length)

    def __xor__(self, v):
        return self.value ^ to_bits(v, self.length)

    def __nonzero__(self):
        return self.value.uint

if __name__ == "__main__": 
    from IPython import embed

    def handle_exception(atype, value, tb):
        if hasattr(sys, 'ps1') or not sys.stderr.isatty():
            # we are in interactive mode or we don't have a tty-like
            # device, so we call the default hook
            sys.__excepthook__(atype, value, tb)
        else:
            # we are NOT in interactive mode, print the exception...
            import traceback
            traceback.print_exception(atype, value, tb)
            print

            # ...then start the debugger in post-mortem mode.
            from IPython import embed
            embed()
    sys.excepthook = handle_exception

    REG = Register("FOO:3 :1 BAR:4", 0x12)
    print(REG)
    print(REG.FOO)
    print(REG.BAR)

    reg = REG(0xAC)
    print(reg)
    print(reg.FOO)
    print(reg.BAR)

    embed()
