import OpenHosta as oh

llm = oh.emulator()

@llm.enhance
def compute(string:str)->str:
    """
    This function reverse the string
    """
    pass

print(compute("Hello World !"))