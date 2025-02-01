# LC3 state machine emulator

# Based on Introduction to Computing Systems: From Bits & Gates to C/C++ & Beyond
# https://www.mheducation.com/highered/product/Introduction-to-Computing-Systems-From-Bits-and-Gates-to-C-C%2B%2B-and-Beyond-Patt.html


# Bit string functions

class BitString:
    def __init__(self):
        self.bits = 0b0
        
    def append_int(self, shift, data):
        self.bits <<= shift
        self.bits |= data
        
    def append_bool(self, data):
        self.bits <<= 1
        if data:
            self.bits |= 0b1
        
# Logging functions

log_level = 3

def set_log_level(level):
    global log_level
    log_level = level
    
def log(depth, x):
        if (depth <= log_level):
            print("    " * depth, x)

# Binary manipulation

# Check if this bit is set (bits start at 0, so would be 0 to 15)

def check_bit(value, bit):
    return value & (1 << bit) != 0

# Sign extend or zero extend a value, number of bits in the number, so 5:0 is 6 bits

def sign_extend(value, number_bits):
    top_mask    = (0xffff << number_bits) & 0xffff
    bottom_mask = (~top_mask) & 0xffff
    new_value = value & bottom_mask
    if check_bit(value, number_bits - 1):
        new_value = new_value | top_mask
#    print(f"{value:4x} {top_mask:4x} {bottom_mask:4x} {new_value:4x}")
    return new_value

def zero_extend(value, number_bits):
    top_mask    = (0xffff << number_bits) & 0xffff
    bottom_mask = (~top_mask) & 0xffff
    new_value = value & bottom_mask

    return new_value    

# Definitions for Contol Unit - which are just signal names
# Everything in this class can be accessed by other classes

from enum import IntEnum

class PCMux(IntEnum):
    PC_PLUS_1 = 0
    BUS       = 1
    ADDER     = 2

class DRMux(IntEnum):
    IR_11_9 = 0
    SP      = 1      # R6
    R7      = 2      # R6
    
class SR1Mux(IntEnum):
    IR_11_9 = 0
    IR_8_6  = 1
    SP      = 2      # R6
    
class ADDR1Mux(IntEnum):
    PC     = 0
    BASE_R = 1

class ADDR2Mux(IntEnum):
    ZERO         = 0
    OFFSET_6     = 1
    PC_OFFSET_9  = 2
    PC_OFFSET_11 = 3

class SPMux(IntEnum):
    SP_PLUS_1  = 0
    SP_MINUS_1 = 1
    SAVES_SSP  = 2
    SAVED_USP  = 3

class MARMux(IntEnum):
    IR_7_0 = 0
    ADDER  = 1

class TABLEMux(IntEnum):
    X_00 = 0
    X_01 = 1

class VECTORMux(IntEnum):
    INTV           = 0
    PRIV_EXCEPTION = 1
    OPC_EXCEPTION  = 2
    ACV_EXCEPTION  = 3

class PSRMux(IntEnum):
    INDIVIDUAL = 0
    BUS        = 1

class ALUK(IntEnum):
    ADD   = 0
    AND   = 1
    NOT   = 2
    PASSA = 3
    
class MemRW(IntEnum):
    RD = 0
    WR = 1
    
class Priv(IntEnum):
    SUPER = 0
    USER = 1

## Additional enums

class COND(IntEnum):
    UNCONDITIONAL   = 0
    MEMORY_READY    = 1
    BRANCH          = 2
    ADDRESSING_MODE = 3
    PRIVILEGE_MODE  = 4
    INTERRUPT_TEST  = 5
    ACV_TEST        = 6


# Control Unit class
    
class ControlUnit():
    def clear_control_signals(self):
        # From C.3 The Data Path p705
        
        # LD signals
        self.LD_MAR          = False
        self.LD_MDR          = False
        self.LD_IR           = False
        self.LD_BEN          = False
        self.LD_REG          = False
        self.LD_CC           = False
        self.LD_PC           = False

        # LD signals - privilege and exceptions
        self.LD_PRIV         = False
        self.LD_PRIORITY     = False
        self.LD_SAVED_SSP    = False
        self.LD_SAVED_USP    = False
        self.LD_ACV          = False
        self.LD_VECTOR       = False

        # Core gates
        self.GATE_PC         = False
        self.GATE_MDR        = False
        self.GATE_ALU        = False
        self.GATE_MARMUX     = False
        
        # Vector / interrupt / exception gates
        self.GATE_VECTOR     = False
        self.GATE_PC_MINUS_1 = False
        self.GATE_PSR        = False
        self.GATE_SP         = False

        # MUX
        self.PC_MUX          = PCMux.PC_PLUS_1
        self.DR_MUX          = DRMux.IR_11_9
        self.SR1_MUX         = SR1Mux.IR_11_9
        self.ADDR1_MUX       = ADDR1Mux.PC
        self.ADDR2_MUX       = ADDR2Mux.ZERO
        self.SP_MUX          = SPMux.SP_PLUS_1
        self.MAR_MUX         = MARMux.IR_7_0
        self.PSR_MUX         = PSRMux.INDIVIDUAL
        self.ALUK            = ALUK.PASSA

        self.TABLE_MUX       = TABLEMux.X_00
        self.VECTOR_MUX      = VECTORMux.INTV

        # Memory signals
        self.MIO_EN          = False
        self.RW              = MemRW.RD

        # Processor privilege level signals
        self.SET_PRIV        = Priv.USER

        # Internal stores
        self.MAR_MUX_OUT     = 0
        self.ALU_OUT         = 0
        self.PC_MUX_OUT      = 0
        self.ADDR2_MUX_OUT   = 0
        self.ADDR1_MUX_OUT   = 0
        self.ADDR_ADD_OUT    = 0
        self.SR1_OUT         = 0
        self.SR2_OUT         = 0
        self.SR2_MUX_OUT     = 0
        self.ACV_OUT         = 0
        self.BEN_OUT         = 0
        self.MEMORY_OUT      = 0
        
    def clear_state_signals(self):
        self.J = 0
        self.COND = COND.UNCONDITIONAL
        self.IRD = False       

    def clear_registers(self):
        # General purpose registers
        self.regs = [0, 0, 0, 0, 0 ,0, 0, 0]
        
        # Control Unit registers
        self.PC = 0x3000
        self.IR = 0
        self.PSR = 0b1000_0000_0000_0000
        self.bus = 0

        # Memory access registers
        self.MDR = 0
        self.MAR = 0
        self.R = False

    def clear_logic(self):
        self.BEN = False
        self.ACV = False

        self.SR1 = 0
        self.SR2 = 0
        self.DR = 0
        
        # Non-state signals
        self.INT = False

        self.N = False
        self.Z = False
        self.P = False
        
    def __init__(self):
        # Stored state table (generated by code)
        self.state_matrix = {}
        
        self.clear_control_signals()
        self.clear_state_signals()
        self.clear_registers()
        self.clear_logic()
       
        self.state = 18 # start at state 18

    def store_state(self):
        config = BitString()
        config.append_bool(self.IRD)
        config.append_int(3, self.COND)
        config.append_int(6, self.J)
        config.append_bool(self.LD_MAR)
        config.append_bool(self.LD_MDR)
        config.append_bool(self.LD_IR)
        config.append_bool(self.LD_BEN)
        config.append_bool(self.LD_REG)
        config.append_bool(self.LD_CC)
        config.append_bool(self.LD_PC)
        config.append_bool(self.LD_PRIV)
        config.append_bool(self.LD_SAVED_SSP)
        config.append_bool(self.LD_SAVED_USP)
        config.append_bool(self.LD_VECTOR)
        config.append_bool(self.LD_PRIORITY)
        config.append_bool(self.LD_ACV)
        config.append_bool(self.GATE_PC)
        config.append_bool(self.GATE_MDR)
        config.append_bool(self.GATE_ALU)
        config.append_bool(self.GATE_MARMUX)
        config.append_bool(self.GATE_VECTOR)
        config.append_bool(self.GATE_PC_MINUS_1)
        config.append_bool(self.GATE_PSR)
        config.append_bool(self.GATE_SP)
        config.append_int(2, self.PC_MUX)
        config.append_int(2, self.DR_MUX)
        config.append_int(2, self.SR1_MUX)
        config.append_int(1, self.ADDR1_MUX)
        config.append_int(2, self.ADDR2_MUX)
        config.append_int(2, self.SP_MUX)
        config.append_int(1, self.MAR_MUX)        
        config.append_int(1, self.TABLE_MUX)
        config.append_int(2, self.VECTOR_MUX)
        config.append_int(1, self.PSR_MUX)
        config.append_int(2, self.ALUK)
        config.append_bool(self.MIO_EN)
        config.append_bool(self.RW)
        config.append_bool(self.SET_PRIV)

        self.state_matrix[self.state] = config.bits
        
    def set_control_signals(self):
        # do this manually for now, can implement in a bitmap later
        self.clear_control_signals()
        log(1, f"State {self.state}")

        if   self.state == 0b0000:
            log(1, "BR NZP PC + offset9")
            log(2, "|BEN|")
            self.COND = COND.BRANCH
            self.J = 18     # 18 or 22       
        elif self.state == 0b0001:
            log(1, "ADD DR, SR1, (SR2 / SEXT[imm5])")
            log(2, "DR <- SR1 + (SR2 / SEXT[imm5])")
            self.SR1_MUX = SR1Mux.IR_8_6
            self.LD_REG = True
            self.LD_CC = True
            self.ALUK = ALUK.ADD
            self.GATE_ALU = True
            self.J = 18
        elif self.state == 0b0010:
            log(1, "LD DR, PC + offset9")
            log(2, "MAR <- PC + off9, set ACV")
            self.LD_MAR = True
            self.LD_ACV = True
            self.ADDR2_MUX = ADDR2Mux.PC_OFFSET_9
            self.ADDR1_MUX = ADDR1Mux.PC
            self.MAR_MUX = MARMux.ADDER
            self.SR1_MUX  = SR1Mux.IR_11_9 
            self.GATE_MARMUX = True
            self.J = 35
        elif self.state == 0b0011:
            log(1, "ST SR1, PC + offset9")
            log(2, "MAR <- PC + off9, set ACV")
            self.LD_MAR = True
            self.LD_ACV = True
            self.ADDR2_MUX = ADDR2Mux.PC_OFFSET_9
            self.ADDR1_MUX = ADDR1Mux.PC
            self.MAR_MUX = MARMux.ADDER
            self.SR1_MUX  = SR1Mux.IR_11_9 
            self.GATE_MARMUX = True
            self.J = 23
        elif self.state == 0b0100:
            log(1, "JSR BR / PC + offset11")
            log(2, "| IR[11] |")
            self.COND = COND.ADDRESSING_MODE
            self.J = 20
        elif self.state == 0b0101:
            log(1, "AND DR, SR1, (SR2 / SEXT[imm5])")
            log(2, "DR <- SR1 & (SR2 / SEXT[imm5])")
            self.SR1_MUX = SR1Mux.IR_8_6
            self.LD_REG = True
            self.LD_CC = True
            self.ALUK = ALUK.AND
            self.GATE_ALU = True
            self.J = 18
        elif self.state == 0b0110:
            log(1, "LDR DR, BR + offset6")
            log(2, "MAR <- BR + off6, set ACV")
            self.LD_MAR = True
            self.LD_ACV = True
            self.ADDR2_MUX = ADDR2Mux.OFFSET_6
            self.ADDR1_MUX = ADDR1Mux.BASE_R
            self.MAR_MUX = MARMux.ADDER
            self.SR1_MUX  = SR1Mux.IR_8_6 
            self.GATE_MARMUX = True
            self.J = 35
        elif self.state == 0b0111:
            log(1, "STR DR, BR + offset6")
            log(2, "MAR <- BR + off6, set ACV")
            self.LD_MAR = True
            self.LD_ACV = True
            self.ADDR2_MUX = ADDR2Mux.OFFSET_6
            self.ADDR1_MUX = ADDR1Mux.BASE_R
            self.MAR_MUX = MARMux.ADDER
            self.SR1_MUX  = SR1Mux.IR_8_6 
            self.GATE_MARMUX = True
            self.J = 23
        elif self.state == 0b1000:
            log(1, "*** RTI NOT IMPLEMENTED ***")
            self.J = 18
        elif self.state == 0b1001:
            log(1, "NOT DR, SR")
            log(2, "DR <- NOT(SR1)")
            self.SR1_MUX = SR1Mux.IR_8_6
            self.LD_REG = True
            self.LD_CC = True
            self.ALUK = ALUK.NOT
            self.GATE_ALU = True
            self.J = 18
        elif self.state == 0b1010:
            log(1, "LDI DR, PC + offset9")
            log(2, "MAR <- PC + off9, set ACV")
            self.LD_MAR = True
            self.LD_ACV = True
            self.ADDR2_MUX = ADDR2Mux.PC_OFFSET_9
            self.ADDR1_MUX = ADDR1Mux.PC
            self.MAR_MUX = MARMux.ADDER
            self.SR1_MUX  = SR1Mux.IR_11_9 
            self.GATE_MARMUX = True
            self.J = 17
        elif self.state == 0b1011:
            log(1, "STI SR, PC + offset9")
            log(2, "MAR <- PC + off9, set ACV")
            self.LD_MAR = True
            self.LD_ACV = True
            self.ADDR2_MUX = ADDR2Mux.PC_OFFSET_9
            self.ADDR1_MUX = ADDR1Mux.PC
            self.MAR_MUX = MARMux.ADDER
            self.SR1_MUX  = SR1Mux.IR_11_9 
            self.GATE_MARMUX = True
            self.J = 19
        elif self.state == 0b1100:
            log(1, "JMP BR")
            log(2, "PC <- BR")
            self.ADDR2_MUX = ADDR2Mux.ZERO
            self.ADDR1_MUX = ADDR1Mux.BASE_R
            self.SR1_MUX = SR1Mux.IR_8_6
            self.PC_MUX = PCMux.ADDER
            self.LD_PC = True
            self.J = 18
        elif self.state == 0b1110:
            log(1, "LEA DR, PC + offset9")
            log(2, "DR <- PC + off9")
            self.ADDR2_MUX = ADDR2Mux.PC_OFFSET_9
            self.ADDR1_MUX = ADDR1Mux.PC
            self.MAR_MUX = MARMux.ADDER
            self.DR_MUX  = DRMux.IR_11_9 
            self.GATE_MARMUX = True
            self.LD_REG = True
            self.J = 18
        elif self.state == 0b1111:
            log(1, "*** TRAP NOT IMPLEMENTED ***")
            self.J = 18
        elif self.state == 16:
            log(2, "Mem[MAR] <- MDR, wait R")
            self.MIO_EN = True
            self.RW = MemRW.WR
            self.COND = COND.MEMORY_READY            
            self.J = 16 # same value, to loop until memory ready
        elif self.state == 17:
            log(2, "|ACV|")            
            self.COND = COND.ACV_TEST
            self.J = 24 # or 56
        elif self.state == 18:
            log(2, "MAR <- PC, PC <- PC + 1, set ACV, |INT|")
            log(3, f"PC: 0x{self.PC:4x}")
            self.LD_MAR = True
            self.LD_PC = True
            self.LD_ACV = True
            self.PC_MUX = PCMux.PC_PLUS_1
            self.GATE_PC = True
            self.COND = COND.INTERRUPT_TEST
            self.J = 33
        elif self.state == 19:
            log(2, "|ACV|")            
            self.COND = COND.ACV_TEST
            self.J = 29 # or 61
        elif self.state == 20:
            log(1, "---JSR BR")
            log(2, "R7 <- PC, PC <- BR")
            self.ADDR2_MUX = ADDR2Mux.ZERO
            self.ADDR1_MUX = ADDR1Mux.BASE_R
            self.SR1_MUX = SR1Mux.IR_8_6
            self.PC_MUX = PCMux.ADDER
            self.LD_PC = True
            self.GATE_PC = True
            self.LD_REG = True
            self.DR_MUX = DRMux.R7
            self.J = 18
        elif self.state == 21:
            log(1, "---JSR PC + offset11")
            log(2, "R7 <- PC, PC <- PC + off11")
            self.LD_PC = True
            self.ADDR2_MUX = ADDR2Mux.PC_OFFSET_11
            self.ADDR1_MUX = ADDR1Mux.PC
            self.PC_MUX = PCMux.ADDER
            self.GATE_PC = True
            self.LD_REG = True
            self.DR_MUX = DRMux.R7
            self.J = 18
        elif self.state == 22:
            log(2, "PC <- PC + off9")
            self.LD_PC = True
            self.ADDR2_MUX = ADDR2Mux.PC_OFFSET_9
            self.ADDR1_MUX = ADDR1Mux.PC
            self.PC_MUX = PCMux.ADDER
            self.J = 18
        elif self.state == 23:
            log(2, "MDR <- SR, |ACV|")
            self.LD_MDR = True
            self.ALUK = ALUK.PASSA
            self.GATE_ALU = True
            self.COND = COND.ACV_TEST
            self.J = 16
        elif self.state == 24:
            log(2, "MDR <- M, wait R")
            self.MIO_EN = True
            self.RW = MemRW.RD
            self.LD_MDR = True
            self.J = 24 # same value, to loop until memory ready
            self.COND = COND.MEMORY_READY
        elif self.state == 25:
            log(2, "MDR <- M, wait R")
            self.MIO_EN = True
            self.RW = MemRW.RD
            self.LD_MDR = True
            self.J = 25 # same value, to loop until memory ready
            self.COND = COND.MEMORY_READY
        elif self.state == 26:
            log(2, "MAR <- MDR, set ACV")
            self.LD_MAR = True        
            self.GATE_MDR = True
            self.LD_ACV = True
            self.J = 35
        elif self.state == 27:
            log(2, "DR <- MDR, set CC")
            self.LD_REG = True
            self.DR_MUX = DRMux.IR_11_9
            self.GATE_MDR = True
            self.LD_CC = True
            self.J = 18
        elif self.state == 28:
            log(2, "MDR <- M, wait R")
            self.MIO_EN = True
            self.RW = MemRW.RD
            self.LD_MDR = True
            self.J = 28 # same value, to loop until memory ready
            self.COND = COND.MEMORY_READY
        elif self.state == 29:
            log(2, "MDR <- M, wait R")
            self.MIO_EN = True
            self.RW = MemRW.RD
            self.LD_MDR = True
            self.J = 29 # same value, to loop until memory ready
            self.COND = COND.MEMORY_READY
        elif self.state == 30:
            log(2, "IR <- MDR")
            self.LD_IR = True
            self.GATE_MDR = True
            self.J = 32
        elif self.state == 31:
            log(2, "MAR <- MDR, set ACV")
            self.LD_MAR = True        
            self.GATE_MDR = True
            self.LD_ACV = True
            self.J = 23
        elif self.state == 32:
            log(3, "BEN <- (IR[11] & N) + (IR[10} & Z) + (IR[9] & P), |IR[15:12]|")
            self.LD_BEN = True
            self.J = 0               # Never needed
            self.IRD = True          # IRD is effectively |IR[15:12]|
        elif self.state == 33:
            log(2, "|ACV|")
            self.COND = COND.ACV_TEST
            self.J = 28
        elif self.state == 35:
            log(2, "|ACV|")
            self.COND = COND.ACV_TEST
            self.J = 25 # or 57
        else:
            print(f"MISSING CODE FOR INSTRUCTION {self.state}")
            self.J = 18


           
    def execute_logic(self):
        log(4, f"Logic: bus is 0x{self.bus:04x} ")
 
        # DR
        if self.DR_MUX == DRMux.IR_11_9:
            self.DR = (self.IR & 0x0e00) >> 9
        elif self.DR_MUX == DRMux.R7:
            self.DR = 0x7
        elif self.DR_MUX == DRMux.SP:
            self.DR = 0x6
        log(4, f"Logic: DR  is 0x{self.DR:02x} ")
        
        # SR1
        if self.SR1_MUX == SR1Mux.IR_11_9:
            self.SR1 = (self.IR & 0x0e00) >> 9
        elif self.SR1_MUX == SR1Mux.IR_8_6:
            self.SR1 = (self.IR & 0x01c0) >> 6
        elif self.SR1_MUX == SR1Mux.SP:
            self.SR1 = 0x6
        log(4, f"Logic: SR1 is 0x{self.SR1:02x} ")
        
        # SR2
        self.SR2 = (self.IR & 0x07)
        log(4, f"Logic: SR2 is 0x{self.SR2:02x} ")
        
        # ADDR2MUX
        if self.ADDR2_MUX == ADDR2Mux.ZERO:
            self.ADDR2_MUX_OUT = 0
        elif self.ADDR2_MUX == ADDR2Mux.OFFSET_6:
            self.ADDR2_MUX_OUT = sign_extend(self.IR, 6)
        elif self.ADDR2_MUX == ADDR2Mux.PC_OFFSET_9:
            self.ADDR2_MUX_OUT = sign_extend(self.IR, 9)
        elif self.ADDR2_MUX == ADDR2Mux.PC_OFFSET_11:
            self.ADDR2_MUX_OUT = sign_extend(self.IR, 11)
        log(4, f"Logic: ADDR2_MUX_OUT is 0x{self.ADDR2_MUX_OUT:04x} ")

        # REG FILE
        self.SR1_OUT = self.regs[self.SR1]
        self.SR2_OUT = self.regs[self.SR2]
        log(4, f"Logic: SR1_OUT is       0x{self.SR1_OUT:04x}")
        log(4, f"Logic: SR2_OUT is       0x{self.SR2_OUT:04x}")
        
        # ADDR1MUX
        if self.ADDR1_MUX == ADDR1Mux.PC:
            self.ADDR1_MUX_OUT = self.PC
        elif self.ADDR1_MUX == ADDR1Mux.BASE_R:
            self.ADDR1_MUX_OUT = self.SR1_OUT
        log(4, f"Logic: ADDR1MUX is      0x{self.ADDR1_MUX:04x} ")
        
        # ADDR_ADD
        self.ADDR_ADD_OUT = self.ADDR1_MUX_OUT + self.ADDR2_MUX_OUT
        log(4, f"Logic: ADDR_ADD_OUT is  0x{self.ADDR_ADD_OUT:04x} ")
        
        # MAR_MUX
        if self.MAR_MUX == MARMux.IR_7_0:
            self.MAR_MUX_OUT = zero_extend(self.IR, 8)
        elif self.MAR_MUX == MARMux.ADDER:
            self.MAR_MUX_OUT = self.ADDR_ADD_OUT
        log(4, f"Logic: MAR_MUX_OUT is   0x{self.MAR_MUX_OUT:04x} ")
        
        # Check to see if need to gate MAR_MUX
        if self.GATE_MARMUX:
            log(4, "MARMUX is gated onto main bus (after update)")
            self.bus = self.MAR_MUX_OUT

        # PC_MUX
        if self.PC_MUX == PCMux.PC_PLUS_1:
            self.PC_MUX_OUT = self.PC + 1
        elif self.PC_MUX == PCMux.BUS:
            self.PC_MUX_OUT = self.bus
        elif self.PC_MUX == PCMux.ADDER:
            self.PC_MUX_OUT = self.ADDR_ADD_OUT
        log(4, f"Logic: PC_MUX_OUT is    0x{self.PC_MUX_OUT:04x} ")
        
        # There is no need to check for gating PC_MUX
        # PC is controlled by LD_PC
 
        # SR2_MUX
        if check_bit(self.IR, 5):
            self.SR2_MUX_OUT = sign_extend(self.IR, 5)
        else:
            self.SR2_MUX_OUT = self.SR2_OUT
        log(4, f"Logic: SR2_MUX_OUT is   0x{self.SR2_MUX_OUT:04x} ")


        # ALU
        if   self.ALUK == ALUK.ADD:
            self.ALU_OUT = (self.SR2_MUX_OUT + self.SR1_OUT) & 0xffff
        elif self.ALUK == ALUK.AND:
            self.ALU_OUT = (self.SR2_MUX_OUT & self.SR1_OUT) & 0xffff
        elif self.ALUK == ALUK.NOT:
            self.ALU_OUT = (~self.SR1_OUT) & 0xffff
        elif self.ALUK == ALUK.PASSA:
            self.ALU_OUT = self.SR1_OUT
        log(4, f"Logic: ALU_OUT is       0x{self.ALU_OUT:04x} ")
        
        # Check to see if need to gate ALU
        if self.GATE_ALU:
            log(4, "ALU is gated onto main bus (after update)")
            self.bus = self.ALU_OUT       

        # Calculate BEN
        self.BEN_OUT = ((self.N and check_bit(self.IR, 11)) or
                        (self.Z and check_bit(self.IR, 10)) or
                        (self.P and check_bit(self.IR, 9)))
        log(4, f"Logic: BEN_OUT is {self.BEN_OUT} ")

        # Calculate ACV
        
        # ACV if PSR[15] set and either address is < 0x3000 or >= 0xfe00 
        # self.ACV = ( (self.bus & 0xfe00 == 0xfe00) or (self.bus & 0xc000 == 0x0000) )
        #           and check_bit(cu.PSR,15)
        self.ACV_OUT = check_bit(self.PSR, 15) and ((self.bus >= 0xfe00) or (self.bus < 0x3000))
        log(4, f"Logic: ACV_OUT is {self.ACV_OUT} ")


    # Do Gates
    # Missing GATE_VECTOR, GATE_PC_MINUS_1, GATE_PSR, GATE_SP
    
    def process_gating(self):
        if self.GATE_PC:
            log(3, "PC is gated onto main bus")
            self.bus = self.PC

        if self.GATE_MDR:
            log(3, "MDR is gated onto main bus")
            self.bus = self.MDR

        if self.GATE_ALU:
            log(3, "ALU is gated onto main bus")
            self.bus = self.ALU_OUT        

        if self.GATE_MARMUX:
            log(3, "MARMUX is gated onto main bus")
            self.bus = self.MAR_MUX_OUT

    # Determine the next state of the state machine
    # Uses COND, IRD, IR, R, BEN, PSR, INT, ACV
    
    def set_new_state(self):
        # IRD
        if self.IRD:
            # IR[15:12]
            new_J = (self.IR & 0b1111_0000_0000_0000) >> 12
        # no IRD
        else:
            new_J = self.J
            if (self.COND == COND.ADDRESSING_MODE) and check_bit(self.IR, 11):
                new_J += 1
            if (self.COND == COND.MEMORY_READY) and self.R:
                new_J += 2
            if (self.COND == COND.BRANCH) and self.BEN:
                new_J += 4       
            if (self.COND == COND.PRIVILEGE_MODE) and check_bit(self.PSR, 15):
                new_J += 8
            if (self.COND == COND.INTERRUPT_TEST) and self.INT:
                new_J += 16
            if (self.COND == COND.ACV_TEST) and self.ACV:
                new_J += 32
        self.state = new_J
        log(2, f"New J: {new_J}")

    def load_registers(self):
        # Do Loads at end (like falling edge of clock)
        if self.LD_MDR:
            # This could be to load MDR from a memory read or from the main bus
            if self.MIO_EN:
                self.MDR = self.MEMORY_OUT
                log(3, f"Loading MDR 0x{self.MDR:04x} from internal memory bus")
            else:
                self.MDR = self.bus
                log(3, f"Loading MDR 0x{self.MDR:04x} from main bus")            
            
        if self.LD_MAR:
            self.MAR = self.bus
            log(3, f"Loading MAR 0x{self.MAR:04x} from bus")
        
        if self.LD_PC:
            self.PC = self.PC_MUX_OUT
            log(3, f"Loading PC from PC_MUX_OUT 0x{self.PC:04x}")
                
        if self.LD_IR:
            self.IR = self.bus
            log(3, f"Loading IR 0x{self.IR:04x} from bus")
     
        if self.LD_CC:
            self.Z = (self.bus == 0)
            self.P = (self.bus <= 0x7fff)
            self.N = (self.bus > 0x7fff)
            log(3, f"Loading Z N P {self.Z} {self.N} {self.P} from bus")

        if self.LD_REG:
            self.regs[self.DR] = self.bus
            log(3, f"Loading DR R{self.DR} with 0x{self.bus:04x}")

        if self.LD_ACV:
            self.ACV = self.ACV_OUT
            log(3, f"Loading ACV with {self.ACV}")

        if self.LD_BEN:
            self.BEN = self.BEN_OUT
            log(3, f"Loading BEN with {self.BEN}")

class Memory():
    def __init__(self):
        self.memory_max = 0x4000
        self.memory = [0] * self.memory_max

        self.clock_latency = 3
        self.clock_count = 0

    def clock_cycle(self, cu):
        # There is no need to gate MDR as this can't change in this clock cycle
        # MDR is controlled by a LD_MDR

        cu.R = False
        if cu.MIO_EN:
            self.MEMORY_OUT = 0
            log(3, "Memory enabled")
            # Use clock_count and clock_latency to emulate memory latency of clock_latency cycles
            self.clock_count += 1
            if (self.clock_count >= self.clock_latency):
                self.clock_count = 0
                cu.R = True
                # The only place a memory write can come from is the MDR
                # but a read goes to a mux before MDR
                if cu.RW == MemRW.WR:
                    self.memory[cu.MAR] = cu.MDR
                    log(3, f"Memory write 0x{cu.MDR:04x} to 0x{cu.MAR:04x}")
                else:
                    cu.MEMORY_OUT = self.memory[cu.MAR]
                    log(3, f"Memory read 0x{cu.MEMORY_OUT:04x} from 0x{cu.MAR:04x}")


class LC3():
    def __init__(self):
        self.cu = ControlUnit()
        self.mem = Memory()
        
    def execute(self):
        self.cu.clear_control_signals()
        self.cu.clear_state_signals()
  
        self.cu.set_control_signals()
        self.mem.clock_cycle(self.cu)
        self.cu.process_gating()
        self.cu.execute_logic()
        self.cu.set_new_state()
    
        self.cu.load_registers()

