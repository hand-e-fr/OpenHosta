### This file describe a partial implementation of logprobes for enum return types.
### It is not yet integrated in the main codebase, but it is a proof of concept
### It show how we plan to get small embeddings for enum values and use them to improve the accuracy of the model.
### This is important for vectorial memory

from OpenHosta import reload_dotenv, config
reload_dotenv()

# Works only with gpt-4o and gpt-4.1
#DefaultModel.model_name

import math
from typing import Dict

def posterior_probability(prediction, possible_outcomes, prior_prob_list:Dict[str,float] = {}, previouse_string = "") -> dict:

    # Fill prior_prob_list with uniform distribution if empty
    for outcome_tuple in possible_outcomes:
        if outcome_tuple[0] not in prior_prob_list:
            prior_prob_list[outcome_tuple[0]] = 1.0 / len(possible_outcomes)

    # Normalize prior_prob_list
    total_prob = sum(prior_prob_list.values())
    prior_prob_list = {k: v/total_prob for k,v in prior_prob_list.items()}

    probability_distribution = {k[0]:0 for i,k in enumerate(possible_outcomes)}
    
    min_prob = 1.0
    for outcome_tuple in possible_outcomes:
        #print("Checking variant:", outcome_tuple[0])
        for variant in outcome_tuple:
            for alternative in prediction["top_logprobs"]:
                min_prob = min(min_prob, math.exp(alternative["logprob"]))
                assert isinstance(variant, str)
                generated_text = previouse_string+alternative["token"]
                if len(generated_text) > 0 and variant.startswith(generated_text):
                    prob = math.exp(alternative["logprob"])
                    #print(f"{variant}\t{generated_text}\t{probability_distribution[outcome_tuple[0]]:0.4f} +P:{prob:0.4f} = {probability_distribution[outcome_tuple[0]] + prob:0.4f}")
                    probability_distribution[outcome_tuple[0]] += prob

    # For outcomes that were not in the prediction at all, we set a minimum probability
    # As we mill data, we use the worst case scenario: the minimum logprob observed
    for outcome in probability_distribution:
        if probability_distribution[outcome] == 0:
            #print(f"Outcome '{outcome}' was not found in prediction.")
            if len(previouse_string) > 0:
                selected_variant = [variant for outcome_tuple in possible_outcomes if outcome_tuple[0]==outcome for variant in outcome_tuple if variant.startswith(previouse_string)]
                #print(f'We had previouse string "{previouse_string}", checking for matching {len(selected_variant)} variants: {selected_variant}')
                if any(selected_variant):
                    # This outcome had at least one variant that matched the previouse string
                    # But was not found in the prediction, so we know its prob is lower than the lowest predicted one
                    #print(f"Outcome '{outcome}' had matching variant(s) {selected_variant} but was not found in prediction. Assigning min prob {min_prob:0.6f}")
                    probability_distribution[outcome] = min_prob
                else:
                    # The worst case is that other path would have found perfect matching tokens
                    #print(f"Outcome '{outcome}' had no matching variant for previouse string '{previouse_string}'. Assigning prob 1.0")
                    probability_distribution[outcome] = 1.0
            else:
                # As we are at the begining, we can use the minimum prob observed
                #print(f"Outcome '{outcome}' was not found in prediction. Assigning min prob {min_prob:0.6f}")
                probability_distribution[outcome] = min_prob

    # Normalize the distribution
    total = sum(probability_distribution.values())
    for outcome in probability_distribution:
        probability_distribution[outcome] /= total

    # Combine with prior logprob
    for outcome in probability_distribution:
        probability_distribution[outcome] *= prior_prob_list.get(outcome)
    # Re-normalize
    total = sum(probability_distribution.values())
    if total == 0:
        total = 1.0 
        
    for outcome in probability_distribution:
        probability_distribution[outcome] /= total
    
    # Return the final likelihood as logprobs
    logprob_distribution = {}
    for outcome in probability_distribution:
        logprob_distribution[outcome] = math.log(probability_distribution[outcome])

    return logprob_distribution

# Test is the probabilit distribution has a value that is discriminative enough
def has_discriminative_value(logprob_distribution:dict, threshold:float=0.7)->bool:
    max_logprob = max(logprob_distribution.values())
    exp_values = {k: math.exp(v - max_logprob) for k,v in logprob_distribution.items()}
    total = sum(exp_values.values())
    normalized_probs = {k: v/total for k,v in exp_values.items()}
    for k,v in normalized_probs.items():
        if v >= threshold:
            return True
    return False

def most_probable_value(logprob_distribution:dict)->str:
    max_logprob = max(logprob_distribution.values())
    exp_values = {k: math.exp(v - max_logprob) for k,v in logprob_distribution.items()}
    total = sum(exp_values.values())
    normalized_probs = {k: v/total for k,v in exp_values.items()}
    sorted_probs = sorted(normalized_probs.items(), key=lambda item: item[1], reverse=True)
    return sorted_probs[0][0], sorted_probs[0][1]

# Not yet supported by ollama, supported by gpt-4o and gpt-4.1
def get_enum_logprobes(*,function_pointer=None, inspection=None)->dict:
    if inspection is None and function_pointer is not None:
        if not hasattr(function_pointer, "hosta_inspection"):
            raise ValueError("Function pointer does not have hosta_inspection attribute. Did you call this function at least once?")
        inspection = function_pointer.hosta_inspection 
    elif inspection is not None:
        pass
    else:
        raise ValueError("Either function_pointer or inspection must be provided")
    
    response_dict = inspection["logs"]["llm_api_response"]
    return_type = inspection["analyse"]["type"]
    assert issubclass(return_type, Enum), "Return type is not an Enum"

    assert "logprobs" in response_dict["choices"][0], "Model response does not contain logprobs. Make sure the model supports logprobs."
    assert "top_logprobs" in response_dict["choices"][0]["logprobs"]["content"][0], "Model response does not contain top_logprobs. Make sure the model supports logprobs."

    logp_list = response_dict["choices"][0]["logprobs"]["content"]
    if len(logp_list) <= 0:
        print(f"Warning: not enough logprobs ({len(logp_list)})")
        return {}

    possible_outcomes = [(
        str(v.value),
        f'"{v.value}"', 
        f"'{v.value}'", 
        str(v.name).upper(), 
        str(v.name).lower(), 
        str(v.name), 
        f'"{v.name}"', 
        f"'{v.name}'", 
        f"<{return_type.__name__}.{v.name}>", 
        f"{return_type.__name__}.{v.name}", 
        ) for v in list(return_type)]

    prior_prob_list = {}
    previouse_string = ""
    for prediction in logp_list:
        #print(f"Stepping through prediction token: '{prediction['token']}'")
        logprobes = posterior_probability(prediction, possible_outcomes, prior_prob_list=prior_prob_list, previouse_string=previouse_string)
        prior_prob_list = {k: math.exp(v) for k,v in logprobes.items()}
        previouse_string += prediction['token']
        
    return logprobes

def safe(threshold:float=0.8):

    def configuration_decorator(function_pointer):
        
        inner_func_pointer = None
        
        def wrapper(*args, **kwargs):
            
            previouse_model_params = config.DefaultModel.api_parameters.copy()
            config.DefaultModel.api_parameters |= {"logprobs": True, "top_logprobs": 20}
            result = function_pointer(*args, **kwargs)
            config.DefaultModel.api_parameters = previouse_model_params

            setattr(inner_func_pointer, "hosta_inspection", function_pointer.hosta_inspection)

            logprobes = get_enum_logprobes(function_pointer=function_pointer)
                        
            if not has_discriminative_value(logprobes, threshold=threshold):
                raise ValueError("The model did not return a discriminative value for the enum return type. Risk of hallucination.")

            return result
        
        inner_func_pointer = wrapper        

        return wrapper
    
    return configuration_decorator



from enum import Enum
class Color(Enum):
    RED = "red"
    GREEN = "green"
    BLUE = "blue"
    YELLOW = "yellow"
    BLACK = "black"
    WHITE = "white"
    ORANGE = "orange"
    ORANGE_LIGHT = "orange_light"
    PURPLE = "purple"
    PINK = "pink"
    BROWN = "brown"
    GRAY = "gray"
    CYAN = "cyan"
    MAGENTA = "magenta"
    LIME = "lime"
    TEAL = "teal"
    NAVY = "navy"
    MAROON = "maroon"
    OLIVE = "olive"
    NONE = "none"

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

        
from OpenHosta import print_last_prompt, closure, emulate


color_predictions = {
    "top_logprobs":[{"token":"bl", "logprob": -0.5},
               {"token":"blue", "logprob": -0.4},
               {"token":"red", "logprob": -4.0},
               {"token":"black", "logprob": -4.8},
               {"token":"white", "logprob": -4.0},
               {"token":"green", "logprob": -4.3}]}


color_predictions2 = {"top_logprobs":[{"token":"ue", "logprob": -.05},
               {"token":"lague", "logprob": -2.0},]}

possible_colors = [
    ("red", "RED", "Red", "10"),
    ("blue", "BLUE", "Blue", "12"),
    ("green", "GREEN", "Green", "13"),
    ("black", "BLACK", "Black", "14"),
    ("white", "WHITE", "White", "15"),
    ("orange", "ORANGE", "Orange", "16"),
    ("orange_light", "ORANGE_LIGHT", "Orange Light", "17"),
]


belief = posterior_probability(color_predictions, possible_colors)
belief = posterior_probability(color_predictions2, possible_colors, prior_prob_list=belief, previouse_string="bl")
has_discriminative_value(belief, threshold=0.8)
most_probable_value(belief)

    
color = closure("What is the color of this object ?", force_return_type=Color)

color("michael jackson")
print_last_prompt(color)

try:
    get_enum_logprobes(function_pointer=color)
except Exception as e:
    print(f"No logprob: {e}")
    
safe_color=safe(threshold=0.8)(color)

safe_color("michael jackson")
safe_color("orange sur un arbre")
print_last_prompt(safe_color)
get_enum_logprobes(function_pointer=safe_color)

#@safe(threshold=0.8)
def ColorOfThing(thing_description:str)->Color:
    """
    This function return the color of a thing described in the argument.
    """
    return emulate()


import contextvars


class ReproducibleSettings:
    def __init__(self, reproducible: bool = False, acceptable_log_uncertainty: float = -2, seed: int = 42):
        self.reproducible = reproducible
        self.acceptable_log_uncertainty = acceptable_log_uncertainty
        self.selected_path_certainty = 1.0
        self.seed = seed
        self.contextvar = None
        self.trace = []

def safe(acceptable_log_uncertainty: float = -2, seed: int = 42):

    settings = ReproducibleSettings(reproducible=True, acceptable_log_uncertainty=acceptable_log_uncertainty, seed=seed)
    reproducible_settings = contextvars.ContextVar("reproducible_settings", default=settings)
    settings.contextvar = reproducible_settings
    
    return settings

class UncertaintyError(Exception):
    pass

def check_colors():
    ret1 = ColorOfThing("The sky on a clear day.")
    ret2 = ColorOfThing("Color of Michael Jackson during his life.")
    ret3 = ColorOfThing("Color of the skin of Michael Jackson.")

    return ret1, ret2, ret3

# Gurantee that the log uncertainty of the total path is above the acceptable threshold
with safe(acceptable_log_uncertainty=-2):
    try:
        ret1, ret2, ret3 = check_colors()
        print(f"ret1: {ret1}, ret2: {ret2}, ret3: {ret3}")
    except UncertaintyError as e:
        print(f"Hallucination detected: {e}")    


class Year(Enum):
    YEAR_2100 = "2100"
    YEAR_2050 = "2050"
    YEAR_2101 = "2101"
    YEAR_2110 = "2110"
    YEAR_2200 = "2200"
    YEAR_3000 = "3000"

@safe(threshold=0.999999)
def BestDate(assertion:str)->Year:
    """
    This function return the best year for a given assertion.
    """
    return emulate()
BestDate("Quelle année serons nous dans 76 ans. nous sommes en 2026")

BestDate("An USA citizen will land on Mars.")

function_pointer=ColorOfThing
function_pointer=BestDate

ret = ColorOfThing("The sky on a clear day.")
ret = ColorOfThing("Color of Michael Jackson during his life.")

args = ["Color of the skin of Michael Jackson."]

class MainDocumentSubject(Enum):
    SCIENCE = "science"
    ART = "art"
    HISTORY = "history"
    TECHNOLOGY = "technology"
    LITERATURE = "literature"
    MUSIC = "music"
    SPORTS = "sports"
    POLITICS = "politics"
    ENTERTAINMENT = "entertainment"
    HEALTH = "health"
    BUSINESS = "business"
    EDUCATION = "education"
    TRAVEL = "travel"
    FOOD = "food"
    FASHION = "fashion"
    NATURE = "nature"
    PHILOSOPHY = "philosophy"
    RELIGION = "religion"
    PSYCHOLOGY = "psychology"
    ENVIRONMENT = "environment"
    NONE = "none"
    
document_subject = closure("What is the main subject of this document ?", force_return_type=MainDocumentSubject)
document_subject("The document is about the history of science and technology.")
get_enum_logprobes(function_pointer=document_subject)

document_subject("The first part is about the history of medical science. The second part is more specifically about the development of vaccines and their impact on public health")

