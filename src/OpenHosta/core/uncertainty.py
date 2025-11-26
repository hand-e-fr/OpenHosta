import os
import math
import uuid
import contextvars
from typing import Dict, Tuple  # added Tuple

from ..core.errors import ModelMissingLogprobsError
from ..core.errors import UncertaintyError

from enum import Enum

SAFE_CONTEXT_VAR_NAME = "reproducible_settings"
reproducible_settings_ctxvar = contextvars.ContextVar(SAFE_CONTEXT_VAR_NAME, default={})

def _trim_logp_list(logp_list):
    """
    Remove special control tokens from a VLLM logprob list.
    Returns the trimmed list.
    """
    # Helper to find first occurrence index of a token, if present
    def _first_index(token):
        tokens = [t['token'] for t in logp_list]
        return min((i for i, t in enumerate(tokens) if t == token), default=None)

    # Jump to the first token after <|message|>
    if "<|message|>" in [t['token'] for t in logp_list]:
        last_message_index = max(i for i, t in enumerate(logp_list) if t['token'] == "<|message|>")
        logp_list = logp_list[last_message_index + 1:]

    # Cut off at the first occurrence of each control token, if present
    for ctrl_token in ("<|return|>", "<|im_end|>", "<｜end▁of▁sentence｜>"):
        idx = _first_index(ctrl_token)
        if idx is not None:
            logp_list = logp_list[:idx]

    return logp_list

def get_certainty(function_pointer, vocabulary_size=200_000) -> Tuple[float, int]:
    """
    Calculates an uncertainty score based on the branching factor of log probabilities
    in the LLM response.

    Returns:
        (selected_proportion, above_random_branches)
        where `selected_proportion` is the product of per‑token probabilities
        and `above_random_branches` is the total number of likely alternatives
        across all tokens.
    """
    # 1. Extract the nested data source safely
    try:
        response_logprobs = function_pointer.hosta_inspection["logs"]["llm_api_response"]["choices"][0]["logprobs"]["content"]
    except (KeyError, IndexError, AttributeError):
        return 0.0, 0

    return get_naive_certainty(response_logprobs, vocabulary_size=vocabulary_size)

def get_naive_certainty(response_logprobs, vocabulary_size=200_000) -> Tuple[float, int]:
    
    selected_proportion = 1.0
    above_random_branches = 1

    # 2. Iterate through tokens to calculate branching options
    for i, token_data in enumerate(response_logprobs):
        token_text = token_data.get("token", "")

        # Skip the first token if it starts with a quote
        if i == 0 and (token_text.startswith("'") or token_text.startswith('"')):
            continue

        top_logprobs = token_data.get("top_logprobs", [])
        likely_alternatives = [
            p for p in top_logprobs
            if p.get('logprob', -float('inf')) > math.log(1 / vocabulary_size)
        ]

        above_random_branches *= max(len(likely_alternatives), 1)

        valid_mass = sum(math.exp(t["logprob"]) for t in likely_alternatives if token_text.startswith(t['token']))
        total_mass = sum(math.exp(t["logprob"]) for t in likely_alternatives)

        step_probability = 1.0 if total_mass == 0 else valid_mass / total_mass
        selected_proportion *= step_probability

    return selected_proportion, above_random_branches   


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
def get_enum_logprobes(*, function_pointer=None, inspection=None) -> dict:
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

    if "logprobs" not in response_dict["choices"][0] or not response_dict["choices"][0]["logprobs"]:
        raise ModelMissingLogprobsError("Model response does not contain logprobs. Make sure the model supports logprobs.")
    
    logp_list = response_dict["choices"][0]["logprobs"]["content"]
    if len(logp_list) <= 0:
        print(f"Warning: not enough logprobs ({len(logp_list)})")
        return {}

    # Use the new helper to trim control tokens
    logp_list = _trim_logp_list(logp_list)

    if "rational" in inspection["logs"]:
        rational = inspection["logs"]["rational"]
        answer_part = []
        rational_part = []
        for token_data in logp_list:
            if rational.startswith(token_data['token']):
                rational = rational[len(token_data['token']):]
                rational_part.append(token_data)
            else:
                answer_part.append(token_data)
                
        rational_certainty, branch_count = get_naive_certainty(rational_part)
        print(f"Rational part uncertainty: {1 - rational_certainty:0.6f} over {branch_count} branches")
        
        logp_list = answer_part
    else:
        rational_uncertainty = 1
        
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
        logprobes = posterior_probability(prediction, possible_outcomes, prior_prob_list=prior_prob_list, previouse_string=previouse_string)
        #print(f"Logprobes after token '{prediction['token']}': {logprobes}")
        prior_prob_list = {k: math.exp(v) for k,v in logprobes.items()}
        previouse_string += prediction['token']
    
    if all([previouse_string not in v for v in possible_outcomes]):
        raise UncertaintyError(f"The generated string '{previouse_string}' does not match any of the possible enum outcomes. Risk of hallucination.")
        
    return logprobes

class ReproducibleSettings:
    def __init__(self, acceptable_cumulated_uncertainty: float = 0.05, seed: int = 42):
        self.acceptable_cumulated_uncertainty = acceptable_cumulated_uncertainty
        self.cumulated_uncertainty = 0.0
        self.seed = seed
        self.uuid = uuid.uuid4()
        self.trace = []
        
    def __repr__(self):
        return f"""ReproducibleSettings(
            acceptable_cumulated_uncertainty={self.acceptable_cumulated_uncertainty},
            cumulated_uncertainty={self.cumulated_uncertainty}, 
            seed={self.seed}, 
            uuid={self.uuid})"""
        
class ReproducibleContextManager:
    def __init__(self, settings: ReproducibleSettings):
        self.settings = settings

    def __enter__(self):
        reproducible_settings:dict = reproducible_settings_ctxvar.get()
        reproducible_settings[self.settings.uuid] = self.settings
        
        return self.settings

    def __exit__(self, exc_type, exc_value, traceback):
        reproducible_settings:dict = reproducible_settings_ctxvar.get()
        if self.settings.uuid in reproducible_settings:
            del reproducible_settings[self.settings.uuid]

def safe(acceptable_cumulated_uncertainty: float = 0.05, seed: int = None):

    if seed is None and "OPENHOSTA_DEFAULT_MODEL_SEED" in os.environ:
        try:
            seed = int(os.environ["OPENHOSTA_DEFAULT_MODEL_SEED"])
        except ValueError:
            print(f"Warning: OPENHOSTA_DEFAULT_MODEL_SEED is not a valid integer: {os.environ['OPENHOSTA_DEFAULT_MODEL_SEED']}. Using default seed.")

    if seed is None:
        print("Warning: No seed provided for reproducible context. This will lead to non-reproducible results. This is not very safe.")

    settings = ReproducibleSettings(
        acceptable_cumulated_uncertainty=acceptable_cumulated_uncertainty,
        seed=seed
    )
        
    return ReproducibleContextManager(settings)


def last_uncertainty(function_pointer) -> float:
    if hasattr(function_pointer, "hosta_inspection") and \
        "uncertainty" in function_pointer.hosta_inspection["logs"]:
        return function_pointer.hosta_inspection["logs"]["uncertainty"]
    else:
        return 0
