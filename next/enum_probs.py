### This file describe a partial implementation of logprobes for enum return types.
### It is not yet integrated in the main codebase, but it is a proof of concept
### It show how we plan to get small embeddings for enum values and use them to improve the accuracy of the model.
### This is important for vectorial memory

from OpenHosta import closure, DefaultModel, reload_dotenv
reload_dotenv()
# Works only with gpt-4o and gpt-4.1
DefaultModel.api_parameters |= {"logprobs": True, "top_logprobs": 20}
DefaultModel.model_name
        
from OpenHosta import print_last_prompt


# Not yet supported by ollama, supported by gpt-4o and gpt-4.1
def get_enum_logprobes(*,function_pointer=None, inspection=None):
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
    
    logp_list = response_dict["choices"][0]["logprobs"]["content"]
    if len(logp_list) <= 0:
        print(f"Warning: not enough logprobs ({len(logp_list)})")
        return {}
    if logp_list[0]['token'] in ["'", '"']:
        logp_list = logp_list[1]
    else:
        logp_list = logp_list[0]
    
    assert issubclass(return_type, Enum), "Return type is not an Enum"
    
    # TODO: make it recursive to handle multiple tokens per enum value
    logprobes = {}
    token_list = [l["token"] for l in logp_list['top_logprobs']]
    for v in list(return_type):
        logprobes[v] = min([x['logprob'] for x in logp_list['top_logprobs']])*1.1
        max_match_length = 0
        
        # Find the longest token that matches the start of the enum value
        for pos, token in enumerate(token_list):
            if (v.value.startswith(token) or v.name.startswith(token)) and len(token) > max_match_length:
                # print(f"Found match for {v} with token '{token}' (len {len(token)})")
                max_match_length = len(token)
                logprobes[v] = logp_list['top_logprobs'][pos]['logprob']
        # print(f"Final logprob for {v} is {logprobes[v]}")
    return logprobes


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
    
color = closure("What is the color of this object ?", force_return_type=Color)

color("michael jackson")
get_enum_logprobes(function_pointer=color)
print_last_prompt(color)

response_dict = color.hosta_inspection["logs"]["llm_api_response"]
response_dict["choices"][0]["logprobs"]["content"][0]
response_dict["choices"][0]["logprobs"]["content"][1]
response_dict["choices"][0]["logprobs"]["content"][2]

for i,v in enumerate(response_dict["choices"][0]["logprobs"]["content"]):
    print(f"Option {i}:")
    t=[l["token"] for l in v['top_logprobs']]
    v=[l["logprob"] for l in v['top_logprobs']]
    for c in Color:
        if c.value in t:
            print(f"  {c.value}: {v[t.index(c.value)]}")
        else:
            print(f"  {c.value}: Not found")



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