### Tihs is an idea to have guards as objects
### 
### The main idea is to have a base class Guard that will be inherited by other classes
### Each class will implement the guard_test method that will test if the value is valid
### If the value is not valid, a TypeError will be raised
###
### It is based on the theory of types. A type is a set of values that share a common property.
### For example, the type "positive integer" is a set of integers that are greater than zero.
### The type "email address" is a set of strings that follow the format of an email address.
### The type "insult" is a set of strings that are insults.
###
### This would also allow to have complex types that are composed of other types.
### For example, an email address could contain an insult.
### 

# In this case, Guard is a better name than Constraint as verification appends after the creation of the data by the LLM.
# We could use Constraint for regular expressions that would bias the generation of the LLM's tokens to respect the constraint.
from OpenHosta.semantics import Guard 

class SentenceType(Guard):
    pass

class InsultType(SentenceType):
    # This is just to show that we can have multiple levels of inheritance
    pass

s0=SentenceType("you are a nice guy") 
if isinstance(s0, InsultType):
    print("s0 is an insult")
else:
    print("s0 is not an insult")

### Suggested implementation from gemini-2.5-pro
# https://g.co/gemini/share/52e79c93460b

### Suggested implementation from the workshop between Leandre and Emmanuel

from abc import ABC, abstractmethod

class Guard(ABC):
    def __init__(self, value:str|dict):
        
        self.guard_test(value)
        
        self.value = value
        
    @abstractmethod
    def guard_test(self, value:str|dict)->bool:
        raise NotImplementedError("You must implement the guard_test method")
    
    def __repr__(self):
        return f"{self.__class__.__name__}({self.value})"
    
    def __str__(self):
        return str(self.value)
    
class InsultType(Guard):
    def guard_test(self, value:str|dict)->bool:
        """
        This function tests if the value is a valid insult.
        """
        def is_insult(text:str)->bool:        
            return emulate()
        
        def explain_why_it_is_not_an_insult(text:str)->str:
            return emulate()

        if not is_insult(value):
            raise TypeError(f"The value is not a valid insult: {explain_why_it_is_not_an_insult(value)}")


insult = InsultType("You are a nice guy")


class MyEmailType:
    def __init__(self, email: str):
        if "@" not in email or "." not in email.split("@")[-1]:
            raise ValueError(f"Invalid email address: {email}")
        self.email = email
    
    def __str__(self):
        return self.email
    
class RetryPipeline:
    def __init__(self, retries:int=3):
        self.retries = retries
    
    def pull(self, message: str) -> str:

        
        
from OpenHosta import emulate, print_last_decoding, print_last_prompt
from dataclasses import dataclass

@dataclass
class User:
    name: str
    email: str

def get_user_email(message:str) -> InsultType:
    """
    This function asks the user for their email address and returns it as a MyEmailType.
    
    explain the mistakes before answering in between <think> </think> tags.
    """
    return emulate()

try:
    user = get_user_email("my name is Emmanuel and (my email is ebatt @hand .com)")
except TypeError as e:
    print(f"Caught TypeError: {e}")
    
    
print_last_prompt(get_user_email)
print_last_decoding(get_user_email)

def my_workflow(user_input:str) -> InsultType:
    """
    This function takes a user input and returns an insult.
    """
    theme = self.my_theme
    
    thought("Make a long story about the theme")
    toto = thought("Make a long story about the theme")
    toto:Sentence = thought("Make a long story about the theme")
    
    a_long_story:StoryType  = thought("Make a long story about the theme")
    
    SomeInsult:SentenceType = thought("Make an insult about the story")
    return emulate()

