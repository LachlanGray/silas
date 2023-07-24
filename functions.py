import lmql

def unpack(func): # this can apply @query so theres one decorator
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        return result[0]
    return wrapper

@unpack
@lmql.query(model="openai/gpt-3.5-turbo", decoder="sample", temperature=0.75)
def gen(args: list):
    '''
    prompt = args
    for arg in args:
        "{arg}"
    "[completion]" where STOPS_AT(completion, "\n")
    prompt.append(completion)
    return prompt
    '''

@unpack
@lmql.query(model="openai/gpt-3.5-turbo", decoder="sample", temperature=0.75)
def extend(args: list):
    '''
    prompt = args
    for arg in args:
        "{arg}"
    "[completion]" where STOPS_AT(completion, "\n")
    prompt.append(completion)
    return "".join(prompt)
    '''

@unpack
@lmql.query(model="openai/gpt-3.5-turbo", decoder="sample", temperature=0.75)
def bool_reduce(*args):
    '''
    "{''.join(args).rstrip()}"
    "[completion]" where STOPS_AT(completion, "Yes") and STOPS_AT(completion, "yes") and STOPS_AT(completion, "No") and STOPS_AT(completion, "no")
    if "Yes" in completion or "yes" in completion:
        return "True\n"
    return "False\n"
    '''

l = [
    "is there anything wrong with this reasoning? yes or no:\n```\n"
    "here's how we make a cake:\n"
    "1: get milk from fridge\n",
    "2: get eggs from fridge\n",
    "3: get butter from fridge\n```\nanswer: ",
]

