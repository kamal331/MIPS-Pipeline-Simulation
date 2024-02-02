"""
_summary_
    parrallel MIPS simulator with 2-way MSI cache coherence protocol
_Author_: Mohammad Kamal
_Date_: 2024-02-02
_Version_: 1.0.0

_Features_
    I) To design a hardware, we have to consider some important factors:
        1) Scalability: the ability to add more modules to the system.
        2) Performance: the ability to execute instructions as fast as possible.
        3) Reliability: the ability to execute instructions without errors.
        4) Power consumption: the ability to execute instructions with the
           least power consumption.
        
        This is a hardware simulation and hardwares can't be changed easily, so 
        we have to consider these factors in the code.
        1) Scalability: Modules are seperated and can be added or removed easily.
        2) Performance: The code is staticly and dynamically analyzed to 
            find the bottlenecks and optimize them.
        3) Reliability: The code is tested with different test cases. And dynamicly
            checked for errors.
        4) Power consumption: The code is optimized to use lower power consumption.

    II) Code is type-hinted, analyzed and optimized with:
        + Pylint (famous open-source static code analysis tool)
        + mypy (static type checker for python)
        + Pylance (Microsoft static code analysis tool)
        + Bandit (a tool designed to find common security issues in Python code)
        + Snyk (leading platform for automated security)
        + CodeQL
        + Sonar
        + Deepsource (for static and dynamic analysis of the code)
          NOTE: Deepsource analysis include:
              - Performance Issues
              - Style Issues
              - Anti-patterns
              - Security Issues
              - Documentation Issues
              - Bug Risk
              and NONE of them found any issue in the code :)
    
    III) The code is on GitHub and is version controlled.
   
    IV) The code has good structure and commenting.

    V) The code uses colored output for better readability.





"""
import sys
from termcolor import colored
from Register import RegFile
from Cache import data_cache, inst_mem
from Alu import ALU
from BinFuncs import sign_extend, bin_to_int_signed, bin_to_int_unsigned
from PipelineRegister import PipelineRegister


# ************************** Pre-Defined Variables **************************

if_id = PipelineRegister('if_id', {'PC': '0'*5, 'RD': '0'*5, 'RT': '0'*5,
                         'RS': '0'*5, 'SHAMT': '0'*5, 'FUNCT': '0'*6,
                                   'OPCODE': '0'*6, 'IR': '0'*32})

id_ex = PipelineRegister('id_ex', {'PC': '0'*32, 'RD': '0'*5, 'RT': '0'*5,
                                   'RS': '0'*5, 'SHAMT': '0'*5,
                                   'FUNCT': '0'*6, 'OPCODE': '0'*6,
                                   'IR': '0'*32, 'REG_DST': '0',
                                   'ALU_SRC': '0'*2, 'MEM_TO_REG': '0',
                                   'ZERO': '0', 'ALUT_OP': '0'*2,
                                   'MEM_READ': '0',
                                   'MEM_WRITE': '0', 'BRANCH': '0',
                                   'REG_WRITE': '0'})

ex_mem = PipelineRegister('ex_mem', {'PC': '0'*32, 'RD': '0'*5, 'RT': '0'*5,
                                     'RS': '0'*5, 'SHAMT': '0'*5,
                                     'FUNCT': '0'*6, 'OPCODE': '0'*6,
                                     'IR': '0'*32, 'REG_DST': '0',
                                     'ALU_SRC': '0'*2, 'MEM_TO_REG': '0',
                                     'ALUT_OP': '0'*2, 'MEM_READ': '0',
                                     'MEM_WRITE': '0', 'BRANCH': '0',
                                     'REG_WRITE': '0', 'ALU_OUT': '0'*32,
                                     'ZERO': '0',
                                     'RDVAL': '0'*32,
                                     'RSVAL': '0'*32, 'RTVAL': '0'*32})

mem_wb = PipelineRegister('mem_wb', {'PC': '0'*32, 'RD': '0'*5, 'RT': '0'*5,
                                     'RS': '0'*5, 'SHAMT': '0'*5,
                                     'FUNCT': '0'*6, 'OPCODE': '0'*6,
                                     'IR': '0'*32, 'REG_DST': '0',
                                     'ALU_SRC': '0'*2, 'MEM_TO_REG': '0',
                                     'ALUT_OP': '0'*2, 'MEM_READ': '0',
                                     'MEM_WRITE': '0', 'BRANCH': '0',
                                     'REG_WRITE': '0', 'ALU_OUT': '0'*32,
                                     'ZERO': '0',
                                     'RDVAL': '0'*32,
                                     'RSVAL': '0'*32, 'RTVAL': '0'*32})


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


reg_file = RegFile()
# initialize reg_file:
for i in range(32):
    reg_file[f'${i}'] = 0

alu = ALU()
alu_inp1 = alu_inp2 = alu_out = zero_flag = pc = stall_count = 0


# ************************** Helper Functions **************************

def hazard_detection(instr: str) -> None:
    """_summary_

    Args:
        instr (str): 32-bit binary string of the instruction
    """
    global alu_inp1, alu_inp2  # skipcq: PYL-W0603

    # ------- for raw hazard of r-type instructions -------
    # ex hazard:
    if ex_mem['REG_WRITE'] and ex_mem['RD'] != '00000' and ex_mem['RD'] == instr[6:11]:
        alu_inp1 = ex_mem['RDVAL']

    # mem hazard:
    elif mem_wb['REG_WRITE'] and mem_wb['RD'] != '00000' and mem_wb['RD'] == instr[6:11]:
        alu_inp1 = mem_wb['RDVAL']

    # ex hazard:
    if ex_mem['REG_WRITE'] and ex_mem['RD'] != '00000' and ex_mem['RD'] == instr[11:16]:
        alu_inp2 = ex_mem['RDVAL']

    # mem hazard:
    elif mem_wb['REG_WRITE'] and mem_wb['RD'] != '00000' and mem_wb['RD'] == instr[11:16]:
        alu_inp2 = mem_wb['RDVAL']
    # ------- for raw hazard of load-use data hazard -------
        # if id_ex['MEMREAD'] and id_ex['RT'] != '00000' and \
        # (id_ex['RT'] == instr[6:11] or id_ex['RT'] == instr[11:16]):
        #    # stall -> force control signals to 0. ex, mem, wb do no operation.
        #      and prevent update of pc and if/id register (instruction will decode again)
        #     id_ex['REGWRITE'] = 0
        #     id_ex['MEMTOREG'] = 0
        #     id_ex['MEMREAD'] = 0
        #     id_ex['MEMWRITE'] = 0
        #     id_ex['ALUOP'] = '00'  # no operation
        #     id_ex['ALUSRC'] = 0
        #     id_ex['PCWRITE'] = 0
        #     id_ex['PCSRC'] = '00'  # no operation
        #     id_ex['IFIDWRITE'] = 0
        #     id_ex['PC'] = id_ex['PC'] - 4  # pc will not update
        #     if_id['PC'] = if_id['PC'] - 4
        #     print('---- stall ----')
        #     return True

        # # ------- branch hazard -------


def update_if_id() -> None:
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
    if inst == '0' * 32 or opcode == 'break':
        id_ex['REG_DST'] = '0'
        id_ex['ALU_SRC'] = '00'
        id_ex['MEM_TO_REG'] = '0'
        id_ex['ALUT_OP'] = '00'
        id_ex['MEM_READ'] = '0'
        id_ex['MEM_WRITE'] = '0'
        id_ex['BRANCH'] = '0'
        id_ex['REG_WRITE'] = '0'
    elif is_rtype(opcode):
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
        if opcode == 'lw':
            id_ex['MEM_TO_REG'] = '1'
            id_ex['ALUT_OP'] = '00'
            id_ex['MEM_READ'] = '1'
            id_ex['MEM_WRITE'] = '0'
            id_ex['REG_DST'] = '0'
        elif opcode == 'sw':
            id_ex['ALUT_OP'] = '00'
            id_ex['MEM_READ'] = '0'
            id_ex['MEM_WRITE'] = '1'
            id_ex['REG_DST'] = '0'
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

    mem_wb['REG_DST'] = ex_mem['REG_DST']
    mem_wb['ALU_SRC'] = ex_mem['ALU_SRC']
    mem_wb['MEM_TO_REG'] = ex_mem['MEM_TO_REG']
    mem_wb['ALUT_OP'] = ex_mem['ALUT_OP']
    mem_wb['MEM_READ'] = ex_mem['MEM_READ']
    mem_wb['MEM_WRITE'] = ex_mem['MEM_WRITE']
    mem_wb['BRANCH'] = ex_mem['BRANCH']
    mem_wb['REG_WRITE'] = ex_mem['REG_WRITE']
    mem_wb['ALU_OUT'] = ex_mem['ALU_OUT']
    mem_wb['RDVAL'] = ex_mem['RDVAL']


# ************************** Fetch **************************

def fetch() -> None:
    # get instruction from memory
    inst = inst_mem[pc]
    text = colored('instruction fetched: ✅', 'yellow')
    print(text)
    print(inst)


def is_rtype(name: str) -> bool:
    return name in ['add', 'sub', 'and', 'or', 'xor', 'nor', 'slt', 'sll',
                    'srl', 'jr', 'syscall', 'break', 'mult']


def is_itype(name: str) -> bool:
    return name in ['addi', 'andi', 'ori', 'xori', 'beq', 'bne', 'lw', 'sw']


def is_branch(name: str) -> bool:
    return name in ['beq', 'bne']


def print_decoded_inst() -> None:
    # get instruction from if_id
    try:
        opcode = bin_to_inst_dict[(if_id['OPCODE'], if_id['FUNCT'])]
    except KeyError:
        opcode = bin_to_inst_dict[(if_id['OPCODE'], 'xxxxxx')]

    text = colored('instruction decoded: ✅', 'yellow')
    print(text)
    if if_id['IR'] == '0'*32:
        print('nop')
    elif opcode == 'break':
        print('break')
    elif is_rtype(opcode):
        print(opcode, bin_to_regname[if_id['RD']], bin_to_regname[if_id['RS']],
              bin_to_regname[if_id['RT']])
    elif is_itype(opcode):
        print(opcode, bin_to_regname[if_id['RT']], bin_to_regname[if_id['RS']],
              sign_extend(bin_to_int_signed(if_id['IR'][16:], 16), 16))
    elif is_branch(opcode):
        print(opcode, bin_to_regname[if_id['RS']], bin_to_regname[if_id['RT']],
              sign_extend(bin_to_int_signed(if_id['IR'][16:], 16), 16))


# ************************** Decode **************************
def decode() -> None:
    print_decoded_inst()


# ************************** Execute **************************

def ex_rtype(inst: str, opcode: str) -> None:
    global alu_inp1, alu_inp2, alu_out  # skipcq: PYL-W0603

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

    hazard_detection(inst)

    rd = bin_to_regname[inst[16:21]]
    rs = bin_to_regname[inst[6:11]]
    rt = bin_to_regname[inst[11:16]]
    if opcode == 'add':
        alu_out = alu.add(alu_inp1, alu_inp2)
        print('add', rd, rs, rt, '=', alu_out)

    elif opcode == 'sub':
        alu_out = alu.sub(alu_inp1, alu_inp2)
        print('sub', rd, rs, rt)

    elif opcode == 'and':
        alu_out = alu.and_(alu_inp1, alu_inp2)
        print('and', rd, rs, rt)

    elif opcode == 'or':
        alu_out = alu.or_(alu_inp1, alu_inp2)
        print('or', rd, rs, rt)

    elif opcode == 'xor':
        alu_out = alu.xor(alu_inp1, alu_inp2)
        print('xor', rd, rs, rt)

    elif opcode == 'nor':
        alu_out = alu.nor(alu_inp1, alu_inp2)
        print('nor', rd, rs, rt)
    elif opcode == 'mult':
        alu_out = alu.mult(alu_inp1, alu_inp2)
        print('mult', rs, rt)

    elif opcode == 'sll':
        alu_out = alu.sll(alu_inp1, bin_to_int_unsigned(inst[21:26]))
        print('sll', rd, bin_to_regname[inst[11:16]],
              bin_to_int_unsigned(inst[21:26]))

    elif opcode == 'srl':
        alu_out = alu.srl(alu_inp1, bin_to_int_unsigned(inst[21:26]))
        print('srl', rd, bin_to_regname[inst[11:16]],
              bin_to_int_unsigned(inst[21:26]))
    ex_mem['RDVAL'] = alu_out


def ex_itype(inst: str, opcode: str) -> None:
    global alu_inp1, alu_inp2, alu_out  # skipcq: PYL-W0603
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
              '(', bin_to_regname[inst[6:11]], ')', 'address =>', alu_out)
    elif opcode == 'sw':
        alu_out = alu.add(alu_inp1, alu_inp2)
        print('sw', bin_to_regname[inst[11:16]], bin_to_int_signed(inst[16:], 16),
              '(', bin_to_regname[inst[6:11]], ')', 'address =>', alu_out)
    elif opcode == 'beq':
        if alu_inp1 == alu_inp2:
            id_ex['BRANCH'] = '1'
            print('beq', bin_to_regname[inst[6:11]], bin_to_regname[inst[11:16]],
                  bin_to_int_signed(inst[16:], 16), '=> branch taken')
        else:
            id_ex['BRANCH'] = '0'
            print('beq', bin_to_regname[inst[6:11]], bin_to_regname[inst[11:16]],
                  bin_to_int_signed(inst[16:], 16), '=> branch not taken')
    ex_mem['RDVAL'] = alu_out


def execute() -> None:
    inst = id_ex['IR']

    try:
        opcode = bin_to_inst_dict[(id_ex['OPCODE'], id_ex['FUNCT'])]
    except KeyError:
        opcode = bin_to_inst_dict[(id_ex['OPCODE'], 'xxxxxx')]

    text = colored('execution', 'yellow')
    print(text)
    if inst == '0' * 32:
        print('nop')

    elif opcode == 'break':
        print('break')

    elif is_rtype(opcode):
        ex_rtype(inst, opcode)
    elif is_itype(opcode):
        ex_itype(inst, opcode)
    elif is_branch(opcode):
        # branch(opcode)
        pass


# ************************** Memory **************************

def working_with_cache() -> None:
    inst = ex_mem['IR']
    try:
        opcode = bin_to_inst_dict[(ex_mem['OPCODE'], ex_mem['FUNCT'])]
    except KeyError:
        opcode = bin_to_inst_dict[(ex_mem['OPCODE'], 'xxxxxx')]

    text = colored('working with cache/mem:', 'yellow')
    print(text)
    if opcode == 'lw':
        ex_mem['ALU_OUT'] = data_cache[alu_out]
        print('lw', bin_to_regname[inst[11:16]], bin_to_int_signed(inst[16:], 16),
              '(', bin_to_regname[inst[6:11]], ')', 'value: ', ex_mem['ALU_OUT'])

    elif opcode == 'sw':
        data_cache[alu_out] = sign_extend(
            reg_file[f'${bin_to_int_unsigned(inst[11:16])}'].val, 32)
        ex_mem['ALU_OUT'] = sign_extend(
            reg_file[f'${bin_to_int_unsigned(inst[11:16])}'].val, 32)
        print('sw:', '\nin location:', bin_to_int_signed(inst[16:], 16), ', value:',
              reg_file[f'${bin_to_int_unsigned(inst[11:16])}'].val, 'must be saved')

    else:
        print('no cache needed for this instruction 🙄')


# ************************** Write Back **************************

def write_back() -> None:
    inst = mem_wb['IR']

    try:
        opcode = bin_to_inst_dict[(mem_wb['OPCODE'], mem_wb['FUNCT'])]
    except KeyError:
        opcode = bin_to_inst_dict[(mem_wb['OPCODE'], 'xxxxxx')]
    text = colored('write_back_opcode:', 'yellow')

    if inst == '0' * 32:
        print(text, 'nop')
    elif opcode == 'break':
        print(text, 'break')

    else:
        print(text, opcode)
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

        elif mem_wb['MEM_READ'] == '1':
            print('lw', bin_to_regname[inst[11:16]], bin_to_int_signed(inst[16:], 16),
                  '(', bin_to_regname[inst[6:11]], ')', '=', mem_wb['ALU_OUT'])
        elif mem_wb['MEM_WRITE'] == '1':
            print('sw:', '\nin location:', bin_to_int_signed(inst[16:], 16), ', value:',
                  reg_file[f'${bin_to_int_unsigned(inst[11:16])}'].val, ' saved')
        elif opcode == 'jr':
            print('jr', bin_to_regname[inst[6:11]])
        elif opcode == 'jal':
            print('jal', bin_to_regname[inst[6:11]])
        elif opcode == 'j':
            print('j', bin_to_regname[inst[6:11]])


# *********************** main ***********************


def license() -> None:
    print(colored('''
    MIT License
    -----------
    (c) 2024 Mohammad Kamal
    Permission is hereby granted, free of charge, to any person obtaining a copy
    of this software and associated documentation files (the "Software"), to deal
    in the Software without restriction, including without limitation the rights
    to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
    copies of the Software, and to permit persons to whom the Software is
    furnished to do so, subject to the following conditions:
    The above copyright notice and this permission notice shall be
    included in all copies or substantial portions of the Software.
    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
    EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
    OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
    IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
    DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
    ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
    IN THE SOFTWARE.
    ''', 'green'))
    input('Enter any key to back to menu: ')


def simulate() -> None:
    global pc  # skipcq: PYL-W0603
    try:
        with open('instructions.txt', 'r', encoding='utf-8') as f:
            inst_i = 0
            for line in f:
                inst_mem[inst_i] = line.strip()
                inst_i += 1
    except FileNotFoundError:
        print('file not found')
        return
    except Exception as _:
        print('something went wrong')

    pc_write = if_id_write = True

    inst_count = inst_i + 1
    pipeline_stage_no = 5
    total_pipeline_clocks = inst_count + pipeline_stage_no - 1
    cycle_seperator = colored('==================', 'magenta')
    stage_seperator = colored('------------------', 'green')
    k = 0
    while k < total_pipeline_clocks + stall_count:
        if pc_write and if_id_write:
            fetch()
            print(stage_seperator)

            decode()
            print(stage_seperator)

            execute()
            print(stage_seperator)

            working_with_cache()
            print(stage_seperator)

            write_back()
            # write data cache to file:
            with open('data_cache.txt', 'a', encoding='utf-8') as f:
                f.write(str(data_cache))
                f.write('\n')

        print('\n\t', cycle_seperator, '\n')
        update_mem_wb()
        update_ex_mem()  # get from id_ex
        update_id_ex()  # get from if_id
        update_if_id()  # get from pc
        k += 1
        pc += 1
    print('throughput:', inst_count /
          ((total_pipeline_clocks+stall_count)*200e-12))
    print(reg_file)

    input('Press any key to continue: ')


def main() -> None:
    ASK_TEXT = colored('What do you want to do? (simulate, license, exit): ',
                       'magenta')
    CHOICE1 = colored('1. simulate', 'green')
    CHOICE2 = colored('2. license', 'blue')
    CHOICE3 = colored('3. exit', 'yellow')
    CLEAR_TERMINAL = '\033[H\033[J'
    while True:
        print(f'{ASK_TEXT}\n{CHOICE1}\n{CHOICE2}\n{CHOICE3}')
        choice = input()
        while choice not in ['1', '2', '3']:
            print(colored('invalid input', 'red'))
            print(f'{ASK_TEXT}\n{CHOICE1}\n{CHOICE2}\n{CHOICE3}')
            choice = input()
        if choice == '1':
            simulate()
        elif choice == '2':
            license()
        else:
            sys.exit()
        print(CLEAR_TERMINAL)


if __name__ == '__main__':
    main()
