import OpenHosta as oh

llm = oh.emulator()

@llm.enhance
def compute(a:int, b:int)->int:
    """
    This function adds two intergers and multiply the result by the difference of them
    """
    pass

compute(4, 2)