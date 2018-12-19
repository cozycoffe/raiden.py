#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
from ctypes import *

BITS_COUNT_IN_UINT32 = 32

def raiden(data, key):
    result = [0, 0]
    b0 = c_uint32(data[0])
    b1 = c_uint32(data[1])

    k = [c_uint32(key[0]), c_uint32(key[1]), c_uint32(key[2]), c_uint32(key[3])]
    sk = c_uint32(0)

    for i in range(0, 16):
        sk.value = k[i % 4].value = c_uint32(c_uint32(k[0].value + k[1].value).value + (c_uint32(k[2].value + k[3].value).value ^ (k[0].value << (k[2].value % 32)))).value
        b0.value += (c_uint32(sk.value + b1.value).value << 9) ^ (c_uint32((sk.value - b1.value)).value ^ (c_uint32((sk.value + b1.value)).value >> 14))
        b1.value += (c_uint32(sk.value + b0.value).value << 9) ^ (c_uint32(sk.value - b0.value).value ^ (c_uint32(sk.value + b0.value).value >> 14))

    result[0] = b0.value
    result[1] = b1.value

    return result


def decode_raiden(data, key):
    result = [0, 0]
    b0 = c_uint32(data[0])
    b1 = c_uint32(data[1])
    k = [c_uint32(key[0]), c_uint32(key[1]), c_uint32(key[2]), c_uint32(key[3])]
    subkeys = [c_uint32(0)] * 16

    # Subkeys are calculated
    for i in range(0, 16):
        k[i % 4].value = c_uint32(c_uint32(k[0].value + k[1].value).value + (c_uint32(k[2].value + k[3].value).value ^ (k[0].value << (k[2].value % 32)))).value
        subkeys[i] = c_uint32(k[i % 4].value)

    # Process is applied in the inverse order
    for i in range(15, -1, -1):
        b1.value -= (c_uint32(subkeys[i].value + b0.value).value << 9) ^ (c_uint32(subkeys[i].value - b0.value).value ^ (c_uint32(subkeys[i].value + b0.value).value >> 14))
        b0.value -= (c_uint32(subkeys[i].value + b1.value).value << 9) ^ (c_uint32(subkeys[i].value - b1.value).value ^ (c_uint32(subkeys[i].value + b1.value).value >> 14))

    result[0] = b0.value
    result[1] = b1.value

    return result


if __name__ == "__main__":
    key = [1, 2, 3, 4]
    v = [1234567890, 1234567890]
    enc = raiden(v, key)
    print("Original numbers", v)
    print("Encoded numbers", enc)
    print("Decoded numbers", decode_raiden(enc, key))
