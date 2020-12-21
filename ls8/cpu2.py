"""CPU functionality."""

import sys


LDI = 0b10000010
PRN = 0b01000111
HLT = 0b00000001
MUL = 0b10100010
POP = 0b01000110
PUSH = 0b01000101
ADD = 0b10100000


class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.ram = [0] * 255
        self.reg = [0] * 16
        self.pc = 0
        self.sp = 6

        self.branchtable = {}
        self.branchtable[LDI] = self.ldi
        self.branchtable[PRN] = self.prn
        self.branchtable[HLT] = self.hlt
        self.branchtable[MUL] = self.mul
        self.branchtable[POP] = self.pop
        self.branchtable[PUSH] = self.push

    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
        elif op == "MUL":
            self.reg[reg_a] *= self.reg[reg_b]
        else:
            raise Exception("Unsupported ALU operation")

    def ldi(self, op_a, op_b):
        self.reg[op_a] = op_b
        self.pc += (self.ram[self.pc] >> 6) + 1
        print(':', self.pc)

    def prn(self, val):
        print(self.reg[val])
        self.pc += (self.ram[self.pc] >> 6) + 1
        print(':', self.pc)

    def hlt(self):
        sys.exit(2)

    def mul(self, op_a, op_b):
        self.alu('MUL', op_a, op_b)
        # print(op_a, op_b)
        self.pc += (self.ram[self.pc] >> 6) + 1
        print(':', self.pc)

    def pop(self, val):
        stack_value = self.ram[self.sp]
        self.reg[val] = stack_value
        self.sp += 1
        self.pc += (self.ram[self.pc] >> 6) + 1
        print(':', self.pc)

    def push(self, val):
        self.sp -= 1
        value = self.reg[val]
        self.ram_write(self.sp, value)
        self.pc += (self.ram[self.pc] >> 6) + 1
        print(':', self.pc)

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            # self.fl,
            # self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()

    def run(self):
        """Run the CPU."""
        IR = self.ram[self.pc]
        running = True
        while running:
            IR = self.ram[self.pc]
            operand_a = self.ram_read(self.pc+1)
            operand_b = self.ram_read(self.pc+2)

            self.branchtable[LDI](operand_a, operand_b)
            self.branchtable[PUSH](operand_a)
            self.branchtable[POP](operand_a)
            self.branchtable[MUL](operand_a, operand_b)
            self.branchtable[PRN](operand_a)
            self.branchtable[HLT]()

            # self.pc += (IR >> 6) + 1

    def ram_read(self, address):
        return self.ram[address]

    def ram_write(self, address, value):
        self.ram[address] = value

    def load(self, filename):
        try:
            address = 0
            with open(filename) as f:
                for line in f:
                    comment_split = line.split("#")
                    num = comment_split[0].strip()
                    if len(num) == 0:
                        continue
                    value = int(num, 2)
                    self.ram[address] = value
                    address += 1
        except FileNotFoundError:
            print(f"{sys.argv[0]}: {sys.argv[1]} not found")
            sys.exit(2)
