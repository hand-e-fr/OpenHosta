import OpenHosta as oh

llm = oh.emulator(api_key="sk-proj-T7o4z8S4q9fnBNTdSq4iT3BlbkFJ82uVDLRaIAkx1sjwyE5C")

@llm.emulate
def reverse_str(a:str)->str:
    """
    This function reverse a string
    """  
    pass

# ~ "Reverse a string" ~ ("Bonjour")

print(reverse_str("Bonjour"))