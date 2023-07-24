import argparse
import importlib
import inspect
from dataclasses import dataclass

# TODO: if-goto doesn't consume bool
# TODO: if-goto also doesn't work
# TODO: pushing lines to stack is surrounded in ""
# TODO: since base can't be popped perhaps add explicit base that returns pc to -1 (then main program can return out)

debug = True

stack = ["- BASE -------------------------------------------\n"]
heap = []
primitives = {} # python functions
symbols = {} # label -> address mappings
slobmys = {} # address -> label mappings

lcl = {}
static = {}

pc = 0
sp = 0 # cannot pop base of stack


def load_functions(module_name):
    module = importlib.import_module(module_name)
    functions = inspect.getmembers(module, inspect.isfunction)
    fct_dict = {name.replace('_', "-"): fct for name, fct in functions}
    return fct_dict

def push(x):
    global lcl
    global stack
    global sp

    if isinstance(x, Frame):
        stack.append(x)
        return

    if x.strip() in lcl:
        x = x.strip()
        if debug: input(f"push: {len(lcl[x])} lines from {x}")
        if isinstance(lcl[x], (tuple, list)):
            stack += lcl[x]
            return
        stack.append(lcl[x])
        return
    if debug: input(f"push: {x}")
    stack.append(x)

def pop(x, n=1):
    global stack
    global lcl
    global sp

    n = n.strip() if isinstance(n, str) else n

    if debug: input(f"pop {n} -> {x}")

    if n == "*":
        n = len(stack) - (sp + 1)
    else:
        if isinstance(n, str):
            assert n.isdigit(), f"nargs must be a number, not {n}"

    popped = stack[-n:]
    del stack[-n:]
    lcl[x] = popped
    return

def dup(n=1):
    global stack
    global sp
    if n == "*":
        n = len(stack) - 1 - sp

    if debug: input(f"dup: {n}")

    stack += stack[-n:]

def goto(symbol):
    global pc
    # pc = loc
    symbol = symbol.strip()
    pc = symbols[symbol] -1 # -1 because pc is incremented after each instruction
    if debug: input(f"sending control to {symbol} ({symbols[symbol]})")

def if_goto(symbol): # TODO NEXT: if-goto not even called
    global pc

    symbol = symbol.strip()

    if bool(stack.pop()[1].strip()):
        if debug: input(f"sending control to {symbol} ({symbols[symbol]})")
        pc = symbols[symbol.strip()] - 1 # -1 because pc is incremented after each instruction
    else:
        if debug: input(f"continuing to {pc+1}")

@dataclass
class Frame:
    fct: str
    sp: int
    pc: int
    lcl: dict

    def __str__(self):
        r = f"- {self.fct} ({self.sp}) "
        return r + (50-len(r)) * "-" + "\n"

    def __iter__(self):
        yield self.fct
        yield self.sp
        yield self.pc
        yield self.lcl

def call(fct, nargs): # The function becomes what it wants to return
    global lcl
    global sp
    global pc
    global stack

    nargs = nargs.strip()

    if nargs == "*":
        nargs = len(stack) - (sp + 1)  # +1 to exclude Frame
    else:
        assert nargs.isdigit(), f"nargs must be a number, not {nargs}"

    nargs = int(nargs)

    arg = stack[-nargs:]
    del stack[-nargs:]

    push(Frame(fct, sp, pc, lcl.copy()))

    sp = len(stack) - 1

    # arg = new_arg

    if fct in primitives:
        result = primitives[fct](*arg)
        if debug: print(f"call: {fct} {nargs} -> {result}")
        if isinstance(result, (tuple, list)):
            stack += result
        else:
            stack.append(result)

        return_ctrl()
        return

    if debug: print(f"call: {fct} {nargs}")

    stack += arg

    lcl = {}
    goto(fct)


def return_ctrl():
    global lcl
    global sp
    global pc
    global stack

    _, sp, pc, lcl = stack.pop(sp)

    if debug: input(f"returning control to caller ({pc + 1})")

def print_stack():
    global stack
    global lcl
    print("\033c")
    for x in stack:
        print(x, end="")
    print("\n\n")
    print("- LOCALS -----------------------------------------")
    for x, lines in lcl.items():
        print(f"{x}:\n")
        for line in lines:
            print(f"    {line}", end="")
    print("\n--------------------------------------------------\n")



def main():
    parser = argparse.ArgumentParser(description="Process some files.")
    parser.add_argument("filename", type=str, help="Input filename")
    parser.add_argument("-o", "--output", type=str, help="Output filename", default="")

    clargs = parser.parse_args()

    file = clargs.filename
    with open(file, "r") as f:
        lines = f.readlines()

    lines = [line.lstrip() for line in lines if line.strip()]

    global pc
    global primitives
    global stack

    primitives = load_functions("functions")

    # process labels and function definitions
    i = 0
    remaining_lines = len(lines)
    while remaining_lines > 0:
        lines[i] = lines[i].lstrip()
        remaining_lines -= 1
        if lines[i].startswith("label"):
            label = lines[i].split(" ", 1)[1].strip()
            symbols[label] = i
            lines.pop(i)
            continue
        if lines[i].startswith("function"):
            name = lines[i][9:]
            name = name.strip()

            symbols[name] = i
            lines.pop(i)
            continue

        i += 1

    if debug:
        global slobmys
        slobmys = {v: k for k, v in symbols.items()}

    if clargs.output:
        with open(clargs.output, "w") as f:
            f.write("".join(lines))
            f.write("\n")
            f.write(str(symbols))
    else:
        while pc >= 0:
            line = lines[pc]
            cmd_and_arg = line.split(" ", 1)
            if len(cmd_and_arg) == 1:
                cmd, arg = cmd_and_arg[0].strip(), "" # strip because it will include \n
            else:
                cmd, arg = cmd_and_arg

            match cmd:
                case "push":
                    push(arg)
                case "pop":
                    if " " in arg:
                        arg, n = arg.split(" ", 1)
                        pop(arg, n)
                    else:
                        pop(arg)
                case "dup":
                    dup(arg)
                case "goto":
                    goto(arg)
                case "if-goto":
                    if_goto(arg)
                case "call":
                    fct, nargs = arg.split(" ", 1)
                    call(fct, nargs)
                case "return":
                    return_ctrl()
                case "exit":
                    pc = -1
                    break
                case _:
                    nargs = arg
                    call(cmd, nargs)

            pc += 1

            print_stack()
        input("\n[ finished ]")







if __name__ == "__main__":
    main()


