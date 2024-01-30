"""
_summary_
    parrallel MIPS simulator with MSI cache coherence protocol

"""

from Memory import Memory
from Register import RegFile
from Cache import Cache
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


def fetch() -> None:
    global if_id
    # get instruction from memory
    inst = inst_mem[bin_to_int_unsigned(if_id['PC'])]
    # update if_id
    if_id['IR'] = inst
    if_id['OPCODE'] = inst[:6]
    if_id['RS'] = inst[6:11]
    if_id['RT'] = inst[11:16]
    if_id['RD'] = inst[16:21]
    if_id['SHAMT'] = inst[21:26]
    if_id['FUNCT'] = inst[26:32]
    if_id['PC'] = sign_extend(bin_to_int_signed(if_id['PC'], 32) + 1, 32)
    print('instruction fetched ✅:')
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


def print_decoded_inst(if_id: PipelineRegister):
    # get instruction from if_id
    try:
        opcode = bin_to_inst_dict[(if_id['OPCODE'], if_id['FUNCT'])]
    except KeyError:
        opcode = bin_to_inst_dict[(if_id['OPCODE'], 'xxxxxx')]
    print('instruction decoded ✅:')
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
    # print instruction type:
    print_decoded_inst(if_id)


# -----------

def rtype(inst: str, opcode: str) -> None:
    global alu_inp1, alu_inp2, alu_out, zero_flag
    alu_inp1 = sign_extend(
        reg_file[f'${bin_to_int_unsigned(inst[6:11])}'].val, 32)
    alu_inp2 = sign_extend(
        reg_file[f'${bin_to_int_unsigned(inst[11:16])}'].val, 32)
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
    id_ex['REG_DST'] = 1  # it means that rd is destination
    id_ex['ALU_SRC'] = '00'  # alu_inp2 is from register
    id_ex['MEM_TO_REG'] = 0  # alu_out is from alu
    id_ex['ALUT_OP'] = '10'  # alu_out is from alu
    id_ex['MEM_READ'] = 0  # no memory read
    id_ex['MEM_WRITE'] = 0  # no memory write
    id_ex['BRANCH'] = 0  # no branch
    id_ex['REG_WRITE'] = 1  # write to register

    if opcode == 'jr':
        alu_out = 0
        print('jr', bin_to_regname[inst[6:11]])
        # change control signals
        id_ex['ALUT_OP'] = '00'
        id_ex['MEM_WRITE'] = 0


def execute():
    # get instruction from id_ex
    global ex_mem
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

    # execute instruction
    try:
        opcode = bin_to_inst_dict[(id_ex['OPCODE'], id_ex['FUNCT'])]
    except KeyError:
        opcode = bin_to_inst_dict[(id_ex['OPCODE'], 'xxxxxx')]

    if is_rtype(opcode):
        rtype(inst, opcode)
    elif is_itype(opcode):
        # itype(opcode)
        pass
    elif is_branch(opcode):
        # branch(opcode)
        pass


# *********************** main ***********************

def main() -> None:
    with open('instructions.txt', 'r') as f:  # TODO: try excpet
        i = 0
        for line in f:
            inst_mem[i] = line.strip()
            i += 1

    pc_write = if_write = True

    inst_count = 9
    while inst_count > 0:
        # first fetch instruction from memory (from file)
        if pc_write and if_write:
            # fetch instruction from memory
            fetch()
            decode()
            execute()

        print('\n\t------------------\n')
        inst_count -= 1


if __name__ == '__main__':
    main()
