# Doit etre mieux que (pus simple a comprendre, a utiliser et plus complet):
# - https://github.com/prefect-archive/ControlFlow/blob/main/examples/anonymization.py
# - https://pypi.org/project/marvin/
# - DSPy

# from openhosta import auto, emulate, formulate, use, Guarded
from openhosta import HostaModel, Guarded, guard, unguard, GuardConfig
from typing import Callable, Annotated, TypeAlias

qwen:HostaModel = HostaModel(
    model="qwen3.5:4b",
    base_url="http://localhost:11434/v1",
    capabilities={
        "logprobs", "streaming"
    }
)

# Par default le modele test Ollama puis OpenAI.
# Ollama+qwen3.5:4b doit être ok sur tous les tests 

#### OpenHosta: IA-as-a-Function for Zero DSL Agents in poduction 

# Utilisation de OpenTelemetry ? ou logging native python ?
# OpenHosta = un minimum de dépendances => loggin + hooks
# Support de pylance strict
# Modèle de référence pour les tests qwen3.5:4b {effor:none} via ollama

# ultra basic usage

@qwen.auto_body
def translate_to_en(text: str) -> str:
    """
    Translate the text to french
    """
    ...

fr = translate_to_en("Hello world")

# But you need to know how uncertain the traslation was

@qwen.auto_body
def translate_to_en_with_audit(text: str) -> Guarded[str]:
    """
    Translate the text to french
    """
    ...

fr = translate_to_en("Hello world")

print(fr) # "Bonjour le monde"
print(type(fr)) # Guarded[str]
print(type(unguard(fr))) # str

assert fr == unguard(guard(fr)) # True
assert guard(unguard(fr)) == fr  # Oui mais les metadata ont été perdues

SafeTranslation:TypeAlias = Annotated[Guarded[str], GuardConfig(max_effort_ms=1000, max_uncertainty=0.5)]

@qwen.auto_body
def translate_to_en_with_limit_by_annotation(text: str) -> SafeTranslation:
    """
    Translate the text to french
    """
    ...

fr = translate_to_en("Hello world")



@qwen.auto_body(GuardConfig(max_effort_ms=1000, max_uncertainty=0.5))
def translate_to_en_with_limit_by_config(text: str) -> Guarded[str]:
    """
    Translate the text to french
    """
    ...

fr = translate_to_en("Hello world")

### Dans le cas ou il y a les deux, la config du décorateur est prioritaire et écrase celle du type
@qwen.auto_body(GuardConfig(max_effort_ms=100, max_uncertainty=0.2))
def translate_to_en_with_limit_by_config_and_annotation(text: str) -> SafeTranslation:
    """
    Translate the text to french
    """
    ...

fr = translate_to_en("Hello world")


SafeWordTranslation:TypeAlias = Annotated[SafeTranslation, GuardConfig(max_effort_ms=2000, max_uncertainty=0.2)]

@qwen.auto_body
def translate_to_en_with_limit_by_multiple_annotations(text: str) -> SafeWordTranslation:
    """
    Translate the text to french
    """
    ...

fr = translate_to_en("Hello world")

#### Le plus simple : 
#
# @qwen.auto_body et c'est fait. 
#  - Utilise default model, 
#  - ne trace pas l'incertitude, 
#  - ne trace pas les couts, 
#  - 60s retry si api limit, 
#  - 2x retry si api error, 
#  - 2x retry si casting error
# 
# la syntaxe en décorateur avec ... permet de passer toutes les vérifications des linters
#
# PR: Ne doit pas générer d'erreur au linter

from openhosta import envmodel

model = envmodel()

@model.auto_body
def translate(text: str, target_language: str) -> str:
    """
    Translates the given text to the target language.
    """
    ...

#### Just Python, no DSL
# 
# Just use Python types and it's done
# - there is no domain specific language to learn. If you learn something new, it shall be python
# - you become better at python, not at a new DSL that will disapera in a few years

from dataclasses import dataclass

@dataclass
class Person:
    name: str
    age: int
    address: str

#### easy coroutine
# 
# Just add async and it's done
#
# - whatever the return type, just add async and it becomes a coroutine. Single change, no more to do

@model.auto_body
async def identify_person(text: str) -> Person:
    """
    Find the first person in the text and return it
    """
    ...


#### Support for list of objects
#
# Just add list[] and it's done
#
# - You way have multiple return of the same type, add list[] and it's done

@model.auto_body
async def identify_persons(long_text: str) -> list[Person]:
    """
    Find all persons in the text and return them
    """
    ...

#### Support for list of objects
#
# Just add list[] and it's done
#
# - You way have multiple return of the same type, add list[] and it's done

from typing import Iterator

@model.auto_body
def persons_in(long_text: str) -> Iterator[Person]:
    """
    Find all persons in the text and yield them one by one
    """
    ...


#### Support for Guarded objects
# 
# Just add Guarded[] and it's done
# - You get full debug information about the LLM call, LLM reasoning, chat messages and LLM response parsing.
# - You get uncertainty score based on LLM logprobs (if API supports toplogprobs)
# - You get cost tracability

@model.auto_body
def probable_persons_in(long_text: str) -> Iterator[Guarded[Person]]:
    """
    Find all persons in the text and yield them one by one
    """
    ...
    
values = list(probable_persons_in("a long text with 3 persons : Emmanuel Macron, Joe Biden and Angela Merkel"))

print(values) # ["Emmanuel Macron", "Joe Biden", "Angela Merkel"]
gval:Guarded[list[Guarded[Person]]] = guard(values)

from openhosta import guard_info
guard_info(gval).uncertainty # sum of 3 uncertainties from the 3 Person instances

#### Provide context in the docstring
#
# As you would have done it in a regular function
# - Same mindset if you plan to implement yourself or delegate to an LLM
# - Fast prototyping of complex functions
# - Documentation is near the code
# - You refactor for performance ? The docstring does not change! nor your architecture.
#

@model.auto_body
def persons_by_name(long_text: str) -> Guarded[dict[str,Person]]:
    """
    Find all persons in the text and build a dictionary of them by full name
    
    Arguments:
        long_text: The text to search for persons in
        
    Returns:
       A dictionary of persons by full name
    """
    ...

from pandas import DataFrame
from typing import Callable

#### formulate_body will inspect the data on the first call to decide how to implement the function
# It will try to generalize
# It will generate test vectors to validate the implementation

@model.formulate_body
def filter_by_country(source: DataFrame, countries:list[str]) -> DataFrame:
    """
    Filter lines in the source dataframe to only keep those with a country in the list of countries to keep
    The list of countries to keep is provided in the query as a list of country codes in the ISO 3166-1 alpha-2 format
    
    Arguments:
        source: The dataframe to filter with three columns designating the country: CountryName, CountryCode, Location
        countries: The list of countries to keep
        
    Returns:
        The filtered dataframe
    """
    ...


# with formulate_body, GuardConfig() decribes the formulation process
# The uncertainty it the uncertainty of the generated function

@model.formulate_body(GuardConfig(max_effort_ms=30000))
def filter_by_country_with_limit(source: DataFrame, countries:list[str]) -> DataFrame:
    """
    Filter lines in the source dataframe to only keep those with a country in the list of countries to keep
    The list of countries to keep is provided in the query as a list of country codes in the ISO 3166-1 alpha-2 format
    
    Arguments:
        source: The dataframe to filter with three columns designating the country: CountryName, CountryCode, Location
        countries: The list of countries to keep
        
    Returns:
        The filtered dataframe
    """
    ...

# annotation de filter_by_country: Guarded[Callable[[DataFrame, list[str]], DataFrame]]
assert isinstance(filter_by_country, Guarded)

from openhosta import guarded_to_python

print(guarded_to_python(filter_by_country)) # Print the python code generated by the LLM

## Pour passer une fonction à un LLM dans un prompt il suffit d'utiliser guarded_to_python()

def add_two_int(a:int, b:int) -> int:
    """
    Add two int
    """
    return a+b

guarded_to_python(add_two_int) # Print the function prototype with annotations and docstring

# Output:
# def add_two_int(a: int, b: int) -> int:
#     """
#     Add two int
#     """
#     ...

    
# 30s pour build une fonction de filtrage d'après la specification
@model.emulate_body(GuardConfig(max_effort_ms=30000))
def filter(filter_request: str, source_metadata: str) -> Callable[[DataFrame],DataFrame]:
    """
    Return the python code to filter the data as requested by the query
    """
    ...
    
import pandas as pd

@model.auto_body(use=[pd], max_cost=1e6, max_uncertainty=0.05)
def auto_filter(filter_query:str, data:pd.DataFrame) -> Guarded[pd.DataFrame]:
    """
    Filter the data using the query and return the result
    """
    ...

iris:DataFrame = pd.DataFrame({"name"+n:range(10) for n in "abcdefghijklmnopqrstuvwxyz"})

odd_lines = auto_filter("garde les lignes paires", iris)

@model.formulate_body(use=[pd], max_cost=1e6, max_uncertainty=0.05)
def generic_filter(filter_query:str, data:pd.DataFrame) -> Guarded[Callable[[pd.DataFrame],pd.DataFrame]]:
    """
    Filter the data using the query and return the result
    """
    ...

generic_filter("grosses fleurs", iris)


##### Et en streaming ? 


##### Et si je fais mon propre prompt ?


##### et le semantic collections