from typing import Callable, Optional, Union, Tuple, _alias
from types import FrameType, MethodType, FunctionType
from dataclasses import dataclass, is_dataclass

import inspect

from OpenHosta.utils.errors import FrameError
import sys


from OpenHosta import Prompt

# TODO: test all combinations
# allow_thinking: T/F
# use_json_mode: T/F
# chain_of_thought: []
# examples_database: []

# Trois types de sortie LLM: string, json, python
# Map: 
# str -> string
# dataclass / pydantic -> json
# int, float, conplex, ...simple tupes... -> string + regexp
# callable -> python + regexp : test simple var definition + too call

# Input : python code, python repr, json, text
# Process: english string, python pseudo code 
# Output: string to regexp, string to json, string to regexp for python call plus data,  

EMULATE_PROMPT=Prompt("""\
You will act as a simulator for functions that cannot be implemented in actual code.
I'll provide you with function definitions described in Python syntax. These functions will have no body and may even be impossible to implement in real code, so do not attempt to generate the implementation.
Instead, imagine a realistic or reasonable output that matches the function description.
I'll ask questions by directly writing out function calls as one would call them in Python.
Respond with an appropriate return value{% if use_json_mode %} formatted as valid JSON{% endif %}, without adding any extra comments or explanations.
If the provided information isn't enough to determine a clear answer, respond simply with "None".
If assumptions need to be made, ensure they stay realistic, align with the provided description.
{% if not allow_thinking %}If unable to determine a clear answer or if assumptions need to be made, explain is in between <think></think> tags.{% endif %}


Here's the function definition:


```python
def {{ function_name }}({{ function_args }}) -> {{ function_return_as_python_type }}:
    \"\"\"{{ function_doc }}\"\"\"
    ...
    ...behavior to be simulated...
    ...
    return ...appropriate return value...
```
                      
{% if use_json_mode %}As you return the result in JSON format, here's the schema of the JSON object you should return:
{{{ function_return_as_json_schema }}}{% endif %}
                      
{% if examples_database %}Here are some examples of expected input and output:
{{{ examples_database }}}{% endif %}

{% if chain_of_thought %}To solve the request, you have to follow theses intermediate steps. Give only the final result, don't give the result of theses intermediate steps:
{{{ chain_of_thought }}}{% endif %}

{% if allow_thinking %}
If you need to think first, place your thought within <think></think> before answering like this:
<think>
The user might want ...
Wait, I have to...
</think>{% endif %}
""")


def identify_function_of_frame(function_frame):
    """
    frame -> code -> function

    We need to find the function pointer in order to store OpenHosta inspection object
    The main advantage over a centralized list is that this object will be deleted 
    a the same time than the associated function. Keeping a centrelized list would
    induce deletion issues.

    """
    
    function_code = function_frame.f_code
    function_name = function_frame.f_code.co_name
    function_pointer = None # This is to be found by the code below

    # First we look in every parent frame if the function exists there

    look_for_function_in_frame = function_frame.f_back
    while isinstance(look_for_function_in_frame, FrameType):
        
        for candidate_obj in look_for_function_in_frame.f_locals.values():
            # Use try catch as With Flask we found some strange behaviors for some candidate_obj
            try:
                # This is in case function exists in the caller stack
                if callable(candidate_obj) and hasattr(candidate_obj, "__code__"):
                    if candidate_obj.__code__ is function_code:
                        function_pointer = candidate_obj
                        break

            except Exception as e:
                raise FrameError("This is the strange error with Flask", e)
        
        look_for_function_in_frame = look_for_function_in_frame.f_back
    
    # Then look at the object in case we are a method of class
    if function_pointer is None:
        args_info = inspect.getargvalues(function_frame)
        if len(args_info.args) > 0:

            # first_arg_name should be 'self', 'cls' or any funny names)
            first_arg_name = args_info.args[0]
            
            # We get the first argument and check if is is a class 
            first_argument = args_info.locals[first_arg_name]
            
            # If the class has an attribute with our name, there is a good chance it is us
            bound_function = getattr(first_argument, function_name, None)
            if bound_function:
                if isinstance(bound_function, MethodType):
                    function_pointer = bound_function.__func__
                else:
                    # If function is a @staticmethod it does not have class as 
                    # first argument. But it was found by last part below.
                    pass

    # Finally we look in every parent frame if an object has the function
    # This is mainly for @staticmethod

    look_for_function_in_frame = function_frame.f_back
    while isinstance(look_for_function_in_frame, FrameType):
        
        for candidate_obj in look_for_function_in_frame.f_locals.values():
            # Use try catch as With Flask we found some strange behaviors for some candidate_obj
            try:
                # This is in case function was declared as @staticmethod
                if callable(candidate_obj) and hasattr(candidate_obj, function_name):
                    candidate_function = getattr(candidate_obj, function_name)
                    if isinstance(candidate_function, FunctionType) and \
                        candidate_function.__code__ is function_code:
                        function_pointer = candidate_function
                        break

            except Exception as e:
                raise FrameError("This is the strange error with Flask", e)
        
        look_for_function_in_frame = look_for_function_in_frame.f_back

    # Try in globals if not found in parent frames 
    if function_pointer is None:
        function_pointer = function_frame.f_globals.get(function_name, None)
    
    # In case there is a wrapper for class or global defined function
    if not function_pointer is None:
        function_pointer = inspect.unwrap(function_pointer) 

    if not function_pointer is None and \
       not function_pointer.__code__ is function_code:
        raise FrameError(f"We thought that we had found {function_name} but it is not the good one!")

    if function_pointer is None:
        raise Exception("Unable to find function for inspection")

    return function_pointer


def get_caller_frame():
    try:
        frame = sys._getframe(2)
    except ValueError as e:
        raise FrameError("get_caller_frame shall not be called from outsite of exec functions")
    
    return frame

def hosta_analyse_update(frame, analyse):
    args_info = inspect.getargvalues(frame)
    analyse["args"] = [{"name":a["name"], "value":args_info.locals[a["name"]], "type":a["type"]} for a in analyse["args"]] 
    return analyse

def hosta_analyze(frame, function_pointer):
    sig = inspect.signature(function_pointer)
    args_info = inspect.getargvalues(frame)
    
    result_args_value_table = [{
        "name":arg, 
        "value": args_info.locals[arg], 
        "type":sig.parameters[arg].annotation} for arg in args_info.args]
    

    result_function_name = function_pointer.__name__
    result_return_type = sig.return_annotation
    result_docstring = function_pointer.__doc__

    return {
        "name": result_function_name,
        "args": result_args_value_table,
        "type": result_return_type,
        "doc":  result_docstring
    }

def nice_type_name(obj) -> str:
    """
    Get a nice name for the type to insert in function description for LLM.
    """
    if type(obj) is _alias:
        t=obj.__repr__()
        t=t.replace("typing.", "")
        return t
    
    if hasattr(obj, "__name__"):
        return obj.__name__

    return str(obj)

def hosta_prompt_snippets(analyse):
    snippets = build_parameters_as_prompt(analyse["args"])

    snippets |= {
    "function_name"                  : analyse["name"],
    "function_return_as_python_type" : nice_type_name(analyse["type"]),
    "function_return_as_json_schema" : build_types_as_json_schema(analyse["type"]),
    "function_doc"                   : analyse["doc"],
    }

    python_call = "{function_name}({call_arguments})".format(**snippets)
    
    return snippets | {
        "function_call_as_python_code" : python_call,
    }

def describe_specific_types(arg_type):
    # TODO: add pydantic types
    type_definition = None
    if arg_type in vars(__builtins__).values() or\
        type(arg_type) is _alias or\
            arg_type == type:
        print("Ignore type", arg_type)
        # This is generic type. Assume it is known. 
        pass

    elif is_dataclass(arg_type):
        type_definition=f"""\
python class {arg_type.__name__} is defines as a @dataclass:
{arg_type.__doc__}
"""       
    elif hasattr(arg_type, '__annotations__')  and \
            not arg_type.__annotations__ is inspect._empty:
        type_definition=f"""\
python class {arg_type.__name__} has this annotation:
{arg_type.__annotations__}
"""
    else:
        # Unknwon types
        raise Exception(f"Unknwon type ({arg_type}). Please use another type.")

    return type_definition

# from pydantic import BaseModel, Field
# class Toto(BaseModel):
#     toto:str = Field(default="none", description="who is toto")

def build_parameters_as_prompt(args):
    variable_definition_list = []
    type_definition_list = []
    inline_string_list = []
    call_string_list = []
    
    for a in args:
        name, value, arg_type = a["name"], a["value"], a["type"]
        str_arg = name
        call_arg = name
        if arg_type is inspect._empty:
            pass
        else:
            str_arg += ": "+nice_type_name(arg_type) 
            print(name, value, arg_type)
            specifig_type_doc = describe_specific_types(arg_type)
            if not specifig_type_doc is None:
                type_definition_list.append(specifig_type_doc)

        # Place long variables outside function definition. 
        # math.pi is 17 char, I decide to cut at 20 
        str_value = repr(value)
        if len(str_value) > 20:
            variable_definition_list += [name+"="+str_value+"\n"]
        else:
            # We do not show default values as this could contradict values from call
            # str_arg += " = "+str_value
            call_arg += " = "+str_value

        inline_string_list += [str_arg]
        call_string_list   += [call_arg]

    return {
        "function_args":", ".join(inline_string_list),
        "call_arguments":", ".join(call_string_list), 
        "type_definitions":"\n".join(type_definition_list),
        "variable_declaration":"\n".join(variable_definition_list)
    }

def build_types_as_json_schema(arg_type):
    # TODO: build a JSON schema here
    return f"{describe_specific_types(arg_type)}"

def get_hota_inspection(frame):
    function_pointer = identify_function_of_frame(frame)  
    inspection = getattr(function_pointer, "hosta_inspection", None)
    
    if inspection == None:
        analyse = hosta_analyze(frame, function_pointer)
        inspection = {
            "function":function_pointer,
            "frame": frame,
            "analyse": analyse,
            "prompt_snippets":{}
        }
        setattr(function_pointer, "hosta_inspection", inspection)
    else:
        hosta_analyse_update(frame, inspection["analyse"])

    inspection["prompt_snippets"] = hosta_prompt_snippets(inspection["analyse"])

    return inspection


USER_CALL_PROMPT = Prompt("""
{% if variable_declaration %}# Values of parameters to be used
{{ variable_declaration }}{% endif %}
{{ function_call_as_python_code }}""")

def split_cot_answer(response:str) -> tuple[str, str]:
        """
        This function split response into rational and answer.

        Special prompt may ask for chain-of-thought or models might be trained to reason first.

        Args:
            response (str): response from the model.

        Returns:
            tuple[str, str]: rational and answer.
        """
        response = response.strip()

        if response.startswith("<think>") and "</think>" in response:
            chunks = response[8:].split("</think>")
            rational = chunks[0]
            answer = "</think>".join(chunks[1:]) # in case there are multiple </think> tags
        else:
            rational, answer = "", response
        
        return rational, answer

import json

def response_parser(response_dict:dict) -> dict:

    # if "usage" in response_dict:
    #     self._used_tokens += int(response_dict["usage"]["total_tokens"])

    response = response_dict["choices"][0]["message"]["content"]
    reasoning, answer = split_cot_answer(response)
    print(reasoning)
    try:
        l_ret_data = json.loads(answer)
    except json.JSONDecodeError as e:
        # If not a JSON, use as is
        l_ret_data = answer

    return l_ret_data

from OpenHosta import Model

default_model = Model(
        base_url="https://chat.hand-e.cloud/api/chat/completions",
        model='mistral-small-2503',#'chatgpt-4o-latest',
        api_key="sk-2063d493d39544089c3fe31f90d9b468",
        json_output=False
        )

def emulate(model=None):
    global default_model
    if not model is None:
        user_model = model
    else:
        user_model = default_model
    frame = get_caller_frame()
    inspection = get_hota_inspection(frame)
    print(inspection["prompt_snippets"])

    inspection["prompt_snippets"] |= {
        "use_json_mode":True,
        "allow_thinking":True
        }
    
    system_prompt_rendered = EMULATE_PROMPT.render(inspection["prompt_snippets"])
    print(system_prompt_rendered)
    user_prompt_rendered = USER_CALL_PROMPT.render(inspection["prompt_snippets"])
    print(user_prompt_rendered)

    response_dict = user_model.api_call([
            {"role": "system", "content": system_prompt_rendered},
            {"role": "user", "content": user_prompt_rendered}
        ]
    )
    untyped_response = response_parser(response_dict)
    return untyped_response

from typing import Dict

@dataclass
class Town:
    country:str
    long:float
    lat:float

def find_town(town_name:str, zip:int=None, *, size:int, alt:str=0, population=None) -> Town :
    """
    this function return the country and gps location of the town in parameter
    it also return the second word of alt
    """
    global frame
    frame = sys._getframe(0)
    return emulate()

r=find_town(town_name="glasgow", size="1M", alt="very long alt name for unused idea of value")
print(r)

@dataclass
class Client:
  name:str
  surname:str
  company:str
  email:str
  town:str
  address:str

def extract_client_name(text:str) -> Client:
    """
    This function translates the text in the “text” parameter into the language specified in the “language” parameter.
    """
    return emulate()

client1 = extract_client_name("FROM: sebastien@somecorp.com\nTO: shipment@hand-e.fr\nObject: do not send mail support@somecorp.com\n\nto Hello bob, I am Sebastian from Paris, france. Could you send me a sample of your main product? my office address is 3 rue de la république, Lyon 1er")
print(client1)



# Return types:
# - python: unsafe but better on small models
# - json: safe but slow and corrupted
# - raw: of for text only

### Exmaples


#### Example database

class Example:
    def __init__(self, **kwds):
        self.param=kwds
        self.values=[]
        self.is_unique = None
    
    def __eq__(self, value):
        self.value = value
        return self

    def returns(self, value):
        self.value = value
        return self

    def always_returns(self, value):
        if self.is_unique is False:
            raise Exception("You try to make unique a example that what already set as mutliple")
        self.is_unique = True
        self.values = [value]
        return self

    def may_returns(self, value):
        self.values.append(value)
        self.is_unique = False
        return self

    def __repr__(self):
        # This is supposed to be JSONL style, at least for basic types
        return '{' + f'"input": {self.param}, "output": {self.value}"' + '}\n'


def remember_that(**kwds):
    frame = get_caller_frame()
    inspection = get_hota_inspection(frame)
    example = Example(**kwds)
    if "example_database" not in inspection:
        inspection["example_database"] = []

    inspection["example_database"].append(example)
    return example 


### get_caller_function has to work with:
# - functions, 
# - objects methods, 
# - docorated function
# - decorated method
# - functions in functions, 
# - flask routed functions

# It returns:
# - the function pointer with its original name
# - the collable object that is used to reach this function (binder, wrapper, decorator, ...)

### function:
# - function pointer equals binder

def find_country_of_town(town_name, zip=None, *, size, alt=0, population=None) -> str:
    """
    this function return the country of the town in parameter
    """
    return emulate()

find_country_of_town(town_name="glasgow", size="1M")

# toto=find_country_of_town
# toto(45, "rdsd", dd=4)

### Object Method

class MyClass:
    Field1:int=3
    def methode_instance(self, b, arg, *, dd, fd=5, toto=44):
        return emulate()
    
    @staticmethod
    def staticmethod(b, arg, *, dd, fd=5, toto=44):
        return emulate()
    
    @classmethod
    def classmethod(cls, b, arg, *, dd, fd=5, toto=44):
        return emulate()
    
    def call_toto(self):
        return toto(45, "rdsd", dd=4)
    
    
mc = MyClass()
mc.methode_instance(45, "es", dd=5)
mc.staticmethod(45, "es", dd=5)
MyClass.staticmethod(45, "es", dd=5)
mc.classmethod(45, "es", dd=5)
MyClass.classmethod(45, "es", dd=5)

mc.call_toto()


### functions in functions

def foo(x=6):
    def foobar(val):
        return emulate()
    
    def bar(a=4):
        return foobar(a)
    return bar(x)

foo("f")

## Flask

from flask import Flask

app = Flask(__name__)

@app.route('/<page>')
def home(page=3)->str:
    return emulate()


if __name__ == '__main__':
    app.run(debug=True)



## Construct prompt

def my_function(b:int, arg:str, *, dd:int, fd:int=5, toto=44) -> Tuple:
    """
    This is my function that does simple things
    """
    remember_that(a=3, b='R').returns(4)
    return emulate()

frame = my_function(44, "rr", dd=4)
function_pointer = my_function

# my_function.hosta_inspection



# @dataclass
# class Personne:
#     nom: str
#     age: int
#     ville: str

# class PersonneN:
#     nom: str
#     age: int
#     ville: str
# # Création d'une instance de la classe
# personne0 = Personne(nom="Alice", age=30, ville="Paris")
# personne1 = Personne(nom="Alice", age=30, ville="Paris")

# personne2 = PersonneN()
# personne2.nom="Alice"
# personne2.age=30
# personne2.ville="Paris"
# personne2.__annotations__

# import json
# dataclass(MyClass).__annotations__
# MyClass.__annotations__

# personne0 == personne1
# personne1 == personne2


# # Affichage de l'objet
# print(personne1)

# personne1.__annotations__


