from OpenHosta import emulate
from typing import List

def random_list()-> List[int]:
    """
    Return a list of random integers
    """
    return emulate()

print(random_list())