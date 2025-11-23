## L'idée est d'estimer le nombre de réponses envidagées par le LLM
# On compare ce nombre lorsque l'entrée est nulle versus lorsque l'entrée est fournie.
# Si le LLM envisage Rdata=10 réponses possibles pour une entrée donnée, Rnull=10e5 lorsque l'entrée est nulle,
# On peut estimer qu'avec l'entrée donnée, il a décider d'éliminer (10e5 -10) réponses possibles.
# Sa confiance peut être estimée comme le ratio entre les réponses envisagées avec l'entrée donnée
# et les réponses envisagées avec l'entrée nulle.
# soit Confiance = (Rnull - Rdata + 1) / ( Rnull )

# Etude aux limites:
# - Si Rdata est proche de Rnull, confiance proche de 0 => le LLM n'a pas su utiliser l'entrée pour éliminer des réponses possibles
# - Si Rdata est proche de 1, confiance proche de 1 => le LLM a éliminé presque toutes les réponses possibles, il est donc très confiant.

from OpenHosta import emulate, max_uncertainty, print_last_prompt

@max_uncertainty(threshold=0.9)
def name_of_president(country:str, year:int)->str:
    """
    Returns the name of the president of the given country.
    
    Args:
        country (str): The name of the country.
        year (int): The year for which to find the president.
        
    Returns:
        str: The name of the president.
    """
    return emulate()


answer = name_of_president("France", 2021)
# This run the function two times, once with the data, once with None
# In order to approximate the uncertainty of the model, we take:
#  - the lower estimator when the model is given no input. (all takens that are start of the chosen one are supposed to be identical)
#  - the higher estimator when the model is given input. (all tokens are supposed to be different)
# ! We need to decide how to separate tokens that are assumed to be acceptable path. We use Enthropy thresholding for that:
#  - Tokens with probability higher than (1 / number_of_possible_answers) are considered acceptable.
# log(1/150000) = -11.92 
    
print_last_prompt(name_of_president)

# This returns both estimations:
# name_of_president:
#  - with data: "Emmanuel Macron": estimated 5 possible answers
#  - with None: estimated 50 possible answers
# Uncertainty is estimated as (50 - 5 + 1) / 50 = 0.92
# The model is pretty confident in its answer, as it has eliminated most of the possible answers

from OpenHosta import max_uncertainty, print_last_prompt, print_last_uncertainty

from OpenHosta import config, emulate
config.DefaultModel.model_name

@max_uncertainty()
def BestDate(assertion:str)->int:
    """
    This function return the best year for a given assertion.
    """
    return emulate(force_llm_args={"logprobs":True, "top_logprobs":20})

answer = BestDate("The fall of the Berlin Wall")
# returns something like "1989"

print_last_uncertainty(BestDate)
print_last_prompt(BestDate)

answer = BestDate("Emmanuel BATT's birth year")
answer = BestDate("l'année ne naissance du christ")

from OpenHosta.utils.uncertainty import last_uncertainty
a = []
b = []
for i in range(30):
    #answer = BestDate("Célestine birth year")
    answer = BestDate("l'année ne naissance du christ")
    a.append(answer)
    b.append(last_uncertainty(BestDate))

import collections 
collections.Counter(a)

print(len(set(a)))
print(b)

answer = BestDate('random')
# In only one prompt 1/1 = 1

BestDate("le jour le plus long")
print_last_uncertainty(BestDate)

BestDate("un siècle après -58 ")

def president_name(country:str, year:int)->str:
    """
    Return the name of the president
    """
    return emulate(force_llm_args={"logprobs":True, "top_logprobs":20})


president_name("lichtenstein", 1956)


def first_sentence_of(subject:str)->str:
    """
    Return the first sentence of a writing on the subject
    """
    return emulate(force_llm_args={"logprobs":True, "top_logprobs":20})


first_sentence_of("la belle au bois dormant")
first_sentence_of(None)


@max_uncertainty()
def question(prompt:str)->str:
    """
    Answer to a question
    """
    return emulate()

question("distance lune terre. donne juste la distance en km en notation scientifique avec 2 chiffre scinificatif.")
question("distance lune terre. donne juste la distance en milliers de km.")
print_last_uncertainty(question)

from dataclasses import dataclass

@dataclass
class Person:
    name:str
    last_name:str
    
@max_uncertainty()
def extract_name(snippet:str) -> Person:
    """
    Identify the person in a snippet of text.
        
    Return:
       a Person object (str are in between ')
    """
    return emulate()

extract_name("le gagnant des élections de 1986 est Jean-Edouard. il est le fils de Charles Dupond et a conservé le nom de famille")
print_last_uncertainty(extract_name)

import math
i=1
i+=1
[(x["token"], math.exp(x["logprob"])) for x in sorted(extract_name.hosta_inspection["logs"]["llm_api_response"]["choices"][0]["logprobs"]["content"][i]["top_logprobs"], key=lambda x: -x["logprob"])[:4]]