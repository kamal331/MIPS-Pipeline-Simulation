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
from BinFuncs import sign_extend, bin_to_int_signed


class ALU:
    """
    Arithmetic Logic Unit (ALU) for MIPS
    """

    @staticmethod
    def add(a: str, b: str) -> str:
        """
        a + b
        """
        return sign_extend(bin_to_int_signed(a, 32) + bin_to_int_signed(b, 32), 32)

    @staticmethod
    def sub(a: str, b: str) -> str:
        """
        a - b
        """
        return sign_extend(bin_to_int_signed(a, 32) - bin_to_int_signed(b, 32), 32)

    @staticmethod
    def and_(a: str, b: str) -> str:
        """
        a & b
        """
        return sign_extend(bin_to_int_signed(a, 32) & bin_to_int_signed(b, 32), 32)

    @staticmethod
    def or_(a: str, b: str) -> str:
        """
        a | b
        """
        return sign_extend(bin_to_int_signed(a, 32) | bin_to_int_signed(b, 32), 32)

    @staticmethod
    def xor(a: str, b: str) -> str:
        """
        a ^ b
        """
        return sign_extend(bin_to_int_signed(a, 32) ^ bin_to_int_signed(b, 32), 32)

    @staticmethod
    def nor(a: str, b: str) -> str:
        """
        ~(a | b)
        """
        return sign_extend(~(bin_to_int_signed(a, 32) | bin_to_int_signed(b, 32)), 32)

    @staticmethod
    def sll(a: str, n: int) -> str:
        """
        a << n
        """
        return sign_extend(bin_to_int_signed(a, 32) << n, 32)

    @staticmethod
    def srl(a: str, n: int) -> str:
        """
        a >> n
        """
        return sign_extend(bin_to_int_signed(a, 32) >> n, 32)


# * =========== test ===========
if __name__ == '__main__':
    alu = ALU()
    print(alu.add('0'*32, '1'*32))
