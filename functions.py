import lmql

def unpack(func): # this can apply @query so theres one decorator
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        return result[0]
    return wrapper

@unpack
@lmql.query(model="openai/gpt-3.5-turbo", decoder="sample", temperature=0.75, cache=False)
def generate(args):
    '''
    prompt = args
    "{''.join(args)}"
    "[completion]" where STOPS_AT(completion, "\n")
    if not completion.endswith("\n"):
        completion += "\n"
    prompt.append(completion)
    return prompt
    '''

def gen(args):
    return generate(args)

@unpack
@lmql.query(model="openai/gpt-3.5-turbo", decoder="sample", temperature=0.75, cache=False)
def gen_reduce(args):
    '''
    prompt = list(args)
    "{''.join(prompt)}"
    "[completion]" where STOPS_AT(completion, "\n")
    if not completion.endswith("\n"):
        completion += "\n"
    return completion
    '''

@unpack
@lmql.query(model="openai/gpt-3.5-turbo", decoder="sample", temperature=0.75, cache=False)
def extend(args):
    '''
    prompt = list(args)
    "{''.join(prompt)[:-1]}"
    "[completion]" where STOPS_AT(completion, "\n")
    if not completion.endswith("\n"):
        completion += "\n"
    prompt.append(completion)
    return prompt
    '''

@unpack
@lmql.query(model="openai/gpt-3.5-turbo", decoder="sample", temperature=0)
def bool_reduce(args):
    '''
    "{''.join(args)[:-1]}"
    "[completion]" where STOPS_AT(completion, "Yes") and STOPS_AT(completion, "yes") and STOPS_AT(completion, "No") and STOPS_AT(completion, "no")
    if "Yes" in completion or "yes" in completion:
        return "True\n"
    return "False\n"
    '''
