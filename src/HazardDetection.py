"""
Hazard Detection Unit and forwarding unit (Without library)

"""


def hazard_detection(instr: str):
    global if_id, id_ex, ex_mem, mem_wb, alu_inp1, alu_inp2

    # ------- for raw hazard of r-type instructions -------
    # ex hazard:
    if ex_mem['REGWRITE'] and ex_mem['RD'] != '00000' and ex_mem['RD'] == instr[6:11]:
        alu_inp1 = ex_mem['RD'].value

    # mem hazard:
    elif mem_wb['REGWRITE'] and mem_wb['RD'] != '00000' and mem_wb['RD'] == instr[6:11]:
        alu_inp1 = mem_wb['RD'].value

    # ex hazard:
    if ex_mem['REGWRITE'] and ex_mem['RD'] != '00000' and ex_mem['RD'] == instr[11:16]:
        alu_inp2 = ex_mem['RD'].value

    # mem hazard:
    elif mem_wb['REGWRITE'] and mem_wb['RD'] != '00000' and mem_wb['RD'] == instr[11:16]:
        alu_inp2 = mem_wb['RD'].value

    # ------- for raw hazard of load-use data hazard -------
    # if id_ex['MEMREAD'] and id_ex['RT'] != '00000' and (id_ex['RT'] == instr[6:11] or id_ex['RT'] == instr[11:16]):
    #    # stall -> force control signals to 0. ex, mem, wb do no operation. and prevent update of pc and if/id register (instruction will decode again)
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
    
