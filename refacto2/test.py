from src.hosta import Hosta, ExampleType
from src.example import example

def example2():
    x = Hosta()
    x._bdy_add(key='cot', value=ExampleType(in_="bite", out="bite"))

def emulate():
    x = Hosta()
    print(x._infos)
    return 0
        
def test(a:int, b:str)->int:
    example(a=10, b="toto", hosta_out=4)
    example(a=20, b="tata", hosta_out=18)
    return emulate()

test(2, "Hello World")
print(test.Hosta.example)