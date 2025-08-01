import sys

if (len(sys.argv) != 3):
    # .tcasm: Nice, readable and easy to program assembly code, with features like proper operands for all instructions, and returns, etc.
    # .tcu: The format that the Overture CPU can properly execute. To be used in-game.
    print("ERR! Usage: tcasm-converter.py <filename.tcasm> <output.tcu>")
    exit()

with open(sys.argv[1]) as file:
    lines = [line.strip() for line in file]

#constants for registers
register_defs = """# Static setup for source and destinations of all 6 registers and I/O.
const s0 0
const s1 8
const s2 16
const s3 24
const s4 32
const s5 40

const d0 0
const d1 1
const d2 2
const d3 3
const d4 4
const d5 5

const IN 48
const OUT 6
# Continuing to program...

"""

# Now we convert each line of .tcasm to .tcu
# E.g. "mov r0, r1" --> "MOV | s0 | d1"
gp_registers = ["r0", "r1", "r2", "r3", "r4", "r5"]
io_registers = ["in", "out"]

def parse_mov_instruction(instr):
    # Remove comments
    instr = instr.split('#', 1)[0].strip()

    # Skip empty or comment-only lines
    if not instr:
        return None

    # Strip and split the instruction
    parts = instr.replace(',', '').split()

    if len(parts) != 3:
        raise ValueError("Expected format: 'mov r1, r2'")

    mnemonic = parts[0].upper()
    # If the source is an immediate value, src should be s0, and the line above
    # this instruction will need to be the immediate value.
    immediate = ""
    if (parts[1].lower() not in gp_registers and parts[1].lower() not in io_registers):
        immediate = parts[1]
    src = "s0"
    dst = parts[2]

    #print("Instruction: " + instr + " : " + parts[2].lower())
    
    # Handling general purpose registers
    if (parts[1].lower() in gp_registers):
        src = parts[1].lower().replace('r', 's')
    if (parts[2].lower() in gp_registers):
        dst = parts[2].lower().replace('r', 'd')
    
    if (parts[1].lower() == "in"):
        src = "IN"
    if (parts[2].lower() == "out"):
        dst = "OUT"

    converted_instruction = mnemonic + " | " + src + " | " + dst
    result = [immediate, converted_instruction]
    return result

def parse_jmp_instruction(instr):
    # Remove comments
    instr = instr.split('#', 1)[0].strip()

    # Skip empty or comment-only lines
    if not instr:
        return None

    # Strip and split the instruction
    parts = instr.replace(',', '').split()

    if len(parts) != 2:
        raise ValueError("Expected format: 'jmp <dst>'")

    return [parts[1], parts[0].upper()]

def implement_call(instr):
    # Remove comments
    instr = instr.split('#', 1)[0].strip()

    # Skip empty or comment-only lines
    if not instr:
        return None
    
    # Strip and split the instruction
    parts = instr.replace(',', '').split()

    if len(parts) != 2:
        raise ValueError("Expected format: 'call <label>'")
    
    # call <label_name>
    # -->
    # <label_name>
    # JMP
    # label <label_name>_RETURN
    return [parts[1], "JMP", "label " + parts[1] + "_RETURN"]

def implement_return(instr, call_stack):
    # Remove comments
    instr = instr.split('#', 1)[0].strip()

    # Skip empty or comment-only lines
    if not instr:
        return None
    

    
    # return
    # -->
    # <last label used>_RETURN
    # JMP
    if (not call_stack):
        raise ValueError("Error: no labels defined but return is used.")
    return [call_stack[-1] + "_RETURN", "JMP"]

parsed_result = []
calls = []
for line in lines:

    # parse mov commands
    if "mov" in line.lower()[0:3]:
        parsed_result.extend(parse_mov_instruction(line))
    # Now I need to handle jmps and returns...
    elif line and "j" in line.lower()[0]:
        parsed_result.extend(parse_jmp_instruction(line))
    elif "add" in line.lower()[0:3]:
        parsed_result.append("ADD")
    elif "sub" in line.lower()[0:3]:
        parsed_result.append("SUB")
    elif "call" in line.lower()[0:4]:
        parsed_result.extend(implement_call(line))
    elif "label" in line.lower()[0:5]:
        parsed_result.append(line)
        calls.append(line.replace(',', '').split()[1])
    elif "return" in line.lower()[0:6]:
        parsed_result.extend(implement_return(line, calls))
    # pass comments and empty lines along unedited
    elif line:
        parsed_result.append(line)


with open(sys.argv[2], 'w') as fp:
    fp.write(register_defs)
    for line in parsed_result:
        # write each item on a new line
        fp.write("%s\n" % line)
    print('Done')