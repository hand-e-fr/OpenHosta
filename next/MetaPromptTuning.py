from OpenHosta import  MetaPrompt

MP_SYSTEM = MetaPrompt('''\
You will act as a simulator for functions that cannot be implemented in actual code.

I'll provide you with function definitions described in Python syntax. 
These functions will have no body and may even be impossible to implement in real code, 
so do not attempt to generate the implementation.

Instead, imagine a realistic or reasonable output that matches the function description.
I'll ask questions by directly writing out function calls as one would call them in Python.
Respond with an appropriate return value{% if use_json_mode %} formatted as valid JSON{% endif %}, without adding any extra comments or explanations.
If the provided information isn't enough to determine a clear answer, respond simply with "None".
If assumptions need to be made, ensure they stay realistic, align with the provided description.

{% if function_return_as_json_schema %}
Here is the schema of the return value you should produce:
{{ function_return_as_json_schema }}
{% endif %}

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
''')

MP_USER = MetaPrompt('''\
{% if variables_initialization %}# Values of parameters to be used
{{ variables_initialization }}{% endif %}
{{ function_name }}({{ function_call_arguments }}), [])]
''')

from OpenHosta import emulate, config
from OpenHosta.pipelines.simple_pipeline import OneTurnConversationPipeline
from pydantic import BaseModel, Field

class MyClassificationProbs(BaseModel):
    Political: str = Field(..., description="Contenu lié aux politiques, réglementations ou directives.")
    Technical: str = Field(..., description="Contenu lié aux aspects techniques, technologies ou méthodologies.")
    Legal: str = Field(..., description="Contenu lié aux aspects juridiques, contrats ou conformité.")
    Financial: str = Field(..., description="Contenu lié aux aspects financiers, budgets ou coûts.")
                       
def classify_snippet(markdown_snippet: str) -> MyClassificationProbs:
    """
    Analyse un snippet de texte au format Markdown et renvoie
    sa catégorie sous forme d'un Enum.
    """
    return emulate(
        pipeline=OneTurnConversationPipeline(
            model_list=[config.DefaultModel],
            emulate_meta_prompt=MP_SYSTEM,
            user_call_meta_prompt=MP_USER)
        )

c = classify_snippet("Le budget alloué pour le projet est de 5000 euros.")

# How to debug meta prompt:

data = classify_snippet.hosta_inspection["data_for_metaprompt"]

print(MP_SYSTEM.render(data))

MP1 = classify_snippet.hosta_inspection["meta_prompts"][0][1]
MP2 = classify_snippet.hosta_inspection["meta_prompts"][1][1]

print(MP1.render(data))
print(MP2.render(data))
