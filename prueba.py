class Z80Disassembler:
    def __init__(self):
        # Opcode tables
        self.unprefixed_opcodes = {
            0x00: "NOP",
            0x3E: "LD A,{0:02X}",
            0x06: "LD B,{0:02X}",
            0x0E: "LD C,{0:02X}",
            0x16: "LD D,{0:02X}",
            0x1E: "LD E,{0:02X}",
            0x26: "LD H,{0:02X}",
            0x2E: "LD L,{0:02X}",
            0x78: "LD A,B",
            0x79: "LD A,C",
            0xC3: "JP {0:02X}{1:02X}",
            0xCD: "CALL {0:02X}{1:02X}",
            0xC9: "RET",
            # Add more opcodes as needed
        }

        self.cb_prefixed_opcodes = {
            0x00: "RLC B",
            0x01: "RLC C",
            0x11: "RL C",
            0x7C: "BIT 7,H",
            # Add more CB-prefixed opcodes as needed
        }

    def read_byte(self, data, pc):
        """Read a single byte from the data at program counter."""
        if pc < len(data):
            return data[pc]
        return None

    def read_word(self, data, pc):
        """Read a 16-bit word from the data at program counter."""
        if pc + 1 < len(data):
            return data[pc] | (data[pc + 1] << 8)
        return None

    def disassemble_instruction(self, data, pc):
        """Disassemble a single instruction at the given program counter."""
        opcode = self.read_byte(data, pc)
        if opcode is None:
            return None, 0

        instruction = None
        length = 1

        # Handle CB-prefixed opcodes
        if opcode == 0xCB:
            cb_opcode = self.read_byte(data, pc + 1)
            if cb_opcode is not None:
                instruction = self.cb_prefixed_opcodes.get(cb_opcode)
                length = 2

        # Handle unprefixed opcodes
        else:
            instruction_template = self.unprefixed_opcodes.get(opcode)
            if instruction_template:
                # Handle different instruction formats
                if "{0:02X}{1:02X}" in instruction_template:
                    # 16-bit immediate value
                    word = self.read_word(data, pc + 1)
                    if word is not None:
                        instruction = instruction_template.format(word & 0xFF, word >> 8)
                        length = 3
                elif "{0:02X}" in instruction_template:
                    # 8-bit immediate value
                    byte = self.read_byte(data, pc + 1)
                    if byte is not None:
                        instruction = instruction_template.format(byte)
                        length = 2
                else:
                    # No immediate values
                    instruction = instruction_template

        return instruction, length

    def disassemble(self, data, start_address=0):
        """Disassemble a block of Z80 machine code."""
        pc = 0
        result = []

        while pc < len(data):
            instruction, length = self.disassemble_instruction(data, pc)
            if instruction:
                result.append(f"{start_address + pc:04X}: {instruction}")
                pc += length
            else:
                result.append(f"{start_address + pc:04X}: DB {data[pc]:02X}")
                pc += 1

        return result

def main():
    # Example usage
    sample_code = bytes([
        0x3E, 0x42,       # LD A,42h
        0x06, 0x10,       # LD B,10h
        0xC3, 0x00, 0x10  # JP 1000h
    ])

    disassembler = Z80Disassembler()
    disassembled = disassembler.disassemble(sample_code)
    for line in disassembled:
        print(line)

if __name__ == "__main__":
    main()
