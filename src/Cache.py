"""
level one 2-way set-associative MSI cache with write-back policy and write-allocate policy
each block have one of the following states:
    invalid
    shared  -> valid, not modified
    modified
"""
from Memory import Memory
from BinFuncs import sign_extend, bin_to_int_unsigned


class Block:
    """
    block in the cache with tag, data, and state
    """

    def __init__(self, tag: str,
                 data: str,
                 state: str = 'invalid') -> None:
        self.tag = tag
        self.data = data
        self.state = state

    def __str__(self) -> str:
        return f'tag: {self.tag}, data: {self.data}, state: {self.state}'

    def __repr__(self) -> str:
        return self.__str__()


class Cache:
    """
    n-way set-associative cache with write-allocation and write-back policy
    """

    def __init__(self, mem: Memory, cache_size: int,
                 line_of_data_size: int, associativity: int) -> None:
        self.mem = mem
        self.cache_size = cache_size
        self.line_of_data_size = line_of_data_size
        self.associativity = associativity
        self.blocks_no = cache_size // line_of_data_size
        self.sets_no = self.blocks_no // associativity
        # 0 means we have to replace the way 0
        self.lru = [0] * self.sets_no
        self.logic_set_bits_no = self.sets_no.bit_length()-1
        self.block_offset_bits_no = (line_of_data_size // 4).bit_length()-1
        self.tag_bits_no = 32 - self.logic_set_bits_no - self.block_offset_bits_no
        self.blocks_in_line = line_of_data_size // 4  # 4 bytes per word
        self.blocks = [
            [[Block('0'*self.tag_bits_no, '0'*32)
              for _i in range(self.blocks_in_line)]
             for _j in range(associativity)] for _ in range(self.sets_no)
        ]

    def __setitem__(self,
                    address: str,
                    val: str,
                    from_where: str = 'cpu') -> None:  # skipcq: PYL-W0621
        """
        if the block we want to write to is modified, first write the
          value in the block to memory (for all blocks in the line if 
          the block is modified)
        then write the value we want to cache
        after insuring that the modified block is written to memory, write
          the value to the block
        if from_where is 'mem', then we will bring a line from memory to cache
          (it means that for all blocks_in_line we will bring the corresponding 
          data from memory to cache) and state will be 'shared'
        if from_where is 'cpu', then we will write that block to cache and
          state will be 'modified'
        """
        tag = address[:self.tag_bits_no]
        block_offset = int(
            address[self.tag_bits_no+self.logic_set_bits_no:], 2)
        logic_set = int(address[self.tag_bits_no:self.tag_bits_no +
                                self.logic_set_bits_no], 2)
        lru = self.lru[logic_set]
        if from_where == 'mem':
            # first based on lru, decide which way to replace:
            if self.blocks[logic_set][lru][0].state == 'modified':
                for i in range(self.blocks_in_line):
                    self.mem[bin_to_int_unsigned
                             (self.blocks[logic_set][lru][i].tag +
                              f'{logic_set:0{self.logic_set_bits_no}b}' +
                              f'{i:0{self.block_offset_bits_no}b}')] = \
                        self.blocks[logic_set][lru][i].data
            for i in range(self.blocks_in_line):
                self.blocks[logic_set][lru][i].data = \
                    self.mem[bin_to_int_unsigned(
                        address[:self.tag_bits_no] +
                        f'{logic_set:0{self.logic_set_bits_no}b}' +
                        f'{i:0{self.block_offset_bits_no}b}')]
                self.blocks[logic_set][lru][i].tag = tag
                self.blocks[logic_set][lru][i].state = 'shared'
            self.lru[logic_set] = 1 - self.lru[logic_set]
            # first we have to write the modified blocks to memory:
            # for i in range(self.blocks_in_line):
            #     if self.blocks[logic_set][0][i].state == 'modified':
            #         self.mem[bin_to_int_unsigned(self.blocks[logic_set][0][i].tag + f'{logic_set:0{self.logic_set_bits_no}b}' +
            #                  f'{i:0{self.block_offset_bits_no}b}')] = self.blocks[logic_set][0][i].data
            # for i in range(self.blocks_in_line):
            #     self.blocks[logic_set][0][i].data = self.mem[bin_to_int_unsigned(
            #         address[:self.tag_bits_no] + f'{logic_set:0{self.logic_set_bits_no}b}' + f'{i:0{self.block_offset_bits_no}b}')]
            # self.blocks[logic_set][0][i].tag = tag
            # self.blocks[logic_set][0][i].state = 'shared'

        else:
            # for i in range(self.associativity):
            #     if self.blocks[logic_set][i][block_offset].state == 'modified':
            #         self.mem[self.blocks[logic_set][i][block_offset].tag + f'{logic_set:0{self.logic_set_bits_no}b}' +
            #                  f'{block_offset:0{self.block_offset_bits_no}b}'] = self.blocks[logic_set][i][block_offset].data
            self.blocks[logic_set][self.lru[logic_set]
                                   ][block_offset].data = val
            self.blocks[logic_set][self.lru[logic_set]][block_offset].tag = tag
            self.blocks[logic_set][self.lru[logic_set]
                                   ][block_offset].state = 'modified'
            self.lru[logic_set] = 1 - self.lru[logic_set]

    def __getitem__(self, address: str) -> str:  # skipcq: PYL-W0621
        """
        if the block we want to read from is invalid, then we will bring the block from memory to cache and state will be 'shared'
        if the block we want to read from is shared or modified, then we will read the value from the block
        """
        tag = address[:self.tag_bits_no]

        block_offset = int(
            address[self.tag_bits_no+self.logic_set_bits_no:], 2)
        logic_set = int(
            address[self.tag_bits_no:self.tag_bits_no + self.logic_set_bits_no], 2)
        for i in range(self.associativity):
            if self.blocks[logic_set][i][block_offset].tag == tag:
                cond1 = self.blocks[logic_set][i][block_offset].state == 'shared'
                cond2 = self.blocks[logic_set][i][block_offset].state == 'modified'
                if cond1 or cond2:  # reduced the complexity of the code :)
                    print('Cache hit ✅')
                    print(
                        f'hit, tag: {tag}, logic_set: {logic_set}, block_offset: {block_offset}')
                    return self.blocks[logic_set][i][block_offset].data
        # if we are here, then the block is not in the cache and we have to bring it from memory
        print('Cache miss ❌')
        self.__setitem__(
            address, self.mem[bin_to_int_unsigned(address)], 'mem')
        return self.mem[bin_to_int_unsigned(address)]

    # for printing the cache
    def __str__(self) -> str:
        res = ''
        for i in range(self.sets_no):
            res += f'set {i}:\n'
            for j in range(self.associativity):
                res += f'way {j}:\n'
                for k in range(self.blocks_in_line):
                    res += f'{self.blocks[i][j][k]}\n'
        return res
    
    def __repr__(self) -> str:
        return self.__str__()
    
    def __len__(self) -> int:
        return self.sets_no


def get_state_of_block(cache: Cache, address: str) -> str:  # skipcq: PYL-W0621
    tag = address[:cache.tag_bits_no]
    block_offset = int(address[cache.tag_bits_no+cache.logic_set_bits_no:], 2)
    logic_set = int(
        address[cache.tag_bits_no:cache.tag_bits_no + cache.logic_set_bits_no], 2)
    for i in range(cache.associativity):
        if cache.blocks[logic_set][i][block_offset].tag == tag:
            return cache.blocks[logic_set][i][block_offset].state
    return 'invalid'


data_mem: Memory = Memory(4096)
for index in range(4096):
    data_mem[index] = sign_extend(index, 32)
data_cache: Cache = Cache(data_mem, 256, 32, 2)
inst_mem: Memory = Memory(4096)


# * =========== test ===========
if __name__ == '__main__':
    LINE_SEPERATOR = '======================='

    print(data_mem[5])
    print(data_mem[128])

    address = '0' * 25 + '0' * 4 + '0' * 3
    print(f'address: {bin_to_int_unsigned(address)}')
    # first time, it will be a cache miss
    print(f'value: {data_cache[address]}')
    print(get_state_of_block(data_cache, address))

    print(LINE_SEPERATOR)

    address = '0' * 25 + '0' * 4 + '101'
    print(f'address: {bin_to_int_unsigned(address)}')
    # second time for same tag and logic_set, it will be a cache hit
    print(f'value: {data_cache[address]}')

    print(LINE_SEPERATOR)
    # different tag -> different way in the same set -> cache miss
    address = '0' * 24 + '1' + '0' * 4 + '000'
    print(f'address: {bin_to_int_unsigned(address)}')
    print(f'value: {data_cache[address]}')  # miss
    print(LINE_SEPERATOR)
    print(f'value: {data_cache[address]}')  # hit
    # get state of the block
    print(get_state_of_block(data_cache, address))

    print(LINE_SEPERATOR)

    # simulate cpu writes:
    data_cache['0'*25 + '1'*4 + '000'] = '1'*32
    print('value: ', data_cache['0'*25 + '1'*4 + '000'])
    print(get_state_of_block(data_cache, '0'*25 + '1'*4 + '000'))
