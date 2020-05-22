#  [ ] Add the `CMP` instruction and `equal` flag to your LS-8.

# - [ ] Add the `JMP` instruction.

# - [ ] Add the `JEQ` and `JNE` instructions.

import sys

LDI = 0b10000010
PRN = 0b01000111
HLT = 0b00000001
MUL = 0b10100010
POP = 0b01000110 
PUSH = 0b01000101 
CALL = 0b01010000
RET = 0b00010001
ADD = 0b10100000

# per instructions, added: 
CMP = 0b10100111
JMP = 0b01010100 
JEQ = 0b01010101
JNE = 0b01010110




SP = 7 



class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.reg = [0] * 8 
        self.ram = [0] * 256 
        self.pc = 0 
        self.branchtable = {}
        self.branchtable[LDI] = self.handle_LDI
        self.branchtable[PRN] = self.handle_PRN
        self.branchtable[HLT] = self.handle_HLT
        self.branchtable[MUL] = self.handle_MUL
        self.branchtable[POP] = self.handle_POP
        self.branchtable[PUSH] = self.handle_PUSH
        self.branchtable[CALL] = self.handle_CALL
        self.branchtable[RET] = self.handle_RET
        self.branchtable[ADD] = self.handle_ADD
        self.branchtable[CMP] = self.handle_CMP
        self.branchtable[JMP] = self.handle_JMP
        self.branchtable[JEQ] = self.handle_JEQ
        self.branchtable[JNE] = self.handle_JNE


    def ram_read(self, address): 
        return self.ram[address] 

    def ram_write(self, address, value):
        self.ram[address] = value 

    def load(self, program):
        """Load a program into memory."""

        address = 0

                # For now, we've just hardcoded a program:

        # program = [
        #     # From print8.ls8
        #     0b10000010, # LDI R0,8
        #     0b00000000,
        #     0b00001000,
        #     0b01000111, # PRN R0
        #     0b00000000,
        #     0b00000001, # HLT
        # ]

        with open(sys.argv[1]) as f:
            for line in f:
                string_val = line.split("#")[0].strip()
                if string_val == "":
                    continue 
                value = int(string_val, 2)
                self.ram[address] = value
                address += 1


    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
        elif op == "MUL": # Multiply the values in two registers together and store the result in registerA
            self.reg[reg_a] *= self.reg[reg_b]
        else:
            raise Exception("Unsupported ALU operation")

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            #self.fl,
            #self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()

    def handle_LDI(self): # sets register -> value
        operand_a = self.ram_read(self.pc + 1) 
        operand_b = self.ram_read(self.pc + 2)

        # operand_a (register in LDI) = operand_b (value in LDI)
        self.reg[operand_a] = operand_b
        self.pc += 3 # down 3 to MUL

    def handle_PRN(self): # print the actual value inside of the register -> like LDI, but only the first part
        operand_a = self.ram_read(self.pc + 1) 

        # print(register at location operand_a)
        print(self.reg[operand_a])
        self.pc += 2 # down 2 to HLT


    def handle_MUL(self): #multiply side by side values, must call alu to use mult funct
        operand_a = self.ram_read(self.pc + 1) 
        operand_b = self.ram_read(self.pc + 2)

        # pass in name of function and params
        self.alu("MUL", operand_a, operand_b) 
        self.pc += 3 
    
    
    def handle_HLT(self):
        sys.exit(0) #quit


    def handle_PUSH(self):
        #Decrement the stack pointer on push
        self.reg[SP] -= 1 
        # ran_read returns the ram address (not value)
        # save reg + 1 to find the address = now, reg_num should be = mem address
        reg_num = self.ram_read(self.pc + 1)
        # find actual number value of address  by looking inside register
        value = self.reg[reg_num]
        # value found inside register needs to replace SP value
        # sp address, register val
        self.ram_write(self.reg[SP], value)
        #increment by two to halt
        self.pc += 2 

    def handle_POP(self):
        # set value as memory address at SP 
        value = self.ram_read(self.reg[SP]) #4a from ex
        # save reg + 1 to find the address = now, reg_num should be = mem address
        reg_num = self.ram_read(self.pc +1) #register address, set its value to the val of SP
        self.reg[reg_num] = value
        #increase the stack pointer on pop -> previously pushed item on stack
        self.reg[SP] += 1 #F1->F2
        #increment by two to halt
        self.pc += 2

    def handle_CALL(self):
        # after call -> pushed to stack
        # decrement the stack
        self.reg[SP] -= 1
        # create address, two away from intial pc
        address = self.pc + 2
        # sp address = register address
        self.ram[self.reg[SP]] = address

        reg_num = self.ram_read(self.pc + 1)
        self.pc = self.reg[reg_num]
        

    def handle_RET(self):
        # Return from subroutine -> pop the val from the top of the stack, store it in pc 
        self.pc = self.ram[self.reg[SP]]
        # increment SP
        self.reg[SP] += 1

    def handle_ADD(self): 
        # add val of a and b 
        operand_a = self.ram_read(self.pc + 1) 
        operand_b = self.ram_read(self.pc + 2)

        # call alu method
        self.alu("ADD", operand_a, operand_b)
        self.pc += 3
        
    def run(self):
        """Run the CPU."""

        running = True

        while running: 
            IR = self.ram[self.pc] #fetch value from RAM and then use that value to look up handler function in the branch table
            self.branchtable[IR]()







