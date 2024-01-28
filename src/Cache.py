from BinFuncs import sign_extend, bin_to_int_unsigned
"""
level one 2-way set-associative MSI cache
each block have one of the following states:
    invalid
    shared
    modified
"""


class Block:
    def __init__(self, tag: str, data: str) -> None:
        self.tag = tag
        self.data = data
        self.state = 'invalid'

    def __str__(self) -> str:
        return f'Block(tag={self.tag}, data={self.data}, state={self.state})'

    def __repr__(self) -> str:
        return str(self)

    def __eq__(self, o: object) -> bool:
        if isinstance(o, Block):
            return self.tag == o.tag
        return False

    def __hash__(self) -> int:
        return hash(self.tag)

    def __len__(self) -> int:
        return len(self.data)

    def __getitem__(self, key: int) -> str:
        return self.data[key]


class Cache:
    def __init__(self, size: int, block_size: int, num_ways: int) -> None:
        self.size = size
        self.block_size = block_size
        self.num_blocks = size // block_size
        self.num_ways = num_ways
        self.num_sets = self.num_blocks // self.num_ways

        self.tag_size = 32 - (self.num_sets).bit_length() - \
            (block_size).bit_length() + 2
        self.set_bits_size = (self.num_sets).bit_length() - 1

        self.blocks = [[Block('0'*self.tag_size, '0'*block_size)
                        for _ in range(num_ways)] for _ in range(self.num_sets)]

        self.lru = [0 for _ in range(self.num_sets)]

    def __getitem__(self, key: str) -> Block | None:
        set_idx = bin_to_int_unsigned(key[self.tag_size:])
        tag = key[:self.tag_size]
        for i in range(self.num_ways):
            if self.blocks[set_idx][i].tag == tag:
                return self.blocks[set_idx][i]
        return None

    def __setitem__(self, key: str, val: Block) -> None:
        set_idx = bin_to_int_unsigned(key[self.tag_size:])
        tag = key[:self.tag_size]
        for i in range(self.num_ways):
            if self.blocks[set_idx][i].tag == tag:
                self.blocks[set_idx][i] = val
                return
        # if not in cache, add it to cache
        self.blocks[set_idx][self.lru[set_idx]] = val
        self.lru[set_idx] = (self.lru[set_idx] + 1) % self.num_ways

    def __str__(self) -> str:
        return '\n'.join([f'{i}: {self.blocks[i]}' for i in range(self.num_sets)])

    def __repr__(self) -> str:
        return str(self)

    def __len__(self) -> int:
        return self.size


def if_in_cache(cache: Cache, address: str) -> bool:
    tag_size = cache.tag_size
    set_bit_size = cache.set_bits_size
    tag_bits = address[:tag_size]
    set_bits = address[tag_size:tag_size+set_bit_size]
    # offset_bits = address[tag_size+set_bit_size:]
    # check if the block is in cache
    if cache[tag_bits + set_bits]:
        return True
    return False


def add_to_cache(cache: Cache, address: str, data: str) -> None:
    tag_size = cache.tag_size
    set_bit_size = cache.set_bits_size
    tag_bits = address[:tag_size]
    set_bits = address[tag_size:tag_size+set_bit_size]
    # offset_bits = address[tag_size+set_bit_size:]
    # if not, add it to cache
    block = Block(tag_bits, data)
    block.state = 'shared'
    cache[tag_bits + set_bits] = block


# * =========== test ===========
if __name__ == '__main__':
    cache: Cache = Cache(1024, 32, 2)
    # print(cache.tag_size)
    # print(cache)

    # check if a value is in cache or not, if not, add it to cache
    address = '01' * 16
    tag_size = 23
    set_bit_size = 4
    tag_bits = address[:tag_size]
    set_bits = address[tag_size:tag_size+set_bit_size]
    offset_bits = address[tag_size+set_bit_size:]
    print(tag_bits, set_bits, offset_bits)
    # check if the block is in cache
    if not if_in_cache(cache, address):
        add_to_cache(cache, address, '10101010101010101010101010101010')
    # print(cache)
    print(cache[tag_bits + set_bits])
    # print(cache)
