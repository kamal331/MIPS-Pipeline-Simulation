"""
_summary_
    parrallel MIPS simulator with MSI cache coherence protocol

"""
from termcolor import colored
from Memory import Memory
from Register import RegFile
from Cache import Cache, if_in_cache, add_to_cache
from Alu import ALU
from BinFuncs import sign_extend, bin_to_int_signed, bin_to_int_unsigned
from PipelineRegister import PipelineRegister


if_id = PipelineRegister('if_id', {'PC': '0'*5, 'RD': '0'*5, 'RT': '0'*5,
                         'RS': '0'*5, 'SHAMT': '0'*5, 'FUNCT': '0'*6,
                                   'OPCODE': '0'*6, 'IR': '0'*32})

id_ex = PipelineRegister('id_ex', {'PC': '0'*32, 'RD': '0'*5, 'RT': '0'*5,
                                   'RS': '0'*5, 'SHAMT': '0'*5,
                                   'FUNCT': '0'*6, 'OPCODE': '0'*6,
                                   'IR': '0'*32, 'REG_DST': '0',
                                   'ALU_SRC': '0'*2, 'MEM_TO_REG': '0',
                                   'ALUT_OP': '0'*2, 'MEM_READ': '0',
                                   'MEM_WRITE': '0', 'BRANCH': '0',
                                   'REG_WRITE': '0'})  # TODO: early branch detection

ex_mem = PipelineRegister('ex_mem', {'PC': '0'*32, 'RD': '0'*5, 'RT': '0'*5,
                                     'RS': '0'*5, 'SHAMT': '0'*5,
                                     'FUNCT': '0'*6, 'OPCODE': '0'*6,
                                     'IR': '0'*32, 'REG_DST': '0',
                                     'ALU_SRC': '0'*2, 'MEM_TO_REG': '0',
                                     'ALUT_OP': '0'*2, 'MEM_READ': '0',
                                     'MEM_WRITE': '0', 'BRANCH': '0',
                                     'REG_WRITE': '0', 'ALU_OUT': '0'*32,
                                     'ZERO': '0'})
# 'ALU_IN2': '0'*32, 'ALU_IN1': '0'*32, 'MEM_READ_DATA': '0'*32

mem_wb = PipelineRegister('mem_wb', {'PC': '0'*32, 'RD': '0'*5, 'RT': '0'*5,
                                     'RS': '0'*5, 'SHAMT': '0'*5,
                                     'FUNCT': '0'*6, 'OPCODE': '0'*6,
                                     'IR': '0'*32, 'REG_DST': '0',
                                     'ALU_SRC': '0'*2, 'MEM_TO_REG': '0',
                                     'ALUT_OP': '0'*2, 'MEM_READ': '0',
                                     'MEM_WRITE': '0', 'BRANCH': '0',
                                     'REG_WRITE': '0', 'ALU_OUT': '0'*32,
                                     'ZERO': '0'})


# tuple(opcode, funct): instruction
bin_to_inst_dict = {
    ('000000', '100000'): 'add',
    ('000000', '100010'): 'sub',
    ('000000', '100100'): 'and',
    ('000000', '100101'): 'or',
    ('000000', '100110'): 'xor',
    ('000000', '100111'): 'nor',
    ('000000', '101010'): 'slt',
    ('000000', '000000'): 'sll',
    ('000000', '000010'): 'srl',
    ('000000', '001000'): 'jr',
    ('000000', '001100'): 'syscall',
    ('000000', '001101'): 'break',
    ('000000', '010000'): 'mfhi',
    ('000000', '010010'): 'mflo',
    ('000000', '011000'): 'mult',
    ('000000', '011001'): 'multu',
    ('000000', '011010'): 'div',
    ('000000', '011011'): 'divu',
    ('000000', '010001'): 'mthi',
    ('000000', '010011'): 'mtlo',
    ('000000', '100001'): 'movn',
    ('000000', '100011'): 'movz',
    ('000000', '101011'): 'sltu',
    ('000000', '101000'): 'addu',
    ('000000', '101001'): 'addiu',
    ('000000', '001111'): 'jal',
    ('000100', 'xxxxxx'): 'beq',
    ('000101', 'xxxxxx'): 'bne',
    ('100011', 'xxxxxx'): 'lw',
    ('101011', 'xxxxxx'): 'sw',
    ('001000', 'xxxxxx'): 'addi',
    ('001100', 'xxxxxx'): 'andi',
    ('001101', 'xxxxxx'): 'ori',
    ('001110', 'xxxxxx'): 'xori',
    ('000010', 'xxxxxx'): 'j',
    ('000011', 'xxxxxx'): 'jal'
}

bin_to_regname = {
    '00000': '$0',   # zero
    '00001': '$1',   # at
    '00010': '$2',   # v0
    '00011': '$3',   # v1
    '00100': '$4',   # a0
    '00101': '$5',   # a1
    '00110': '$6',   # a2
    '00111': '$7',   # a3
    '01000': '$8',   # t0
    '01001': '$9',   # t1
    '01010': '$10',  # t2
    '01011': '$11',  # t3
    '01100': '$12',  # t4
    '01101': '$13',  # t5
    '01110': '$14',  # t6
    '01111': '$15',  # t7
    '10000': '$16',  # s0
    '10001': '$17',  # s1
    '10010': '$18',  # s2
    '10011': '$19',  # s3
    '10100': '$20',  # s4
    '10101': '$21',  # s5
    '10110': '$22',  # s6
    '10111': '$23',  # s7
    '11000': '$24',  # t8
    '11001': '$25',  # t9
    '11010': '$26',  # k0
    '11011': '$27',  # k1
    '11100': '$28',  # gp
    '11101': '$29',  # sp
    '11110': '$30',  # fp
    '11111': '$31'   # ra
}


inst_mem = Memory(1024)
reg_file = RegFile()


# initialize reg_file:
for i in range(32):
    reg_file[f'${i}'] = 0


alu = ALU()
cache = Cache(1024, 32, 2)
data_mem = Memory(1024)
for i in range(1024):
    data_mem[i] = i

alu_inp1 = alu_inp2 = alu_out = 0
zero_flag = 0
pc = 0


def update_if_id() -> None:
    global if_id
    if_id['PC'] = sign_extend(pc, 32)
    # get instruction from memory
    inst = inst_mem[pc]
    # update if_id
    if_id['IR'] = inst
    if_id['OPCODE'] = inst[:6]
    if_id['RS'] = inst[6:11]
    if_id['RT'] = inst[11:16]
    if_id['RD'] = inst[16:21]
    if_id['SHAMT'] = inst[21:26]
    if_id['FUNCT'] = inst[26:32]


def update_id_ex() -> None:
    global id_ex
    inst = if_id['IR']
    # update id_ex
    id_ex['IR'] = inst
    id_ex['OPCODE'] = inst[:6]
    id_ex['RS'] = inst[6:11]
    id_ex['RT'] = inst[11:16]
    id_ex['RD'] = inst[16:21]
    id_ex['SHAMT'] = inst[21:26]
    id_ex['FUNCT'] = inst[26:32]
    id_ex['PC'] = if_id['PC']

    # control signals
    # execute instruction
    try:
        opcode = bin_to_inst_dict[(id_ex['OPCODE'], id_ex['FUNCT'])]
    except KeyError:
        opcode = bin_to_inst_dict[(id_ex['OPCODE'], 'xxxxxx')]
    if is_rtype(opcode):
        id_ex['REG_DST'] = '1'
        id_ex['ALU_SRC'] = '00'
        id_ex['MEM_TO_REG'] = '0'
        id_ex['ALUT_OP'] = '10'
        id_ex['MEM_READ'] = '0'
        id_ex['MEM_WRITE'] = '0'
        id_ex['BRANCH'] = '0'
        id_ex['REG_WRITE'] = '1'
    elif is_itype(opcode):
        id_ex['REG_DST'] = '0'
        id_ex['ALU_SRC'] = '01'
        id_ex['MEM_TO_REG'] = '0'
        id_ex['ALUT_OP'] = '00'
        id_ex['MEM_READ'] = '0'
        id_ex['MEM_WRITE'] = '0'
        id_ex['BRANCH'] = '0'
        id_ex['REG_WRITE'] = '1'
        if opcode in ['lw', 'sw']:
            id_ex['MEM_TO_REG'] = '1'
            id_ex['ALUT_OP'] = '00'
            id_ex['MEM_READ'] = '1'
            id_ex['REG_DST'] = '0'
            if opcode == 'sw':
                id_ex['MEM_WRITE'] = '1'
                id_ex['REG_WRITE'] = '0'
    elif is_branch(opcode):
        id_ex['REG_DST'] = '0'
        id_ex['ALU_SRC'] = '00'
        id_ex['MEM_TO_REG'] = '0'
        id_ex['ALUT_OP'] = '01'
        id_ex['MEM_READ'] = '0'
        id_ex['MEM_WRITE'] = '0'
        id_ex['BRANCH'] = '1'
        id_ex['REG_WRITE'] = '0'


def update_ex_mem() -> None:
    global ex_mem
    # get instruction from id_ex
    inst = id_ex['IR']
    # update ex_mem
    ex_mem['IR'] = inst
    ex_mem['OPCODE'] = inst[:6]
    ex_mem['RS'] = inst[6:11]
    ex_mem['RT'] = inst[11:16]
    ex_mem['RD'] = inst[16:21]
    ex_mem['SHAMT'] = inst[21:26]
    ex_mem['FUNCT'] = inst[26:32]
    ex_mem['PC'] = id_ex['PC']

    # control signals
    # execute instruction
    try:
        opcode = bin_to_inst_dict[(id_ex['OPCODE'], id_ex['FUNCT'])]
    except KeyError:
        opcode = bin_to_inst_dict[(id_ex['OPCODE'], 'xxxxxx')]

    # get needed control signals from id_ex TODO: some signals are not needed and can be removed
    ex_mem['REG_DST'] = id_ex['REG_DST']
    ex_mem['ALU_SRC'] = id_ex['ALU_SRC']
    ex_mem['MEM_TO_REG'] = id_ex['MEM_TO_REG']
    ex_mem['ALUT_OP'] = id_ex['ALUT_OP']
    ex_mem['MEM_READ'] = id_ex['MEM_READ']
    ex_mem['MEM_WRITE'] = id_ex['MEM_WRITE']
    ex_mem['BRANCH'] = id_ex['BRANCH']
    ex_mem['REG_WRITE'] = id_ex['REG_WRITE']
    ex_mem['ALU_OUT'] = alu_out


def update_mem_wb() -> None:
    global mem_wb
    # get instruction from ex_mem
    inst = ex_mem['IR']
    # update mem_wb
    mem_wb['IR'] = inst
    mem_wb['OPCODE'] = inst[:6]
    mem_wb['RS'] = inst[6:11]
    mem_wb['RT'] = inst[11:16]
    mem_wb['RD'] = inst[16:21]
    mem_wb['SHAMT'] = inst[21:26]
    mem_wb['FUNCT'] = inst[26:32]
    mem_wb['PC'] = ex_mem['PC']

    # control signals
    # execute instruction
    try:
        opcode = bin_to_inst_dict[(mem_wb['OPCODE'], mem_wb['FUNCT'])]
    except KeyError:
        opcode = bin_to_inst_dict[(mem_wb['OPCODE'], 'xxxxxx')]

    # get needed control signals from ex_mem TODO: some signals are not needed and can be removed
    mem_wb['REG_DST'] = ex_mem['REG_DST']
    mem_wb['ALU_SRC'] = ex_mem['ALU_SRC']
    mem_wb['MEM_TO_REG'] = ex_mem['MEM_TO_REG']
    mem_wb['ALUT_OP'] = ex_mem['ALUT_OP']
    mem_wb['MEM_READ'] = ex_mem['MEM_READ']
    mem_wb['MEM_WRITE'] = ex_mem['MEM_WRITE']
    mem_wb['BRANCH'] = ex_mem['BRANCH']
    mem_wb['REG_WRITE'] = ex_mem['REG_WRITE']
    mem_wb['ALU_OUT'] = ex_mem['ALU_OUT']


def fetch() -> None:
    global if_id
    # get instruction from memory
    inst = inst_mem[pc]
    # ! No need to write to if_id
    # if_id['IR'] = inst
    # if_id['OPCODE'] = inst[:6]
    # if_id['RS'] = inst[6:11]
    # if_id['RT'] = inst[11:16]
    # if_id['RD'] = inst[16:21]
    # if_id['SHAMT'] = inst[21:26]
    # if_id['FUNCT'] = inst[26:32]
    text = colored('instruction fetched: ✅', 'yellow')
    print(text)
    print(inst)


def is_rtype(name: str) -> bool:
    return name in ['add', 'sub', 'and', 'or', 'xor', 'nor', 'slt', 'sll',
                    'srl', 'jr', 'syscall', 'break', 'mfhi', 'mflo', 'mult',
                    'multu', 'div', 'divu', 'mthi', 'mtlo', 'movn', 'movz',
                    'sltu', 'addu']


def is_itype(name: str) -> bool:
    return name in ['addi', 'andi', 'ori', 'xori', 'beq', 'bne', 'lw', 'sw']


def is_branch(name: str) -> bool:
    return name in ['beq', 'bne']


def print_decoded_inst(if_id: PipelineRegister) -> None:
    # get instruction from if_id
    try:
        opcode = bin_to_inst_dict[(if_id['OPCODE'], if_id['FUNCT'])]
    except KeyError:
        opcode = bin_to_inst_dict[(if_id['OPCODE'], 'xxxxxx')]

    text = colored('instruction decoded: ✅', 'yellow')
    print(text)
    if is_rtype(opcode):
        print(opcode, bin_to_regname[if_id['RD']], bin_to_regname[if_id['RS']],
              bin_to_regname[if_id['RT']])
    elif is_itype(opcode):
        print(opcode, bin_to_regname[if_id['RT']], bin_to_regname[if_id['RS']],
              sign_extend(bin_to_int_signed(if_id['IR'][16:], 16), 16))
    elif is_branch(opcode):
        print(opcode, bin_to_regname[if_id['RS']], bin_to_regname[if_id['RT']],
              sign_extend(bin_to_int_signed(if_id['IR'][16:], 16), 16))


def decode():
    # get instruction from if_id

    # print instruction type:
    print_decoded_inst(if_id)


# -----------

def ex_rtype(inst: str, opcode: str) -> None:
    global alu_inp1, alu_inp2, alu_out, zero_flag

    # binary should be passed to alu
    if type(reg_file[f'${bin_to_int_unsigned(inst[6:11])}'].val) is int:
        alu_inp1 = sign_extend(
            reg_file[f'${bin_to_int_unsigned(inst[6:11])}'].val, 32)
        alu_inp2 = sign_extend(
            reg_file[f'${bin_to_int_unsigned(inst[11:16])}'].val, 32)

    # if binary, no need to do anything
    if type(reg_file[f'${bin_to_int_unsigned(inst[6:11])}'].val) is str:
        alu_inp1 = reg_file[f'${bin_to_int_unsigned(inst[6:11])}'].val
        alu_inp2 = reg_file[f'${bin_to_int_unsigned(inst[11:16])}'].val

    # alu_inp1 = reg_file[f'${bin_to_int_unsigned(inst[6:11])}'].val
    # alu_inp2 = reg_file[f'${bin_to_int_unsigned(inst[11:16])}'].val
    # print(f'alu_inp1 = {alu_inp1}')

    if opcode == 'add':
        alu_out = alu.add(alu_inp1, alu_inp2)
        print('add', bin_to_regname[inst[16:21]], bin_to_regname[inst[6:11]],
              bin_to_regname[inst[11:16]], '=', alu_out)
    elif opcode == 'sub':
        alu_out = alu.sub(alu_inp1, alu_inp2)
        # reg_file[bin_to_int_unsigned(inst[16:21])] = alu_out
        print('sub', bin_to_regname[inst[16:21]], bin_to_regname[inst[6:11]],
              bin_to_regname[inst[11:16]])
    elif opcode == 'and':
        alu_out = alu.and_(alu_inp1, alu_inp2)
        # reg_file[bin_to_int_unsigned(inst[16:21])] = alu_out
        print('and', bin_to_regname[inst[16:21]], bin_to_regname[inst[6:11]],
              bin_to_regname[inst[11:16]])
    elif opcode == 'or':
        alu_out = alu.or_(alu_inp1, alu_inp2)
        # reg_file[bin_to_int_unsigned(inst[16:21])] = alu_out
        print('or', bin_to_regname[inst[16:21]], bin_to_regname[inst[6:11]],
              bin_to_regname[inst[11:16]])
    elif opcode == 'xor':
        alu_out = alu.xor(alu_inp1, alu_inp2)
        # reg_file[bin_to_int_unsigned(inst[16:21])] = alu_out
        print('xor', bin_to_regname[inst[16:21]], bin_to_regname[inst[6:11]],
              bin_to_regname[inst[11:16]])
    elif opcode == 'nor':
        alu_out = alu.nor(alu_inp1, alu_inp2)
        # reg_file[bin_to_int_unsigned(inst[16:21])] = alu_out
        print('nor', bin_to_regname[inst[16:21]], bin_to_regname[inst[6:11]],
              bin_to_regname[inst[11:16]])

    elif opcode == 'sll':
        alu_out = alu.sll(alu_inp1, bin_to_int_unsigned(inst[21:26]))
        # reg_file[bin_to_int_unsigned(inst[16:21])] = alu_out
        print('sll', bin_to_regname[inst[16:21]], bin_to_regname[inst[11:16]],
              bin_to_int_unsigned(inst[21:26]))

    elif opcode == 'srl':
        alu_out = alu.srl(alu_inp1, bin_to_int_unsigned(inst[21:26]))
        # reg_file[bin_to_int_unsigned(inst[16:21])] = alu_out
        print('srl', bin_to_regname[inst[16:21]], bin_to_regname[inst[11:16]],
              bin_to_int_unsigned(inst[21:26]))

    # change control signals

    # if opcode == 'jr':
    #     alu_out = 0
    #     print('jr', bin_to_regname[inst[6:11]])
    #     # change control signals
    #     # id_ex['ALUT_OP'] = '00'
    #     # id_ex['MEM_WRITE'] = 0


def ex_itype(inst: str, opcode: str) -> None:
    global alu_inp1, alu_inp2, alu_out, zero_flag
    if type(reg_file[f'${bin_to_int_unsigned(inst[6:11])}'].val) is int:
        alu_inp1 = sign_extend(
            reg_file[f'${bin_to_int_unsigned(inst[6:11])}'].val, 32)
    if type(reg_file[f'${bin_to_int_unsigned(inst[6:11])}'].val) is str:
        alu_inp1 = reg_file[f'${bin_to_int_unsigned(inst[6:11])}'].val

    alu_inp2 = sign_extend(
        bin_to_int_signed(inst[16:], 16), 32)

    if opcode == 'addi':
        alu_out = alu.add(alu_inp1, alu_inp2)
        print('addi', bin_to_regname[inst[11:16]], bin_to_regname[inst[6:11]],
              bin_to_int_signed(inst[16:], 16), '=', alu_out)
    elif opcode == 'andi':
        alu_out = alu.and_(alu_inp1, alu_inp2)
        print('andi', bin_to_regname[inst[11:16]], bin_to_regname[inst[6:11]],
              bin_to_int_signed(inst[16:], 16), '=', alu_out)
    elif opcode == 'ori':
        alu_out = alu.or_(alu_inp1, alu_inp2)
        print('ori', bin_to_regname[inst[11:16]], bin_to_regname[inst[6:11]],
              bin_to_int_signed(inst[16:], 16), '=', alu_out)
    elif opcode == 'xori':
        alu_out = alu.xor(alu_inp1, alu_inp2)
        print('xori', bin_to_regname[inst[11:16]], bin_to_regname[inst[6:11]],
              bin_to_int_signed(inst[16:], 16), '=', alu_out)

    elif opcode == 'lw':
        alu_out = alu.add(alu_inp1, alu_inp2)
        print('lw', bin_to_regname[inst[11:16]], bin_to_int_signed(inst[16:], 16),
              '(', bin_to_regname[inst[6:11]], ')', '=', alu_out)
    elif opcode == 'sw':
        alu_out = alu.add(alu_inp1, alu_inp2)
        print('sw', bin_to_regname[inst[11:16]], bin_to_int_signed(inst[16:], 16),
              '(', bin_to_regname[inst[6:11]], ')', '=', alu_out)


def execute():
    # get instruction from id_ex
    global ex_mem
    inst = id_ex['IR']

    # # update ex_mem
    # ex_mem['IR'] = inst
    # ex_mem['OPCODE'] = inst[:6]
    # ex_mem['RS'] = inst[6:11]
    # ex_mem['RT'] = inst[11:16]
    # ex_mem['RD'] = inst[16:21]
    # ex_mem['SHAMT'] = inst[21:26]
    # ex_mem['FUNCT'] = inst[26:32]
    # ex_mem['PC'] = id_ex['PC']

    # execute instruction
    try:
        opcode = bin_to_inst_dict[(id_ex['OPCODE'], id_ex['FUNCT'])]
    except KeyError:
        opcode = bin_to_inst_dict[(id_ex['OPCODE'], 'xxxxxx')]

    if is_rtype(opcode):
        ex_rtype(inst, opcode)
    elif is_itype(opcode):
        ex_itype(inst, opcode)
    elif is_branch(opcode):
        # branch(opcode)
        pass


def working_with_cache() -> None:
    # if data is in cache, get it from cache. if not, get it from memory and add it to cache.
    # if instruction is lw, get data from cache or memory and add it to cache
    # if instruction is sw, write data to cache and set state to modified
    # if cache is full, use LRU to replace a block and before replacing, write back to memory if state is modified
    global ex_mem
    inst = ex_mem['IR']
    try:
        opcode = bin_to_inst_dict[(ex_mem['OPCODE'], ex_mem['FUNCT'])]
    except KeyError:
        opcode = bin_to_inst_dict[(ex_mem['OPCODE'], 'xxxxxx')]

    if opcode == 'lw':
        # check if the block is in cache
        if not if_in_cache(cache, alu_out):
            # if not, add it to cache
            add_to_cache(cache, alu_out, data_mem[alu_out])
        # get data from cache
        ex_mem['ALU_OUT'] = cache[alu_out].data
        print('lw', bin_to_regname[inst[11:16]], bin_to_int_signed(inst[16:], 16),
              '(', bin_to_regname[inst[6:11]], ')', '=', ex_mem['ALU_OUT'])
    elif opcode == 'sw':
        # check if the block is in cache
        if not if_in_cache(cache, alu_out):
            # if not, add it to cache
            add_to_cache(cache, alu_out, data_mem[alu_out])
        # write data to cache and set state to modified
        cache[alu_out].data = sign_extend(
            reg_file[f'${bin_to_int_unsigned(inst[11:16])}'].val, 32)
        cache[alu_out].state = 'modified'
        print('sw', bin_to_regname[inst[11:16]], bin_to_int_signed(inst[16:], 16),
              '(', bin_to_regname[inst[6:11]], ')', '=', cache[alu_out].data)
    # elif opcode == 'addi':
    #     print('addi', bin_to_regname[inst[11:16]], bin_to_regname[inst[6:11]],
    #           bin_to_int_signed(inst[16:], 16), '=', ex_mem['ALU_OUT'])
    else:
        print('no cache needed for this instruction 🙄')


def write_back() -> None:
    # get instruction from mem_wb
    global mem_wb
    inst = mem_wb['IR']

    # # update mem_wb
    # mem_wb['IR'] = inst
    # mem_wb['OPCODE'] = inst[:6]
    # mem_wb['RS'] = inst[6:11]
    # mem_wb['RT'] = inst[11:16]
    # mem_wb['RD'] = inst[16:21]
    # mem_wb['SHAMT'] = inst[21:26]
    # mem_wb['FUNCT'] = inst[26:32]
    # mem_wb['PC'] = ex_mem['PC']

    # execute instruction
    try:
        opcode = bin_to_inst_dict[(mem_wb['OPCODE'], mem_wb['FUNCT'])]
    except KeyError:
        opcode = bin_to_inst_dict[(mem_wb['OPCODE'], 'xxxxxx')]
    text = colored('write_back_opcode:   ', 'red')
    print(text, opcode)

    # if instruction is lw, write data to register
    if mem_wb['MEM_TO_REG'] == '1':
        reg_file[f'${bin_to_int_unsigned(inst[11:16])}'].val = mem_wb['ALU_OUT']
        print('lw', bin_to_regname[inst[11:16]], bin_to_int_signed(inst[16:], 16),
              '(', bin_to_regname[inst[6:11]], ')', '=', mem_wb['ALU_OUT'])
    elif mem_wb['REG_WRITE'] == '1':
        if is_itype(opcode):
            reg_file[f'${bin_to_int_unsigned(inst[11:16])}'].val = mem_wb['ALU_OUT']
            print('reg file updated ✅:',
                  bin_to_regname[inst[11:16]], '=', mem_wb['ALU_OUT'])
        if is_rtype(opcode):
            reg_file[f'${bin_to_int_unsigned(inst[16:21])}'].val = mem_wb['ALU_OUT']
            print('reg file updated ✅:',
                  bin_to_regname[inst[16:21]], '=', mem_wb['ALU_OUT'])
        # elif is_rtype(opcode): TODO: voice1
        #     print('&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&')
        #     reg_file[bin_to_int_unsigned(inst[16:21])].val = mem_wb['ALU_OUT']
        #     print(opcode, bin_to_regname[inst[16:21]], bin_to_regname[inst[6:11]],
        #           bin_to_regname[inst[11:16]], '=', mem_wb['ALU_OUT'])
    elif mem_wb['MEM_READ'] == '1':
        print('lw', bin_to_regname[inst[11:16]], bin_to_int_signed(inst[16:], 16),
              '(', bin_to_regname[inst[6:11]], ')', '=', mem_wb['ALU_OUT'])
    elif opcode == 'jr':
        print('jr', bin_to_regname[inst[6:11]])
    elif opcode == 'jal':
        print('jal', bin_to_regname[inst[6:11]])
    elif opcode == 'j':
        print('j', bin_to_regname[inst[6:11]])


# *********************** main ***********************

def main() -> None:
    global pc
    with open('instructions.txt', 'r') as f:  # TODO: try excpet
        i = 0
        for line in f:
            inst_mem[i] = line.strip()
            i += 1

    pc_write = if_id_write = True

    inst_count = 6
    pipeline_stage_no = 5
    total_pipeline_clocks = inst_count + pipeline_stage_no - 1  # ! except for hazards
    cycle_seperator = colored('==================', 'magenta')
    stage_seperator = colored('------------------', 'green')
    while total_pipeline_clocks > 0:
        # first fetch instruction from memory (from file)
        # pipeline fetch, decode, execute memory, write back
        if pc_write and if_id_write:
            # fetch instruction from memory
            fetch()
            print(stage_seperator)

            decode()
            print(stage_seperator)

            execute()
            print(stage_seperator)

            working_with_cache()
            print(stage_seperator)

            write_back()

        print('\n\t', cycle_seperator, '\n')
        update_mem_wb()
        update_ex_mem()  # get from id_ex
        update_id_ex()  # get from if_id
        update_if_id()  # get from pc
        total_pipeline_clocks -= 1
        pc += 1


if __name__ == '__main__':
    main()
