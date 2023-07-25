import argparse
import importlib
import inspect
from dataclasses import dataclass

# TODO: argv input (for each? index? get length?)
# - foreach <stack name> as if each one is pushed to one arg function

# TODO: blocks; homoiconic data representation (maybe)
# - stored in lcl? then there is a default data stack (arg), and call stack is separate
# - you can pop stacks until they are empty
# - not just push but insertions
# - pass block references as well as args. if you push a block it includes its tags?

# TODO: type system
# - everything has a prompt represtation and a program representation;
#   no need for all the if/elses in the runtime
# - should everything be a block


# TODO: callable as python
# TODO: repeat preprocess directive
# TODO: escape primitive uses in prompt

debug = False

black = lambda text: f"\033[30m{text}\033[0m"
red = lambda text: f"\033[31m{text}\033[0m"
green = lambda text: f"\033[32m{text}\033[0m"
yellow = lambda text: f"\033[33m{text}\033[0m"
blue = lambda text: f"\033[34m{text}\033[0m"
magenta = lambda text: f"\033[35m{text}\033[0m"
cyan = lambda text: f"\033[36m{text}\033[0m"
white = lambda text: f"\033[37m{text}\033[0m"

# stack = ["- BASE -------------------------------------------\n"]
stack = []
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

def pop(x="null", n=1):
    global stack
    global lcl
    global sp

    x = x.strip()
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

def if_goto(symbol):
    global pc

    symbol = symbol.strip()

    do_jump = stack.pop()

    if do_jump == "True\n":
        if debug: input(f"sending control to {symbol} ({symbols[symbol]})")
        pc = symbols[symbol.strip()] - 1 # -1 because pc is incremented after each instruction
    elif do_jump == "False\n":
        if debug: input(f"continuing to {pc+1}")
    else:
        assert False, f"if-goto expected [True, False], not {do_jump}"

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

    if nargs > 0:
        arg = stack[-nargs:]
        del stack[-nargs:]
    else:
        arg = []

    push(Frame(fct, sp, pc, lcl.copy()))

    sp = len(stack) - 1

    # arg = new_arg

    if fct in primitives:
        result = primitives[fct](arg)
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
    for x in stack[:-1]:
        print(x, end="")
    print(stack[-1], end="")
    if debug:
        print("\n\n")
        print("- LOCALS -----------------------------------------")
        for x, lines in lcl.items():
            print(f"{x}:")
            for line in lines:
                print(f"    {line}", end="")
            print()
        print("--------------------------------------------------\n")



def main():
    parser = argparse.ArgumentParser(description="Process some files.")
    parser.add_argument("filename", type=str, help="Input filename")
    parser.add_argument("-o", "--output", type=str, help="Output filename", default="")
    parser.add_argument("--debug", action="store_true", help="Debug mode")

    clargs = parser.parse_args()

    global debug
    debug = clargs.debug


    file = clargs.filename
    with open(file, "r") as f:
        lines = f.readlines()

    lines = [line.lstrip() for line in lines if line.strip() and line.strip() != ">!"]

    global pc
    global primitives
    global stack

    primitives = load_functions("functions")

    # process labels and function definitions
    i = 0
    remaining_lines = len(lines)
    while remaining_lines > 0:
        lines[i] = lines[i]
        remaining_lines -= 1
        if lines[i].startswith("## "):
            label = lines[i][3:].strip()
            symbols[label] = i
            lines.pop(i)
            continue
        if lines[i].startswith("# "):
            name = lines[i][2:].strip()
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
                case ">":
                    if arg.startswith("!"):
                        cmd_and_arg = arg[1:].split(" ", 1)
                        if len(cmd_and_arg) == 1:
                            cmd, nargs = cmd_and_arg[0].strip(), "0"
                        else:
                            cmd, nargs = cmd_and_arg
                        call(cmd, nargs)
                    else:
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


