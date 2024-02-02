"""
Functions related to doing things with binary numbers
"""


def sign_extend(val: int, bits_no: int) -> str:
    # ex: if bigger than 32 bits, return least 32 bits
    if val >= 2**bits_no:
        return bin(val)[-bits_no:]
    if val < 0:
        return '1' * (bits_no - len(bin(val))) + 3*'1' + bin(val)[3:]
    return '0' * (bits_no - len(bin(val))) + 2*'0' + bin(val)[2:]


def bin_to_int_signed(val: str, bits_no: int) -> int:
    if val.startswith('1'):
        return -1 * (2**bits_no - int(val, 2))
    return int(val, 2)


def bin_to_int_unsigned(val: str) -> int:
    return int(val, 2)


# * =========== test ===========
if __name__ == '__main__':
    print(sign_extend(1, 32))
    print(sign_extend(-1, 32))
    print(sign_extend(2**33, 32))
    print(bin_to_int_signed('1'*32, 32))
