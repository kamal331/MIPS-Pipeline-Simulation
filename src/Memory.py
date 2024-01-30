"""
design memory for the MIPS simulator. Because memory is a large array, we use a class to represent it.
"""


class Memory:
    def __init__(self, size: int) -> None:
        self.size = size
        self.mem = [0 for _ in range(size)]

    def __getitem__(self, key: int) -> int:
        return self.mem[key]

    def __setitem__(self, key: int, val: int) -> None:
        self.mem[key] = val

    def __str__(self) -> str:
        return '\n'.join([f'{i}: {self.mem[i]}' for i in range(self.size)])

    def __len__(self) -> int:
        return self.size

    def __iter__(self):
        return iter(self.mem)

    def __next__(self) -> int:
        try:
            return next(self.mem)
        except StopIteration:
            raise StopIteration


# * =========== test ===========
# mem: Memory = Memory(100)
# mem[0] = 1
# mem[1] = 2
# mem[2] = 3

# print(mem)

