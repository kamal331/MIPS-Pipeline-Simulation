"""
This file contains the ALU class for MIPS.
ALU has 2 inputs and 1 output.
The inputs are 32-bit binary strings.
The output is a 32-bit binary string.

ALU can do the following operations:
    add
    sub
    and
    or
    xor
    nor
    slt
    sll
    srl
"""
from BinFuncs import sign_extend, bin_to_int


class ALU:
    def __init__(self) -> None:
        pass

    def add(self, a: str, b: str) -> str:
        """
        a + b
        """
        return sign_extend(bin_to_int(a) + bin_to_int(b))

    def sub(self, a: str, b: str) -> str:
        """
        a - b
        """
        return sign_extend(bin_to_int(a) - bin_to_int(b))

    def and_(self, a: str, b: str) -> str:
        """
        a & b
        """
        return sign_extend(bin_to_int(a) & bin_to_int(b))

    def or_(self, a: str, b: str) -> str:
        """
        a | b
        """
        return sign_extend(bin_to_int(a) | bin_to_int(b))

    def xor(self, a: str, b: str) -> str:
        """
        a ^ b
        """
        return sign_extend(bin_to_int(a) ^ bin_to_int(b))

    def nor(self, a: str, b: str) -> str:
        """
        ~(a | b)
        """
        return sign_extend(~(bin_to_int(a) | bin_to_int(b)))

    def sll(self, a: str, n: int) -> str:
        """
        a << n
        """
        return sign_extend(bin_to_int(a) << n)

    def srl(self, a: str, n: int) -> str:
        """
        a >> n
        """
        return sign_extend(bin_to_int(a) >> n)


# * =========== test ===========
# alu: ALU = ALU()
# print(alu.add(sign_extend(-1), sign_extend(1)))
# print(alu.sub(sign_extend(-1), sign_extend(1)))
