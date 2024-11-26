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
        self.eti = {}
        self.eti_number = 1

    def read_opcodes_csv(self, name):
        map = {}
        with open('static/csv/'+name+'.csv') as file:
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
        jump = False
        double_prefix = False

        if opcode == 0xED:
            offset = 1
            ed_opcode = self.read_byte(data, pc + 1)
            if ed_opcode is not None:
                instruction = self.ed_opcodes.get(ed_opcode)

        elif opcode == 0xCB:
            offset= 1
            cb_opcode = self.read_byte(data, pc + 1)
            if cb_opcode is not None:
                instruction = self.cb_opcodes.get(cb_opcode)

        elif opcode == 0xDD:
            dd_opcode= self.read_byte(data, pc + 1)

            if dd_opcode == 0xCB:
                double_prefix = True
                ddcb_opcode = self.read_byte(data, pc+3)
                instruction = self.ddcb_opcodes.get(ddcb_opcode)

            elif dd_opcode is not None:
                offset = 1
                instruction = self.dd_opcodes.get(dd_opcode)

        elif opcode == 0xFD:
            fd_opcode= self.read_byte(data, pc + 1)

            if fd_opcode == 0xCB:
                double_prefix = True
                fdcb_opcode = self.read_byte(data, pc+3)
                instruction = self.fdcb_opcodes.get(fdcb_opcode)

            elif fd_opcode is not None:
                offset = 1
                instruction = self.fd_opcodes.get(fd_opcode)

        else:
            instruction = self.opcodes.get(opcode)

        if double_prefix and instruction:
            if "{0:02X}" in instruction:
                byte = self.read_byte(data, pc + 2)
                if byte is not None:
                    instruction = instruction.format(byte)
                    length = 4

        elif instruction:
            if "JR" in instruction or "JP" in instruction:
                jump = True

            if "{0:04X}" in instruction:
                word = self.read_word(data, pc + 1 + offset)
                if word is not None:
                    if jump:
                        if self.eti.get(word) is None:
                            self.eti[word] = self.eti_number;
                            self.eti_number += 1;
                        instruction = instruction.replace('{0:04X}H', 'eti' + str(self.eti[word]))
                        length = 3 + offset
                    else:
                        instruction = instruction.format(word)
                        length = 3 + offset


            elif "{0:02X}H$" in instruction:
                byte = self.read_byte(data, pc + 1 + offset)
                if byte is not None:
                    if byte & (1<<7):
                        byte -= 256
                    word = byte + pc + 2
                    if jump:
                        if self.eti.get(word) is None:
                            self.eti[word] = self.eti_number;
                            self.eti_number += 1;
                        instruction = instruction.replace('{0:02X}H$', 'eti' + str(self.eti[word]))
                        length = 3 + offset
                    else:
                        instruction = instruction.format(word)
                        length = 3 + offset
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
        address = []

        while pc < len(data):
            instruction, length = self.disassemble_instruction(data, pc)
            if instruction:
                result.append(f"{"%eti%" +instruction}")
                address.append(pc)
                pc += length
            else:
                result.append("Instrucción inválida")
                address.append(pc)
                pc += 1;

        for i in range(len(result)):
            line = result[i]
            if self.eti.get(address[i]) is not None:
                result[i] = line.replace('%eti%', 'eti' + str(self.eti.get(address[i])) + ': ')
            else:
                result[i] = line.replace('%eti%', '      ')

        return result
