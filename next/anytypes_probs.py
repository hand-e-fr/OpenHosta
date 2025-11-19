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

from OpenHosta import emulate, max_uncertainty, print_last_uncertainty


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

[(x["token"], x["logprob"], len([y['logprob'] for y in x['top_logprobs'] if y['logprob']  > -11 ]), min(y['logprob'] for y in x['top_logprobs'])) for x in get_next_step.hosta_inspection["logs"]["llm_api_response"]["choices"][0]["logprobs"]["content"]]
    
print_last_uncertainty(name_of_president)

# This returns both estimations:
# name_of_president:
#  - with data: "Emmanuel Macron": estimated 5 possible answers
#  - with None: estimated 50 possible answers
# Uncertainty is estimated as (50 - 5 + 1) / 50 = 0.92
# The model is pretty confident in its answer, as it has eliminated most of the possible answers




from OpenHosta import max_uncertainty, print_last_probability_distribution, print_last_prompt

from OpenHosta import MetaPrompt, OneTurnConversationPipeline, config


def BestDate(assertion:str)->int:
    """
    This function return the best year for a given assertion.
    """
    return emulate(force_llm_args={"logprobs":True, "top_logprobs":20})

answer = BestDate("The fall of the Berlin Wall")
# returns something like "1989"

answer = BestDate("Emmanuel BATT's birth year")
print(answer)

[(x["token"], x["logprob"], len([y['logprob'] for y in x['top_logprobs'] if y['logprob']  > -11 ]), min(y['logprob'] for y in x['top_logprobs'])) for x in BestDate.hosta_inspection["logs"]["llm_api_response"]["choices"][0]["logprobs"]["content"]]

BestDate.hosta_inspection["logs"]["llm_api_response"]["choices"][0]["logprobs"]["content"][0]

def prod(lst):
    result = 1
    for x in lst:
        result *= x
    return result

def possible_aswers_count(function_pointer) -> int:
    return prod([len([y['logprob'] for y in x['top_logprobs'] if y['logprob']  > -11 ]) for i,x in enumerate(function_pointer.hosta_inspection["logs"]["llm_api_response"]["choices"][0]["logprobs"]["content"]) if not (i == 0 and (x["token"].startswith("'") or x["token"].startswith('"')) )])

def get_uncertainty(function_pointer) -> float:
    p0 = 1
    p1 = prod([len([y['logprob'] for y in x['top_logprobs'] if y['logprob']  > -11 ]) for i,x in enumerate(function_pointer.hosta_inspection["logs"]["llm_api_response"]["choices"][0]["logprobs"]["content"]) if not (i == 0 and (x["token"].startswith("'") or x["token"].startswith('"')) )])
    return  1 - p0 / p1

def print_path(function_pointer):
    print([(" ".join([y['token'] for y in x['top_logprobs'] if y['logprob']  > -11 ]), x["logprob"], len([y['logprob'] for y in x['top_logprobs'] if y['logprob']  > -11 ]), min(y['logprob'] for y in x['top_logprobs'])) for i,x in enumerate(function_pointer.hosta_inspection["logs"]["llm_api_response"]["choices"][0]["logprobs"]["content"]) if not (i == 0 and (x["token"].startswith("'") or x["token"].startswith('"')) )  ])

answer = BestDate("Emmanuel BATT's birth year")


answer = BestDate("The fall of the Berlin Wall")
answer = BestDate("l'année ne naissance du christ")
p0 = possible_aswers_count(BestDate)
p0 

print_path(BestDate)

answer = BestDate(None)
p1 = possible_aswers_count(BestDate)

print_path(BestDate)

import math
uncertainty = min(math.exp(-1e-11), 1 - ((p1 - p0 + 1) / p1))
print(f"Estimated uncertainty: {uncertainty:04f}. Logprob of beeing corect: {math.log(1-uncertainty)} (p0={p0}, p1={p1})")

get_uncertainty(BestDate)
# In only one prompt 1/1 = 1

BestDate("un siècle après -58 ")
print_path(BestDate)

def president_name(country:str, year:int)->str:
    """
    Return the name of the president
    """
    return emulate(force_llm_args={"logprobs":True, "top_logprobs":20})


president_name("lichtenstein", 1956)
get_uncertainty(president_name)
print_path(president_name)


def first_sentence_of(subject:str)->str:
    """
    Return the first sentence of a writing on the subject
    """
    return emulate(force_llm_args={"logprobs":True, "top_logprobs":20})


first_sentence_of("la belle au bois dormant")
possible_aswers_count(first_sentence_of)
first_sentence_of(None)
possible_aswers_count(first_sentence_of)
get_uncertainty(first_sentence_of)
print_path(first_sentence_of)

# Il faut pondérer par proba de chaque route pour négligrer les faibles branches.
# proba des chemins qui match la réponse vs les chemins envisagés