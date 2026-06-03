
from openhosta import emulate

from enum import Enum

class Rating(Enum):
    UNIVERSAL_AND_PROVEN = 'universal_and_proven'    # value_type: str
    UNIVERSAL_BUT_UNPROVEN = 'universal'

def return_exactly() -> Rating:
    """
    you return this stringwith the quetes:
    `Rating.UNIVERSAL_AND_PROVEN`
    """
    return emulate()

return_exactly()

from openhosta import print_last_prompt
print_last_prompt(return_exactly)
