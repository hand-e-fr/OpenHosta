"""
Prompt is text.
Meta-prompt is text with variables and control flow.
Meta-prompt is jinja2. Period.

Just make it easier to inspect and tune.
"""

from textwrap import dedent
from jinja2 import Template

class MetaPrompt:
    """
    Jinja2 compatible template for prompts.

    Prompt is text. MetaPrompt is jinja2 that can be printed as text.

    To create a meta-prompt:
    `my_meta_prompt = MetaPrompt('''Answer the question : {{ user_question }}''')`

    To see the source meta prompt:
    `print(my_meta_prompt)`

    To see the prompt:
    `print(my_meta_prompt.render({"user_question": "what is the meaning of life?"}))`

    The prompt is dedent by default so that you can write:
    ```
    my_meta_prompt = MetaPrompt('''\\
        You are a helpful assistant.

        Answer the question : 
        {{ user_question }}''')
    ```

    Have a look at jinja2 documentation for other possibilities.
    """

    def __init__(self, source, *args, **kargs):
        self._source = dedent(source)
        self._template_args = args
        self._template_kargs = kargs
        self.template = Template(self._source, *args, **kargs)

    def copy(self):
        """
        Create a copy of the meta-prompt.

        Remember that in python everything is a reference, so if you modify the source of a MetaPrompt, all references to it will see the change.
        Most likely you want to copy it first.

        Returns:
            MetaPrompt: A copy of the meta-prompt.
        """
        return MetaPrompt(self._source, *self._template_args, **self._template_kargs)

    @property
    def source(self):
        """
        The source of the meta-prompt.
        """
        return self._source

    @source.setter
    def source(self, value):
        self._source = dedent(value)
        self.template = Template(self._source, *self._template_args, **self._template_kargs)

    def render(self, *args, **kargs):
        """
        Render the template with the given arguments.

        Removes empty lines associated to {% if ...  %} that append to be false. 
        """
        raw_rendering = self.template.render(*args, **kargs)
        lines = raw_rendering.split("\n")
        cleaned_lines = [lines[0]]
        for l in lines[1:]:
            if len(l.strip()) == 0 and len(cleaned_lines[-1].strip()) == 0:
                pass
            else:
                cleaned_lines.append(l)
        return "\n".join(cleaned_lines)

    def __str__(self):
        return self.source

    def __repr__(self):
        return dedent(f"""\
            {type(self)}
            MetaPrompt source:
            --------------------------------
            """)+self.source

EMULATE_META_PROMPT=MetaPrompt(
    """\
    You will act as a simulator for functions that cannot be implemented in actual code.

    I'll provide you with function definitions described in Python syntax. 
    These functions will have no body and may even be impossible to implement in real code, 
    so do not attempt to generate the implementation.

    Instead, imagine a realistic or reasonable output that matches the function description.
    I'll ask questions by directly writing out function calls as one would call them in Python.
    Respond with an appropriate return value{% if use_json_mode %} formatted as valid JSON{% endif %}, without adding any extra comments or explanations.
    If the provided information isn't enough to determine a clear answer, respond simply with "None".
    If assumptions need to be made, ensure they stay realistic, align with the provided description.

    {% if allow_thinking %}If unable to determine a clear answer or if assumptions need to be made, 
    explain is in between <think></think> tags.{% endif %}

    Here's the function definition:

    ```python
    {{ function_return_as_python_type }}
    
    def {{ function_name }}({{ function_args }}) -> {{ function_return_type_name }}:
        \"\"\"{{ function_doc }}\"\"\"
        
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

    {% if allow_thinking %}
    If you need to think first, place your thought within <think></think> before answering like this:
    <think>
    The user might want ...
    Wait, I have to...
    </think>{% endif %}""")

USER_CALL_META_PROMPT = MetaPrompt(
    """\
    {% if variables_initialization %}# Values of parameters to be used
    {{ variables_initialization }}{% endif %}
    {{ function_name }}({{ function_call_arguments }})""")
