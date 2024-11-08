from __future__ import annotations

from typing import List


class MetaPrompt:

    def __init__(self, shards: List[str]):
        for shard in shards:
            if not isinstance(shard, str):
                raise ValueError(
                    "[MetaPrompt.__init__] Shards must be strings.")
            try:
                setattr(self, "_{}".format(shard.upper()), "")
            except:
                raise AttributeError(
                    f"[MetaPrompt.__init__] Failed to initialize {shard} attributs")

    def __repr__(self):
        ctx = {}
        for key, value in self.__dict__.items():
            if key.startswith("CTX_"):
                ctx[key] = value
        return "\n".join(ctx.values())


EMULATE_PROMPT = MetaPrompt([
    "CTX_MAIN",
    "CTX_SEP1"
    "CTX_EXAMPLE",
    "CTX_SEP2"
    "PRE_DEF",
    "PRE_TYPE",
    "PRE_SCHEMA",
    "PRE_LOCALS",
    "PRE_SELF",
    "PRE_EXAMPLE",
    "PRE_COT",
    "USER_SEP"
])
EMULATE_PROMPT.CTX_MAIN = "## Context\n\nYou will act as an emulator of impossible-to-code functions. I will provide you with the description of the function using Python's way of declaring functions, but I won't provide the function body as I don't know how to code it. It might even be impossible to code. Therefore, you should not try to write the body. Instead, directly imagine the function output.\n\nIn the conversation, I will directly write the function call as if it was called in Python. You should directly answer with whatever you believe would be a good return for the function.\n\nIf the output is documented as a Python structure, you should translate it to JSON.\nYou should encode the return in valid JSON format, without comments, using the following format:\n```\n{\"return\":\"...\"}\n```\n\nThe output must be of the same type as that specified in the function call. If you don't have enough information or don't know how to answer, the output should be “None”. \n\nAny assumptions made should be reasonable based on the provided function description and should take into account the error handling of the function."
EMULATE_PROMPT.CTX_SEP1 = "\n---\n"
EMULATE_PROMPT.CTX_EXAMPLE = "## Examples\n\n**Example function definition:**\n```python\ndef example_function(a: int, b: dict) -> int:\n\t\"\"\"\n\tThis is an example function.\n\tIt adds two numbers.\n\t\"\"\"\n\treturn emulate()\n```\n\n**Example emulated function call:**\n```python\nresult = example_function(3, {\"value\": 7})\n```\n\n**Expected JSON output:**\n{\"return\": 10}"
EMULATE_PROMPT.CTX_SEP2 = "\n---\n\n## Function infos\n"
EMULATE_PROMPT.PRE_DEF = "Here's the function definition:"
EMULATE_PROMPT.PRE_TYPE = "Here's the type annotation of the function:"
EMULATE_PROMPT.PRE_SCHEMA = "If it isn't a native type, here's a schema describing the type annotation:"
EMULATE_PROMPT.PRE_LOCALS = "Here's the function's locals variables which you can use as additional information to give your answer:"
EMULATE_PROMPT.PRE_SELF = "Here's the method's class attributs variables which you can use as additional information to give your answer:"
EMULATE_PROMPT.PRE_EXAMPLE = "Here are some examples of expected input and output:"
EMULATE_PROMPT.PRE_COT = "To solve the request, you have to follow theses intermediate steps. Give only the final result, don't give the result of theses intermediate steps:"
EMULATE_PROMPT.USER_SEP = "\n---\n"

THOUGHT_PROMPT = MetaPrompt([
    "CTX_MAIN",
    "CXT_SEP",
    "CTX_EXAMPLE",
    "USER_SEP"
])
THOUGHT_PROMPT.CTX_PROMPT = "You will act as an emulator of impossible-to-code functions. I will provide you with the description of the function using Python's way of declaring functions, but I won't provide the function body as I don't know how to code it. It might even be impossible to code. Therefore, you should not try to write the body. Instead, directly imagine the function output.\n\nIn the conversation, I will directly write the function behavior as a sentence, and the argument passed to the function.\n\nYour objective is to find the Python data type to be returned by the function. Take into account the function's behavior, the wording and intent of the sentence, and the arguments given. You must give your answer without any comment and in the following JSON schema:\n```\n{\"type\": \"\"}\n```\n\nTo fill in the type key, you need to follow Python syntax, such as \"int\" or \"str\", depending on your answer."
THOUGHT_PROMPT.CTX_SEP = "\n---\n"
THOUGHT_PROMPT.CTX_EXAMPLE = "Here are a few examples:\n\nFunction behavior: \"Is a positive number\"\nArgument: 2\nExpected response: {\"type\": \"bool\"}\n\nFunction behavior: \"Multiply a number by 2\"\nArgument: 10\nExpected response: {\"type\": \"int\"}\n\nFunction behavior: \"Reverse a string\"\nArgument: \"Hello World!\"\nExpected response: {\"type\": \"str\"}\n\nFunction behavior: \"Sorts a list in ascending order\"\nArgument: (10, 5, 7, 12, 3)\nExpected response: {\"type\": \"list\"}"
THOUGHT_PROMPT.USER_SEP = "\n---\n"
