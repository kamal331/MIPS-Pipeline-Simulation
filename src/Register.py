class Reg:
    def __init__(self, name: str, val: int = 0) -> None:
        self.name = name
        self.val = val

    def str_val(self) -> str:
        if self.val < 0:
            # why [3:]? because bin() returns '-0bxxxx'
            return '1' * (32 - len(bin(self.val))) + 3*'1' + bin(self.val)[3:]
        # why [2:]? because bin() returns '0bxxxx'
        return '0' * (32 - len(bin(self.val))) + 2*'0' + bin(self.val)[2:]


class RegFile:
    def __init__(self) -> None:
        self.regs = [Reg(f'${i}') for i in range(32)]

    def __getitem__(self, key: str) -> Reg:
        if key.startswith('$'):
            return self.regs[int(key[1:])]
        else:
            return self.regs[int(key)]

    def __setitem__(self, key: str, val: int) -> None:
        if key.startswith('$'):
            self.regs[int(key[1:])].val = val
        else:
            self.regs[int(key)].val = val

    def __str__(self) -> str:
        return '\n'.join([f'{reg.name}: {reg.val}' for reg in self.regs])



# * =========== test ===========
regs: RegFile = RegFile()
regs['$1'] = 1
regs['$2'] = 2
regs['$3'] = 3

print(regs['$1'].str_val())
print(regs['$2'].str_val())
print(regs['$3'].str_val())
print(regs['$4'].str_val())

print(regs)