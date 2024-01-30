"""Pipeline register class definition.
pipeline register is a class that contains the data that is passed between
stages of the pipeline.
data includes:
    - control signals
    - data from the previous stage
    - data from the current stage
"""

from typing import Any


class PipelineRegister:
    def __init__(self, name: str, data: dict[str, Any]) -> None:
        self.name = name
        self.data = data

    def __getitem__(self, key: str) -> str:
        return self.data[key]

    def __setitem__(self, key: str, val: str) -> None:
        self.data[key] = val

    def __str__(self) -> str:
        return f'{self.name}: {self.data}'

    def __repr__(self) -> str:
        return str(self)

    def __len__(self) -> int:
        return len(self.data)


# * =========== test ===========
if __name__ == '__main__':
    if_id = PipelineRegister(
        'IF/ID',
        {'PC': '0'*32,
         'IR': '0'*32,
         'PCWRITE': 1,
         'IFIDWRITE': 1})
    print(if_id)
