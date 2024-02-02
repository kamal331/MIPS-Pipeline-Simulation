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

    @staticmethod
    def mult(m: str, q: str, bits_no=16) -> str:
        """_summary_

        Args:
            a (str): 32-bit binary string
            b (str): 32-bit binary string

        Returns:
            str: a * b using booth algorithm
        """
        # booth algorithm for multiplication of two signed 32-bit numbers
        # 1. initialize the product and the multiplicand
        a = '0' * bits_no
        q_minus = '0'
        for _ in range(bits_no):
            # 2. check the last 2 bits of q and q_minus
            if q[-1] == '1' and q_minus == '0':
                a = (ALU.sub(a, m))[-bits_no:]
            elif q[-1] == '0' and q_minus == '1':
                a = (ALU.add(a, m))[-bits_no:]
            # 3. shift right a and q
            a_copy = q[-1] + a[:-1]
            q_minus = q[-1]
            q = a[-1] + q[:-1]
            a = a_copy

        return (a + q)[-bits_no * 2:]


# * =========== test ===========
if __name__ == '__main__':
    alu = ALU()
    m = '0111'
    q = '0011'
    print(alu.mult(m, q, 4))  # 21 => 010101
