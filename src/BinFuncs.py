"""
Functions related to doing things with binary numbers
"""


def sign_extend(val: int, bits_no: int) -> str:
    """
    turn integer to a 2's complement binary string
    """
    if val >= 2**bits_no:
        return bin(val)[-bits_no:]
    if val < 0:
        return bin(val & (2**bits_no-1))[2:]
    return '0' * (bits_no - len(bin(val))) + 2*'0' + bin(val)[2:]


def bin_to_int_signed(val: str, bits_no: int) -> int:
    if val.startswith('1'):
        return -1 * (2**bits_no - int(val, 2))
    return int(val, 2)


def bin_to_int_unsigned(val: str) -> int:
    return int(val, 2)


def complement(val: str) -> str:
    return ''.join(['1' if bit == '0' else '0' for bit in val])


def bin_sign_extend(val: str, bits_no: int) -> str:
    if val.startswith('1'):
        return '1' * (bits_no - len(val)) + val
    return '0' * (bits_no - len(val)) + val


# * =========== test ===========
if __name__ == '__main__':
    print(sign_extend(1, 32))
    print(sign_extend(-1, 32))
    print(sign_extend(2**33, 32))
    print(sign_extend(-7, 32))
    print(bin_to_int_signed('1'*32, 32))
