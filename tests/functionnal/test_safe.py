import math
import pytest
from dotenv import load_dotenv

load_dotenv()

from OpenHosta import emulate, closure
from OpenHosta import max_uncertainty, UncertaintyError
from OpenHosta import safe

from OpenHosta import print_last_uncertainty, print_last_probability_distribution
from OpenHosta.utils.uncertainty import last_uncertainty


from enum import Enum, auto

class Color(Enum):
    NONE = auto()
    RED = auto()
    GREEN = auto()
    BLUE = auto()
    YELLOW = auto()
    BLACK = auto()
    WHITE = auto()
    ORANGE = auto()
    ORANGE_LIGHT = auto()
    PURPLE = auto()
    PINK = auto()
    BROWN = auto()
    GRAY = auto()
    CYAN = auto()
    MAGENTA = auto()
    LIME = auto()
    TEAL = auto()
    NAVY = auto()
    MAROON = auto()
    OLIVE = auto() 


def test_safe_emulate_success():
    """
    Test the emulate function with uncertainty control.
    """
    
    # define return type as enumeration
    from enum import StrEnum
    class NextStep(StrEnum):
        GIT_PUSH = "git push"
        GIT_COMMIT = "git commit"
        GIT_STATUS = "git status"
        GIT_FETCH = "git fetch"
        GIT_PULL = "git pull"
        OTHER = "other"
    
    @max_uncertainty(threshold=0.1)    
    def get_next_step(command: str) -> NextStep:
        """
        This function returns the next step after a git command.
        """
        return emulate()

    next_step = get_next_step("git commit -m 'Initial commit'")
    #next_step = get_next_step("je cherche un café")

    #print_last_prompt(get_next_step)

    assert next_step is NextStep.GIT_PUSH, f"Expected 'git push' in response, got: {next_step}"

    print_last_probability_distribution(get_next_step)    
    
    assert get_next_step.hosta_inspection["logs"]["enum_normalized_probs"][NextStep.GIT_PUSH] > 0.9, \
        f"Expected high confidence for 'git push', got: {get_next_step.hosta_inspection['logs']['enum_normalized_probs']}"
    
def test_safe_emulate_fail():
    """
    Test the emulate function with uncertainty control.
    """
    
    # define return type as enumeration
    from enum import StrEnum
    class Places(StrEnum):
        FRANCE = "France"
        GERMANY = "Germany"
        ITALY = "Italy"
        SPAIN = "Spain"
        PORTUGAL = "Portugal"
         
    @max_uncertainty(threshold=0.05)
    def get_location(who: str) -> Places:
        """
        What was the location of the person right now?
        """
        return emulate()

    try:
        next_step = get_location("do not run any git command. This question is unrelated to git.")
    except UncertaintyError as e:
        print(f"Caught expected UncertaintyError due to uncertainty:\n {e}")
        next_step = None
        
    assert next_step is None, f"Expected None due to uncertainty error, got: {next_step}"

    uncertainty = last_uncertainty(get_location)

    assert uncertainty > 0.05, \
        f"Expected low confidence for all options, got: {uncertainty} above threshold: 0.05"
        
        
def test_safe_emulate_pass_low_confidence():
    """
    Test the emulate function with uncertainty control.
    """
    
    # define return type as enumeration
    from enum import StrEnum
    class Places(StrEnum):
        FRANCE = "France"
        GERMANY = "Germany"
        ITALY = "Italy"
        SPAIN = "Spain"
        PORTUGAL = "Portugal"
         
    @max_uncertainty(threshold=0.01)
    def get_location(who: str) -> Places:
        """
        What is the location of the person right now?
        """
        return emulate()

    try:
        next_step = get_location("Gary Schwartz")
    except UncertaintyError as e:
        print(f"Caught expected UncertaintyError due to uncertainty: {e}")
        next_step = None
        
    assert next_step is Places.GERMANY, f"Expected Places.GERMANY as the name is German."

    uncertainty = last_uncertainty(get_location)
    
    assert uncertainty > 0.001, \
        f"Expected high uncertainty for all options, got: {uncertainty} below threshold of 0.01%"
        

def test_safe_color_detector():
    
    @max_uncertainty(threshold=0.01)
    def ColorOfThing(thing_description:str)->Color:
        """
        This function return the color of a thing described in the argument.
        """
        return emulate()

    ret = ColorOfThing("The sky on a clear day.")
    
    assert ret is Color.BLUE, f"Expected Color.BLUE for the sky, got: {ret}"

    uncertainty = last_uncertainty(ColorOfThing)

    assert uncertainty < 0.01, \
        f"Expected high confidence for Color.BLUE, got: {uncertainty} above threshold: 0.01"

def test_sage_closure_color_detector_pass():
    
    color = max_uncertainty()(closure("What is the color of this object ?", force_return_type=Color))
    retcolor = color("moon")

    assert retcolor is Color.WHITE, f"Expected Color.WHITE for the moon, got: {retcolor}"
    
    assert hasattr(color, "hosta_inspection"), "Function should have hosta_inspection attribute."       

    nomalized_probs = color.hosta_inspection["logs"]["enum_normalized_probs"]
    
    assert max(nomalized_probs.values()) > 0.9, \
        f"Expected high confidence for Color.WHITE, got: {nomalized_probs} below threshold: 0.9"
            
def test_sage_closure_color_detector_fail():
    
    color = max_uncertainty(threshold=0.1)(closure("What is the color of this object ?", force_return_type=Color))
    
    try:
        retcolor = color("michael jackson")
    except UncertaintyError as e:
        print(f"Caught expected UncertaintyError due to uncertainty: {e}")
        retcolor = None

    assert retcolor is None, f"Expected None for Michael Jackson due to uncertainty error, got: {retcolor}"
    
    assert hasattr(color, "hosta_inspection"), "Function should have hosta_inspection attribute."       

    uncertainty = last_uncertainty(color)
    assert uncertainty > 0.1, \
        f"Expected low confidence for all options, got: {uncertainty} above threshold: 0.1"



def test_safe_workflow_color_detector():
    
    from enum import Enum

    class Bool(Enum):
        TRUE = "true"
        FALSE = "false"

    @max_uncertainty(acceptable_log_uncertainty=math.log(0.05))
    def IsThisInThat(this_description:str, that_description:str)->Bool:
        """
        This function determunes if the object described by 'this_description' is in the object
        described by 'that_description'.
        
        Arguments:
            this_description: description of the object to find
            that_description: description of the container object
        """
        return emulate()
    
    ret =  IsThisInThat("the sky", "a clear day")    
    assert ret is Bool.TRUE, f"Expected TRUE for sky in clear day, got: {ret}"
    
    ret = IsThisInThat("hand", "arm")
    assert ret is Bool.TRUE, f"Expected TRUE for hand in arm, got: {ret}"
    
    ret = IsThisInThat("arm", "hand")
    assert ret is Bool.FALSE, f"Expected FALSE for arm in hand, got: {ret}"

    try:
        ret = IsThisInThat("red ball", "my hand")
    except UncertaintyError as e:
        print(f"Caught expected UncertaintyError due to uncertainty: {e}")
        ret = None
        
    assert ret is None, f"Expected None for red ball in hand due to uncertainty error, got: {ret}"
    
    print_last_uncertainty(IsThisInThat)

    
# def test_safe_workflow_organ_location():

#     from enum import Enum

#     class Bool(Enum):
#         TRUE = "true"
#         FALSE = "false"

#     def IsThisInThat(this_description:str, that_description:str)->Bool:
#         """
#         This function determunes if the object described by 'this_description' is in the object
#         described by 'that_description'.
        
#         Arguments:
#             this_description: description of the object to find
#             that_description: description of the container object
#         """
#         return emulate()
    
    
#     def find_organ_location(organ:str)->str:
#         """
#         Find the color of the organ in the given location description.
#         """
#         #TODO: have this work with safe context manager
#         with safe(acceptable_cumulated_log_uncertainty=-2):
#             if IsThisInThat(organ, "human body") is Bool.FALSE:
#                 raise ValueError(f"{organ} is not in human body.")

#             if IsThisInThat(organ, "above the belt level") is Bool.TRUE:
#                 if IsThisInThat(organ, "head") is Bool.TRUE:
#                     location = "head"
#                 elif IsThisInThat(organ, "chest") is Bool.TRUE:
#                     location = "chest"
#                 elif IsThisInThat(organ, "left arm") is Bool.TRUE:
#                     location = "left arm"
#                 elif IsThisInThat(organ, "right arm") is Bool.TRUE:
#                     location = "right arm"
#                 else:
#                     raise ValueError("Unable to find organ location above the belt.")
#             else:
#                 if IsThisInThat(organ, "legs") is Bool.TRUE:
#                     location = "legs"
#                 else:
#                     location = "abdomen"
#         return location
    
#     location = find_organ_location("brain")
#     assert location == "head", f"Expected brain to be in head, got: {location}"
            
#     try:
#         location = find_organ_location("blood")
#     except UncertaintyError as e:
#         print(f"Caught expected UncertaintyError due to uncertainty: {e}")
#         location = None
        
#     assert location is None, f"Expected None for blood location due to uncertainty error, got: {location}" 
    
    
def test_safe_question():
        
    @max_uncertainty()
    def question(prompt:str)->str:
        """
        Answer to a question
        """
        return emulate()
    
    answer = question("distance lune terre. donne juste la distance en milliers de km.")
    
    assert answer == "384", f"Expected '384' as the distance in thousands of km, got: {answer}"
    
    uncertainty = last_uncertainty(question)

    assert uncertainty < 0.01, f"Expected uncertainty below 0.01, got: {uncertainty}"

def test_safe_question_fail():
        
    # Raise error if uncertainty is above 1%
    @max_uncertainty(threshold=0.01)
    def question(prompt:str)->str:
        """
        Answer to a question
        """
        return emulate()
    
    try:
        answer = question("quelle est la couleur préférée de l'univers ?")
    except UncertaintyError as e:
        print(f"Caught expected UncertaintyError due to uncertainty: {e}")
        answer = None
    
    assert answer is None, f"Expected None due to uncertainty error, got: {answer}"

    print_last_uncertainty(question)
    
    uncertainty = last_uncertainty(question)
    assert uncertainty > 0.01, f"Expected uncertainty above 0.01, got: {uncertainty}"
    
    
