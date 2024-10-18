from src.hosta import Hosta

def example():
    x = Hosta()
    return 0

def emulate():
    x = Hosta()
    print(x._infos)
    return 0
        
def test(a:int)->int:
    example()
    return emulate()

def test2(a:int)->int:
    return emulate()

test(2)
test2(3)

