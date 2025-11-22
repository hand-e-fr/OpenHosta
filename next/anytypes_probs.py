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


# @max_uncertainty(threshold=0.9)
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
    
print_last_uncertainty(name_of_president)

# This returns both estimations:
# name_of_president:
#  - with data: "Emmanuel Macron": estimated 5 possible answers
#  - with None: estimated 50 possible answers
# Uncertainty is estimated as (50 - 5 + 1) / 50 = 0.92
# The model is pretty confident in its answer, as it has eliminated most of the possible answers




from OpenHosta import max_uncertainty, print_last_probability_distribution, print_last_prompt
from OpenHosta.utils.uncertainty import get_enum_logprobes, normalized_probs, has_discriminative_value, UncertaintyError

from OpenHosta import config
config.DefaultModel.model_name

import math

def get_certainty(function_pointer, vocabulary_sie=150000) -> float:
    """
    Calculates an uncertainty score based on the branching factor of log probabilities
    in the LLM response.
    
    The score represents 1 - (1 / total_likely_paths).
    """
    # 1. Extract the nested data source safely
    # This replaces: function_pointer.hosta_inspection["logs"]["llm_api_response"]["choices"][0]["logprobs"]["content"]
    try:
        response_logprobs = function_pointer.hosta_inspection["logs"]["llm_api_response"]["choices"][0]["logprobs"]["content"]
    except (KeyError, IndexError, AttributeError):
        # Handle cases where data is missing
        return 0.0

    selected_proportion = 1
    above_random_branches = 1

    # 2. Iterate through tokens to calculate branching options
    for i, token_data in enumerate(response_logprobs):
        token_text = token_data.get("token", "")
        
        # Condition: Skip the first token if it starts with a quote (' or ")
        # Original: if not (i == 0 and (x["token"].startswith("'") or x["token"].startswith('"')) )
        is_start_quote = (i == 0) and (token_text.startswith("'") or token_text.startswith('"'))
        
        if is_start_quote:
            continue

        # 3. Count "likely" alternatives for this token
        # Original: len([y['logprob'] for y in x['top_logprobs'] if y['logprob'] > -11 ])
        top_logprobs = token_data.get("top_logprobs", [])
        
        # Filter for probabilities greater than random (uniform distrubution over vocabulary size)
        likely_alternatives = [
            p for p in top_logprobs 
            if p.get('logprob', -float('inf')) > math.log(1/vocabulary_sie)
        ]
        
        above_random_branches *= len(likely_alternatives) 
        
        valid_mass = sum(math.exp(t["logprob"]) for t in likely_alternatives if token_text.startswith(t['token']))
        total_mass = sum(math.exp(t["logprob"]) for t in likely_alternatives)
        
        if total_mass == 0:
            step_probability = 1
        else:
            step_probability = valid_mass / total_mass 
        
        # We ignore other brnaches that could have lead to the same meaning.
        # Ideally we should considere them as valid as the uncertainty is on knwoledge and not on format
        selected_proportion *= step_probability
        
    return selected_proportion, above_random_branches   

def max_uncertainty_any(threshold:float=None, acceptable_log_uncertainty:float=None):

    if acceptable_log_uncertainty is not None:
        _threshold = math.pow(10, acceptable_log_uncertainty)
    elif threshold is not None:
        _threshold = threshold
    else:
        _threshold = 0.1

    def configuration_decorator(function_pointer):
        
        inner_func_pointer = None
        
        def wrapper(*args, **kwargs):
            
            setattr(function_pointer, "force_llm_args", {"logprobs": True, "top_logprobs": 20})
            
            # Call the function
            result = function_pointer(*args, **kwargs)
                
            setattr(inner_func_pointer, "hosta_inspection", function_pointer.hosta_inspection)
            
            selected_answer_certainty, above_random_branches = get_certainty(function_pointer)
            
            function_pointer.hosta_inspection["logs"]["enum_normalized_probs"] = {
                "unique_answer":selected_answer_certainty, 
                "multiple_answers":1-selected_answer_certainty, 
                }
            
            certainty = (selected_answer_certainty * above_random_branches ) / ( above_random_branches ) if above_random_branches > 0 else 1
            uncertainty = 1 - certainty

            print(f"Selected value probabilities: {selected_answer_certainty}, \n \
                    Uncertainty: {uncertainty} \n \
                    Required threshold: { 1 - _threshold}. \n \
                    - unique_answer probability: {selected_answer_certainty} \n \
                    - multiple_answers probability:{1-selected_answer_certainty} \n \
                    Above random answers: {above_random_branches} \n \
                    Estimates aswers: {1 + above_random_branches * (1-selected_answer_certainty):02f}")

               
            if uncertainty > _threshold:
                raise UncertaintyError(
                    f"The model did not return a discriminative value for the enum return type. Risk of hallucination.\n \
                    Selected value probabilities: {selected_answer_certainty}, \n \
                    Uncertainty: {uncertainty} \n \
                    Required threshold: { 1 - _threshold}. \n \
                    Above random answers: {above_random_branches} \n \
                    Estimates aswers: {1 + above_random_branches * (1-selected_answer_certainty):02f}")

            return result
        
        inner_func_pointer = wrapper        

        return wrapper
    
    return configuration_decorator

@max_uncertainty_any()
def BestDate(assertion:str)->int:
    """
    This function return the best year for a given assertion.
    """
    return emulate(force_llm_args={"logprobs":True, "top_logprobs":20})

answer = BestDate("The fall of the Berlin Wall")
# returns something like "1989"

print_last_probability_distribution(BestDate)

answer = BestDate("Emmanuel BATT's birth year")

a = []
for i in range(200):
    a.append( BestDate("Emmanuel BATT's birth year"))
print(len(set(a)))

print(answer)

answer = BestDate("l'année ne naissance du christ")

a = []
for i in range(20):
    a.append( BestDate("l'année ne naissance du christ"))
print(len(set(a)))

answer = BestDate('random')
# In only one prompt 1/1 = 1

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

# Il faut pondérer par proba de chaque route pour négligrer les faibles branches.
# proba des chemins qui match la réponse vs les chemins envisagés