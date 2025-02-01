from LC3 import LC3, set_log_level

lc = LC3()
set_log_level(4)

def run_times(times):
    lc.cu.PC = 0x3000
    lc.cu.state = 18
    for _ in range(times):
        lc.execute()

def check(cond):
    print("Success") if cond else print("Failed")

set_log_level(4)


set_log_level(0)

print( "Test:   LDI R2, R1, 0x003")
lc.cu.regs = [0x0003, 0x3005, 0x03ff, 0x0707, 0x0005, 0x0050, 0x0500, 0x5000]
lc.mem.memory[0x3000] = 0b1010_010_0_0000_0011
lc.mem.memory[0x3004] = 0x3008
lc.mem.memory[0x3008] = 0x1234
run_times(18)
print(f"Result: 0x{lc.cu.regs[2]:04x} in R2")
check(lc.cu.regs[2] == 0x1234)
print("-" * 50)

print( "Test:   LDR R2, R1, 0x003")
lc.cu.regs = [0x0003, 0x3005, 0x03ff, 0x0707, 0x0005, 0x0050, 0x0500, 0x5000]
lc.mem.memory[0x3000] = 0b0110_010_001_00_0011
lc.mem.memory[0x3008] = 0x1234
run_times(13)
print(f"Result: 0x{lc.cu.regs[2]:04x} in R2")
check(lc.cu.regs[2] == 0x1234)
print("-" * 50)

print( "Test:   LD R2, 0x003")
lc.cu.regs = [0x0003, 0x3005, 0x03ff, 0x0707, 0x0005, 0x0050, 0x0500, 0x5000]
lc.mem.memory[0x3000] = 0b0010_010_0_0000_0011
lc.mem.memory[0x3004] = 0x1234
run_times(13)
print(f"Result: 0x{lc.cu.regs[2]:04x} in R2")
check(lc.cu.regs[2] == 0x1234)

print( "Test:   JSRR R1")
lc.cu.regs = [0x0003, 0x3005, 0x03ff, 0x0707, 0x0005, 0x0050, 0x0500, 0x5000]
lc.mem.memory[0x3000] = 0b0100_000_001_000000
run_times(9)
print(f"Result: 0x{lc.cu.PC:04x} in PC, 0x{lc.cu.regs[7]:04x} in R7")
check(lc.cu.PC == 0x3005)
check(lc.cu.regs[7] == 0x3001)
print("-" * 50)

print( "Test:   JSR 0x007")
lc.cu.regs = [0x0003, 0x3003, 0x03ff, 0x0707, 0x0005, 0x0050, 0x0500, 0x5000]
lc.mem.memory[0x3000] = 0b0100_1_000_0000_0111
run_times(9)
print(f"Result: 0x{lc.cu.PC:04x} in PC, 0x{lc.cu.regs[7]:04x} in R7")
check(lc.cu.PC == 0x3008)
check(lc.cu.regs[7] == 0x3001)
print("-" * 50)

print( "Test:   JMP R1")
lc.cu.regs = [0x0003, 0x3003, 0x03ff, 0x0707, 0x0005, 0x0050, 0x0500, 0x5000]
lc.mem.memory[0x3000] = 0b1100_000_001_00_0000
run_times(8)
print(f"Result: 0x{lc.cu.PC:04x} in PC")
check(lc.cu.PC == 0x3003)
print("-" * 50)

print( "Test:   BR NZP 2")
lc.cu.Z = True
lc.cu.regs = [0x0003, 0x0003, 0x03ff, 0x0707, 0x0005, 0x0050, 0x0500, 0x5000]
lc.mem.memory[0x3000] = 0b0000_010_0_0000_0010
run_times(9)
print(f"Result: 0x{lc.cu.PC:04x} in PC")
check(lc.cu.PC == 0x3003)
print("-" * 50)

print( "Test:   AND R1, R3, 7")
lc.cu.regs = [0x0003, 0x0003, 0x03ff, 0x0707, 0x0005, 0x0050, 0x0500, 0x5000]
lc.mem.memory[0x3000] = 0b0101_001_011_1_00111
run_times(8)
print(f"Result: 0x{lc.cu.regs[1]:04x} in R1")
check(lc.cu.regs[1] == 0x0007)
print("-" * 50)

print("Test:   LEA R5, 0x70")
lc.cu.regs = [0x0003, 0x0030, 0x0300, 0x3000, 0x0005, 0x0050, 0x0500, 0x5000]
lc.mem.memory[0x3000] = 0b1110_101_001110000
run_times(8)
print(f"Result: 0x{lc.cu.regs[5]:04x} in R5")
check(lc.cu.regs[5] == 0x3071)
print("-" * 50)

print("Test:   STI R5 0x3003")
lc.cu.regs = [0x0003, 0x0030, 0x0300, 0x3000, 0x0005, 0x0050, 0x0500, 0x5000]
lc.mem.memory[0x3000] = 0b1011_101_000000010
lc.mem.memory[0x3003] = 0x3004
lc.mem.memory[0x3004] = 0x1234
run_times(17)
print(f"Result: 0x{lc.mem.memory[0x3004]:04x} in [0x3004]")
check(lc.mem.memory[0x3004] == 0x0050)
print("-" * 50)


print("Test:   STR R2 R3 +3")
lc.cu.regs = [0x0003, 0x0030, 0x0300, 0x3000, 0x0005, 0x0050, 0x0500, 0x5000]
lc.mem.memory[0x3000] = 0b0111_101_011_000011
lc.mem.memory[0x3003] = 0x0000
run_times(12)
print(f"Result: 0x{lc.mem.memory[0x3003]:04x} in [0x3003]")
check(lc.mem.memory[0x3003] == 0x0050)
print("-" * 50)


print("Test:   ST R2 +2")
lc.cu.regs = [0x0003, 0x0030, 0x0300, 0x3000, 0x0005, 0x0050, 0x0500, 0x5000]
lc.mem.memory[0x3000] = 0b0011_010_000_0_00010
lc.mem.memory[0x3003] = 0x0000
run_times(12)
print(f"Result: 0x{lc.mem.memory[0x3003]:04x} in [0x3003]")
check(lc.mem.memory[0x3003] == 0x0300)
print("-" * 50)


print("Test:   FETCH and DECODE cycle")
lc.cu.regs = [0x0003, 0x0030, 0x0300, 0x3000, 0x0005, 0x0050, 0x0500, 0x5000]
lc.mem.memory[0x3000] = 0b0000_0000_0000_0001
run_times(7)       # only 7 instructions to get to DECODE
print(f"Result: got to state {lc.cu.state:d}")
check(lc.cu.state == 0)
print("-" * 50)


print("Test:   NOT 0x3000")
lc.cu.regs = [0x0003, 0x0030, 0x0300, 0x3000, 0x0005, 0x0050, 0x0500, 0x5000]
lc.mem.memory[0x3000] = 0b1001_011_011_1_11111
run_times(8)
print(f"Result: 0x{lc.cu.regs[3]:04x} in R3")
check(lc.cu.regs[3] == 0xcfff)
print("-" * 50)


print("Test:   ADD R1, R3, 7")
lc.cu.regs = [0x0003, 0x0030, 0x0300, 0x3000, 0x0005, 0x0050, 0x0500, 0x5000]
lc.mem.memory[0x3000] = 0b0001_001_011_1_00111
run_times(8)
print(f"Result: 0x{lc.cu.regs[1]:04x} in R2")
check(lc.cu.regs[1] == 0x3007)
print("-" * 50)


print("Test:   ADD R2, R3, R4")
lc.cu.regs = [0x0003, 0x0030, 0x0300, 0x3000, 0x0005, 0x0050, 0x0500, 0x5000]
lc.mem.memory[0x3000] = 0b0001_010_011_0_00_100
run_times(8)
print(f"Result: 0x{lc.cu.regs[2]:04x} in R2")
check(lc.cu.regs[2] == 0x3005)
print("-" * 50)

print( "Test:   LD R2, 0x003 with ACV")
lc.cu.regs = [0x0003, 0x3005, 0x03ff, 0x0707, 0x0005, 0x0050, 0x0500, 0x5000]
lc.mem.memory[0x3000] = 0b0010_010_1_1111_1100
run_times(9)
print(f"Result: {lc.cu.ACV}")
check(lc.cu.ACV == True)
print("-" * 50)

