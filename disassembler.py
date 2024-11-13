import csv

class Dissasembler:
    def __init__(self):
        self.opcodes = self.read_opcodes_csv("opcodes")
        self.ed_opcodes = self.read_opcodes_csv("ed_opcodes")
        self.cb_opcodes = self.read_opcodes_csv("cb_opcodes")
        self.dd_opcodes = self.read_opcodes_csv("dd_opcodes")
        self.ddcb_opcodes = self.read_opcodes_csv("ddcb_opcodes")
        self.fd_opcodes = self.read_opcodes_csv("fd_opcodes")
        self.fdcb_opcodes = self.read_opcodes_csv("fdcb_opcodes")

    def read_opcodes_csv(self, name):
        map = {}
        with open('csv/'+name+'.csv') as file:
           csvFile = csv.reader(file, delimiter=';')
           for lines in csvFile:
               map[int(lines[0], 16)] = lines[1]
        return map

    def read_byte(self, data, pc):
        if pc < len(data):
            return data[pc]
        return None

    def read_word(self, data, pc):
        if pc + 1 < len(data):
            return data[pc] | (data[pc + 1] << 8)
        return None

    def disassemble_instruction(self, data, pc):
        opcode = self.read_byte(data, pc)
        if opcode is None:
            return None, 0

        instruction = None
        length = 1
        offset = 0
        double_prefix = False

        if opcode == 0xED:
            offset = 1
            ed_opcode = self.read_byte(data, pc + 1)
            if ed_opcode is not None:
                instruction = self.ed_opcodes[ed_opcode]

        elif opcode == 0xCB:
            offset= 1
            cb_opcode = self.read_byte(data, pc + 1)
            if cb_opcode is not None:
                instruction = self.cb_opcodes[cb_opcode]

        elif opcode == 0xDD:
            dd_opcode= self.read_byte(data, pc + 1)

            if dd_opcode == 0xCB:
                double_prefix = True
                ddcb_opcode = self.read_byte(data, pc+3)
                instruction = self.ddcb_opcodes[ddcb_opcode]

            elif dd_opcode is not None:
                offset = 1
                instruction = self.dd_opcodes[dd_opcode]

        elif opcode == 0xFD:
            fd_opcode= self.read_byte(data, pc + 1)

            if fd_opcode == 0xCB:
                double_prefix = True
                fdcb_opcode = self.read_byte(data, pc+3)
                instruction = self.fdcb_opcodes[fdcb_opcode]

            elif fd_opcode is not None:
                offset = 1
                instruction = self.fd_opcodes[fd_opcode]

        else:
            instruction = self.opcodes.get(opcode)

        if double_prefix and instruction:
            if "{0:02X}" in instruction:
                byte = self.read_byte(data, pc + 2)
                if byte is not None:
                    instruction = instruction.format(byte)
                    length = 4

        elif instruction:
            if "{0:04X}" in instruction:
                word = self.read_word(data, pc + 1 + offset)
                if word is not None:
                    instruction = instruction.format(word)
                    length = 3 + offset

            elif "{0:02X}H$" in instruction:
                byte = self.read_byte(data, pc + 1 + offset)
                if byte is not None:
                    if byte & (1<<7):
                        byte -= 256
                    instruction = instruction.format(pc + 2 + byte).replace('$','')
                    length = 2 + offset

            elif "{0:02X}" in instruction:
                byte = self.read_byte(data, pc + 1 + offset)
                if byte is not None:
                    instruction = instruction.format(byte)
                    length = 2 + offset
            else:
                length = 1 + offset

        return instruction, length

    def disassemble(self, data, start_address=0):
        pc = 0
        result = []

        while pc < len(data):
            instruction, length = self.disassemble_instruction(data, pc)
            if instruction:
                result.append(f"{start_address + pc:04X}: {instruction}")
                pc += length

        return result

def main():
    sample_code = bytes([0x3A,0x90,0x01,0x4F,0x3E,0x00,0x06,0x00,0xDD,0x21,0x91,0x01,0x11,0x91,0x01,0xB9,
    0xF2,0x47,0x01,0xF5,0xDD,0x7E,0x00,0xFE,0x00,0xCA,0x30,0x01,0x78,0xFE,0x00,0xCA,
    0x2A,0x01,0x04,0xF1,0x3C,0xDD,0x23,0xC3,0x0F,0x01,0xDD,0xE5,0xE1,0xC3,0x22,0x01,
    0x78,0xFE,0x00,0xCA,0x23,0x01,0xC5,0xE5,0xD5,0x48,0x06,0x00,0xED,0xB0,0xD1,0xE1,
    0xC1,0x13,0x10,0xFD,0xC3,0x23,0x01,0x78,0xFE,0x00,0xCA,0x52,0x01,0x48,0x06,0x00,
    0xED,0xB0,0x76])

    disassembler = Dissasembler()
    disassembled = disassembler.disassemble(sample_code)
    for line in disassembled:
        print(line)

main()
