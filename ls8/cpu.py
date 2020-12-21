"""CPU functionality."""

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
JNE = 0b01010110
JEQ = 0b01010101
JMP = 0b01010100
CMP = 0b10100111


class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.ram = [0] * 256
        self.reg = [0] * 8
        self.pc = 0
        self.sp = 0xF4
        self.flags = 0b00000000

        self.branchtable = {}
        self.branchtable[LDI] = self.ldi
        self.branchtable[PRN] = self.prn
        self.branchtable[HLT] = self.hlt
        self.branchtable[MUL] = self.mul
        self.branchtable[POP] = self.pop
        self.branchtable[PUSH] = self.push
        self.branchtable[CALL] = self.call
        self.branchtable[RET] = self.ret
        self.branchtable[ADD] = self.add
        self.branchtable[JNE] = self.jne
        self.branchtable[JEQ] = self.jeq
        self.branchtable[JMP] = self.jmp
        self.branchtable[CMP] = self.cmp

    """ START ALU function calls"""

    def ldi(self, operand_a, operand_b):
        self.reg[operand_a] = operand_b
        self.pc += 3

    def prn(self, operand_a, operand_b):
        print(self.reg[operand_a])
        self.pc += 2

    def hlt(self, operand_a, operand_b):
        sys.exit(1)

    def mul(self, operand_a, operand_b):
        self.alu("MUL", operand_a, operand_b)
        self.pc += 3

    def add(self, operand_a, operand_b):
        self.alu("ADD", operand_a, operand_b)
        self.pc += 3

    def cmp(self, operand_a, operand_b):
        self.alu("CMP", operand_a, operand_b)
        self.pc += 3

    def pop(self, operand_a, operand_b):
        value = self.ram[self.sp]
        self.reg[operand_a] = value
        self.pc += 2

    def push(self, operand_a, operand_b):
        self.sp -= 1
        value = self.reg[operand_a]
        self.ram_write(self.sp, value)
        self.pc += 2

    def call(self, operand_a, operand_b):
        self.sp -= 1
        value = self.pc + 2
        self.ram_write(self.sp, value)
        self.pc = self.reg[operand_a]

    def ret(self, operand_a, operand_b):
        value = self.ram[self.sp]
        self.pc = value

    def jmp(self, operand_a, operand_b):
        self.pc = self.reg[operand_a]

    def jeq(self, operand_a, operand_b):
        if self.flags == 0b00000001:
            self.pc = self.reg[operand_a]
        else:
            self.pc += 2

    def jne(self, operand_a, operand_b):
        if self.flags != 0b00000001:
            self.pc = self.reg[operand_a]
        else:
            self.pc += 2

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

    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
        elif op == "MUL":
            self.reg[reg_a] *= self.reg[reg_b]
        elif op == "CMP":
            if self.reg[reg_a] > self.reg[reg_b]:
                self.flags = 0b00000010
            elif self.reg[reg_a] < self.reg[reg_b]:
                self.flags = 0b00000100
            else:
                self.flags = 0b00000001
        else:
            raise Exception("Unsupported ALU operation")

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

    def ram_read(self, address):
        return self.ram[address]

    def ram_write(self, address, value):
        self.ram[address] = value

    def run(self):
        """Run the CPU."""

        while True:
            IR = self.ram_read(self.pc)
            operand_a = self.ram_read(self.pc + 1)
            operand_b = self.ram_read(self.pc + 2)

            if IR not in self.branchtable:
                sys.exit(1)
            else:
                self.branchtable[IR](operand_a, operand_b)
