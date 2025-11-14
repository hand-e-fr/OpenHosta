
import math
import contextvars

from typing import Dict
from enum import Enum

from .errors import ModelMissingLogprobsError
from .errors import UncertaintyError

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


def normalized_probs(logprob_distribution:dict)->dict:
    max_logprob = max(logprob_distribution.values())
    exp_values = {k: math.exp(v - max_logprob) for k,v in logprob_distribution.items()}
    total = sum(exp_values.values())
    normalized_probs = {k: v/total for k,v in exp_values.items()}
    return normalized_probs

# Test is the probabilit distribution has a value that is discriminative enough
def has_discriminative_value(normalized_probs:dict, threshold:float=0.7)->bool:
    for _,v in normalized_probs.items():
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

    assert issubclass(return_type, Enum), f"Return type is not an Enum. Type: {return_type} is not allowed when checking uncertainty."

    if "logprobs" not in response_dict["choices"][0]:
        raise ModelMissingLogprobsError("Model response does not contain logprobs. Make sure the model supports logprobs.")
    
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

def max_uncertainty(threshold:float=0.8):

    def configuration_decorator(function_pointer):
        
        inner_func_pointer = None
        
        def wrapper(*args, **kwargs):
            
            setattr(function_pointer, "force_llm_args", {"logprobs": True, "top_logprobs": 20})
            
            # Call the function
            try:
                result = function_pointer(*args, **kwargs)
            except Exception as e:
                print("Error during function execution:", e)
                
            setattr(inner_func_pointer, "hosta_inspection", function_pointer.hosta_inspection)

            logprobes = get_enum_logprobes(function_pointer=function_pointer)
            function_pointer.hosta_inspection["logs"]["enum_logprobes"] = logprobes
                   
            normalized_probability = normalized_probs(logprobes)  
            function_pointer.hosta_inspection["logs"]["enum_normalized_probs"] = normalized_probability
               
            if not has_discriminative_value(normalized_probability, threshold=threshold):
                raise UncertaintyError(f"The model did not return a discriminative value for the enum return type. Risk of hallucination. Selected value probabilities: {normalized_probability}, required threshold: {threshold}")

            return result
        
        inner_func_pointer = wrapper        

        return wrapper
    
    return configuration_decorator

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