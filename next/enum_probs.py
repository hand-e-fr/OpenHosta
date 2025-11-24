### This file describe a partial implementation of logprobes for enum return types.
### It is not yet integrated in the main codebase, but it is a proof of concept
### It show how we plan to get small embeddings for enum values and use them to improve the accuracy of the model.
### This is important for vectorial memory

from OpenHosta import reload_dotenv, emulate
reload_dotenv()

# Works only with gpt-4o and gpt-4.1
#DefaultModel.model_name

# Does not work with reasoning models as the output probabilities are conditioned on the reasoning steps.

from enum import Enum

class Year(Enum):
    YEAR_2100 = "2100"
    YEAR_2050 = "2050"
    YEAR_2101 = "2101"
    YEAR_2110 = "2110"
    YEAR_2200 = "2200"
    YEAR_3000 = "3000"

from OpenHosta import max_uncertainty, print_last_probability_distribution, print_last_prompt

from OpenHosta import MetaPrompt, OneTurnConversationPipeline, config

pipe = OneTurnConversationPipeline(model_list=[config.DefaultModel])

pipe.emulate_meta_prompt = MetaPrompt("""\
    You will act as a simulator for functions that cannot be implemented in actual code.

    I'll provide you with function definitions described in Python syntax. 
    These functions will have no body and may even be impossible to implement in real code, 
    so do not attempt to generate the implementation.

    Instead, imagine a realistic or reasonable output that matches the function description.
    I'll ask questions by directly writing out function calls as one would call them in Python.
    Respond with an appropriate return value{% if use_json_mode %} formatted as valid JSON{% endif %}, without adding any extra comments or explanations.
    {% if return_none_allowed %}If the provided information isn't enough to determine a clear answer, respond simply with "None".{% endif %}
    If assumptions need to be made, ensure they stay realistic, align with the provided description.

    {% if allow_thinking %}If unable to determine a clear answer or if assumptions need to be made, 
    explain is in between <think></think> tags.{% endif %}

    Here's the function definition:

    ```python
    {{ function_return_as_python_type }}

    def {{ function_name }}({{ function_args }}) -> {{ function_return_type_name }}:
        """{{ function_doc }}"""

        ...
        ...behavior to be simulated...
        ...

        return ...appropriate return value...
    ```


    {% if use_json_mode %} As you return the result in JSON format, here's the schema of the JSON object you should return:
    {{ function_return_as_json_schema }} {% endif %}

    {% if examples_database %}Here are some examples of expected input and output:
    {{ examples_database }}{% endif %}

    {% if chain_of_thought %}To solve the request, you have to follow theses intermediate steps. Give only the final result, don't give the result of theses intermediate steps:
    {{ chain_of_thought }}{% endif %}
    """)

pipe.user_call_meta_prompt = MetaPrompt("""\
    {% if variables_initialization %}# Values of parameters to be used
    {{ variables_initialization }}{% endif %}
    {{ function_name }}({{ function_call_arguments }})
    """)

@max_uncertainty(threshold=0.2)
def BestDate(assertion:str)->Year:
    """
    This function return the best year for a given assertion.
    """
    return emulate(pipeline=pipe, force_llm_args={"reasoning_effort": "low"})

BestDate("Quelle année serons nous dans 76 ans. nous sommes en 2026")

BestDate("Quelle année serons nous dans 76 ans. nous sommes en 2025")

BestDate("Quelle année serons il y a 5 ans. nous sommes en 2026")

BestDate(None)

# We see that the model answer with high confidence even when he has high uncertainty in its reasoning.
# TODO: We need to find a way to make the model express its uncertainty better.
# - Estimate uncertainty on the reasoning steps using P(Reasoning|Input=input) versus P(Reasoning|Input=None)

# However it works with non reasoning models like qwen3 on vllm 0.11
print_last_prompt(BestDate)
print_last_probability_distribution(BestDate)

BestDate("An USA citizen will land on Mars.")
print_last_probability_distribution(BestDate)

