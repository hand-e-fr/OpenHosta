from src.hosta import Hosta, ExampleType

def example(in_, out):
    x = Hosta()
    x._bdy_add("ex", ExampleType(in_=in_, out= out))
    return 0

def emulate():
    x = Hosta()
    print(x._infos)
    return 0
        
def test(a:int)->int:
    example(2, 4)
    example(9, 18)
    return emulate()

test(2)
print(test.Hosta.example)
