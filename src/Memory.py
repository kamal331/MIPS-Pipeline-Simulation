"""
design memory for the MIPS simulator. Because memory 
is a large array, we use a class to represent it.
"""


from typing import Iterator


class Memory:
    def __init__(self, size: int) -> None:
        self.size = size
        self.mem = ['0'*32 for _ in range(size)]

    def __getitem__(self, key: int) -> str:
        return self.mem[key]

    def __setitem__(self, key: int, val: str) -> None:
        self.mem[key] = val

    def __str__(self) -> str:
        return '\n'.join([f'{i}: {self.mem[i]}' for i in range(self.size)])

    def __len__(self) -> int:
        return self.size

    def __iter__(self) -> Iterator[str]:
        return iter(self.mem)

    def __next__(self) -> str:
        try:
            return next(iter(self.mem))
        except StopIteration as e:
            raise StopIteration from e


# * =========== test ===========
if __name__ == '__main__':
    mem: Memory = Memory(100)
    mem[0] = '1'*32
    mem[1] = '01'*16
    mem[2] = '10'*16

    print(mem)
