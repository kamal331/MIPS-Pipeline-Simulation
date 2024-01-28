"""
Functions related to doing things with binary numbers
"""

def sign_extend(val: int) -> str:
    # if bigger than 32 bits, return least 32 bits
    if val >= 2**32:
        return bin(val)[-32:]
    if val < 0:
        return '1' * (32 - len(bin(val))) + 3*'1' + bin(val)[3:]
    return '0' * (32 - len(bin(val))) + 2*'0' + bin(val)[2:]


def bin_to_int_signed(val: str) -> int:
    if val.startswith('1'):
        return -1 * (2**32 - int(val, 2))
    return int(val, 2)


def bin_to_int_unsigned(val: str) -> int:
    return int(val, 2)


# * =========== test ===========
# print(sign_extend(2**32+1))  # overflow

# print(bin_to_int(sign_extend(2)))
