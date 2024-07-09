import inspect
import requests
import json
import uuid
import time
import hashlib
import sys
import os

emulator_pre_prompt: str = (
    """
You will act as an emulator of impossible-to-code functions. I will provide you with the description of the function using Python's way of declaring functions, but I won't provide the function body as I don't know how to code it. It might even be impossible to code. Therefore, you should not try to write the body. Instead, directly imagine the function output.

In the conversation, I will directly write the function call as if it was called in Python. You should directly answer with whatever you believe would be a good return for the function.

When you produce an answer, you should estimate the confidence level:

    "low": You did your best, but with the provided description and your knowledge, you are not confident about the answer.
    "medium-instance": You did your best, and with the provided description and your knowledge, you are pretty sure this answer is valid but not the only valid answer.
    "medium-unique": You did your best, and with the provided description and your knowledge, you are pretty sure this answer is the unique and valid answer.
    "high-instance": You did your best, and you are sure that your provided answer is a valid answer. It is a well-known function or you can easily implement a Python code that yields elements from the list of valid answers. This answer is randomly chosen from the list of valid answers.
    "high-unique": You did your best, and you are sure that your provided answer is the unique valid answer. It is a well-known function or you can easily implement a Python code that solves the question and calculates this answer given this input.

If the output is documented as a Python structure, you should translate it to JSON.
You should encode the return in valid JSON format, without comments, using the following format:
{"return":..., "confidence":...}

The output must be of the same type as that specified in the function call.

Any assumptions made should be reasonable based on the provided function description and should take into account the error handling of the function.

Consistency in the confidence levels is important to ensure accurate responses.
This is the function documentation:

Example function call:

def example_function(a: int, b: dict) -> int:
    """
    """
    This is an example function.
    It adds two numbers.
    """
    """
    pass

Example imagined function output:

result = example_function(3, {"value": 7})

Expected JSON output:

{"return": 10, "confidence": "medium-unique"}

This is the function documentation:
"""
)

enhancer_pre_prompt: str = """
I want you to become my Expert Prompt Creator for developer.
Your goal is to help me craft the best possible prompt for my programming needs.
The prompt you provide should be written from the perspective of me making the request to GPT-4o.
Consider in your prompt creation that this prompt will be entered into an interface for GPT-4o.
Apart from diagrams, you must write in text, without following any syntax.
The process is as follows:

You will generate the following sections:

"
-> enhanced:
{provide the best possible prompt according to my request. The prompt is used to describe
a function to be performed in Python as precisely as possible. You can add error handling,
as the function needs it to work properly. But don't code the function in the prompt.
The prompt should not tell to create the function, but describe how it works.}

-> critique:
{provide a concise paragraph on how to improve the prompt. Be very critical in your response.
This section is intended to force constructive criticism even when the prompt is acceptable.
Any assumptions and or issues should be included. Don't forget that you speak to a developer}

-> suggested:
{rewrite the prompt with the suggested improvements you made in the critique category.
The aim is to make a proposal, an example. Make logical assumptions to solve
the problem based on the context and all the information you have. You have to respond
to the problems you formulated in the previous category. But don't code the function
in the prompt.}

-> mermaid:
{Make a mermaid diagram explaining the function described by the prompt. You need to break
the reasoning into several steps for ease of understanding and clarity. You must
make it logical and easy to look at. You have to write it in mermaid syntax.
You must not use the markdown syntax}
"
"""


class emulator:
    __version__ = 1.0

    __last_return__ = None
    __last_content__ = None
    __last_data__ = {"return": None, "confidence": "low"}

    _default_api_key = "sk-proj-T7o4z8S4q9fnBNTdSq4iT3BlbkFJ82uVDLRaIAkx1sjwyE5C"
    _default_ai_model: str = "gpt-4o"
    _default_creativity: float = 0.5
    _default_diversity: float = 0.5

    __last_enh_return__: str = None
    __last_enh__: dict = {
        "enhanced": None,
        "critique": None,
        "suggested": None,
        "mermaid": None,
    }

    def __init__(
        self,
        model: str = None,
        creativity: float = None,
        diversity: float = None,
        api_key: str = None,
    ) -> None:
        self.api_key = emulator._default_api_key if api_key is None else api_key
        self.model = emulator._default_ai_model if model is None else model
        self.temperature = (
            emulator._default_creativity if creativity is None else creativity
        )
        self.top_p = emulator._default_diversity if diversity is None else diversity

    def gpt4o(self, function_doc, function_call):
        global emulator_pre_prompt
        api_key = self.api_key
        l_body = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": [
                        {
                            "type": "text",
                            "text": emulator_pre_prompt
                            + "---\n"
                            + function_doc
                            + "\n---",
                        }
                    ],
                },
                {"role": "user", "content": [{"type": "text", "text": function_call}]},
            ],
            "response_format": {"type": "json_object"},
        }

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        }

        response = requests.post(
            "https://api.openai.com/v1/chat/completions", json=l_body, headers=headers
        )

        self.__last_return__ = {"code": response.status_code, "text": response.text}

        self.__resp__ = response

        if response.status_code == 200:
            data = response.json()
            json_string = data["choices"][0]["message"]["content"]
            self.__last_content__ = json_string
            try:
                l_ret_data = json.loads(json_string)
                self.__jsonN__ = l_ret_data

            except json.JSONDecodeError as e:
                print(f"JSONDecodeError: {e}")
                l_cleand = "\n".join(json_string.split("\n")[1:-1])
                l_ret_data = json.loads(l_cleand)

            self.__last_data__ = l_ret_data

            l_ret = l_ret_data["return"]
        else:
            print(f"Error {response.status_code}: {response.text}")
            self.__last_data__ = {"return": None, "confidence": "low"}
            l_ret = None

        return l_ret

    def emulate(self, func):
        def wrapper(*args, **kwargs):
            sig = inspect.signature(func)
            bound_args = sig.bind(*args, **kwargs)
            bound_args.apply_defaults()

            func_name = func.__name__
            func_params = ", ".join(
                [
                    (
                        f"{param_name}: {param.annotation.__name__}"
                        if param.annotation != inspect.Parameter.empty
                        else param_name
                    )
                    for param_name, param in sig.parameters.items()
                ]
            )
            func_return = (
                f" -> {sig.return_annotation.__name__}"
                if sig.return_annotation != inspect.Signature.empty
                else ""
            )
            function_def = f"def {func_name}({func_params}):{func_return}\n    '''\n    {func.__doc__}\n    '''"

            func_call_args = ", ".join(
                [str(value) for value in bound_args.arguments.values()]
            )
            function_call = f"{func_name}({func_call_args})"

            try:
                result = self.gpt4o(function_def, function_call)
            except Exception as e:
                print(Exception)
                print(f"[EMU_ERROR] {e}", function_call)
                result = None
            return result

        return wrapper

    def oracle(self, func):

        def get_output(func, *args, **kwargs):
            data_function, tag_output = func(*args, **kwargs)
            if tag_output != 0 and tag_output != 1 and tag_output != True and tag_output != False:
                raise ValueError(
                    f"Tag output should be 0 or 1 or True or False, but got {tag_output}")
                
            return data_function, tag_output

        def wrapper_function(*args, **kwargs):
            sig = inspect.signature(func)

            bound_args = sig.bind(*args, **kwargs)
            bound_args.apply_defaults()

            func_name = func.__name__

            func_params = ", ".join(
                [
                    (
                        f"{param_name}: {param.annotation.__name__}"
                        if param.annotation != inspect.Parameter.empty
                        else param_name
                    )
                    for param_name, param in sig.parameters.items()
                ]
            )

            func_return = (
                f" -> {sig.return_annotation.__name__}"
                if sig.return_annotation != inspect.Signature.empty
                else ""
            )

            function_def = f"def {func_name}({func_params}):{func_return}\n    '''\n    {func.__doc__}\n    '''"

            func_call_args = ", ".join(
                [str(value) for value in bound_args.arguments.values()]
            )
            function_call = f"{func_name}({func_call_args})"

            return function_call, function_def

        def create_json(*args, **kwargs):

            function_call, function_def = wrapper_function(*args, **kwargs)
            data_function, tag_output = get_output(func, *args, **kwargs)

            data = {
                "Version": self.__version__,
                "Model used": self.model,
                "Id session": str(uuid.uuid4()),
                "Timestamp": int(time.time()),
                "func_call": function_call,
                "func_hash": hashlib.md5(function_def.encode()).hexdigest(),
                "Tag output": tag_output,
                "Data": data_function,
            }
            json_object = json.dumps(data, indent=5)
            return json_object

        return create_json

    def ai_call_enh(self, sys_prompt: str, func_prot: str, func_doc: str):
        api_key = self.api_key
        url = "https://api.openai.com/v1/chat/completions"

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        }

        data = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": [{"type": "text", "text": sys_prompt}]},
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": "\nHere's my python function's prototype:\n---\n"
                            + func_prot
                            + "\n---\n",
                        }
                    ],
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": "\nHere's my python function's prompt:\n---\n"
                            + func_doc
                            + "\n---\n",
                        }
                    ],
                },
            ],
            "temperature": self.temperature,
            "top_p": self.top_p,
        }

        response = requests.post(url, headers=headers, data=json.dumps(data))

        if response.status_code == 200:
            response_data = response.json()
            return response_data["choices"][0]["message"]["content"]
        else:
            sys.stderr.write(
                "[CALL_ERROR] The request was unsuccessful or one of the parameters is invalid"
            )
            sys.stderr.write(f"Status: {response.status_code}")
            return None

    def parse_data(self, response: str):
        current_section = None
        current_text = []

        for line in response.splitlines():
            if line.startswith("->"):
                if current_section:
                    self.__last_enh__[current_section] = "\n".join(current_text).strip()
                current_section = line[3:].strip(":")
                current_text = []
            else:
                current_text.append(line)
        if current_section:
            self.__last_enh__[current_section] = "\n".join(current_text).strip()

    def create_mermaid_file(self, mmd_script: str, name: str, dir: str) -> None:
        try:
            with open(f"{dir}/{name}_diagram.mmd", "w") as file:
                try:
                    file.write(mmd_script)
                except Exception as e:
                    sys.stderr.write(
                        f"[MMD_ERROR]: {e}\nAn error occured when writing .mmd file"
                    )
        except IOError as e:
            sys.stderr.write(f"[MMD_ERROR] {e}")
        finally:
            file.close()

    def create_help_file(
        self, name: str, enhanced: str, critique: str, suggested: str, dir: str
    ) -> None:
        try:
            with open(f"{dir}/{name}_enhanced.md", "w") as file:
                try:
                    file.write("# ENHANCER\n")
                    file.write(f"- **Enhanced prompt:**\n{enhanced}\n")
                    file.write(f"- **How to improve your prompt:**\n{critique}\n")
                    file.write(f"- **Improvemed prompt suggestion:**\n{suggested}\n")
                except Exception as e:
                    sys.stderr.write(
                        f"[HLP_ERROR] {e}: \nAn error occured when writing .mmd file"
                    )
        except IOError as e:
            sys.stderr.write(f"[HELP_ERROR] {e}")
        finally:
            file.close()

    def build_output(self, func: object) -> int:
        path = ""

        try:
            if not func.__name__ and not type(func.__name__) is str:
                raise ValueError("ValueError -> function name")
            if (
                not self.__last_enh__["enhanced"]
                and not type(self.__last_enh__["enhanced"]) is str
            ):
                raise ValueError("ValueError -> enhanced output")
            if (
                not self.__last_enh__["critique"]
                and not type(self.__last_enh__["critique"]) is str
            ):
                raise ValueError("ValueError -> critique output")
            if (
                not self.__last_enh__["suggested"]
                and not type(self.__last_enh__["suggested"]) is str
            ):
                raise ValueError("ValueError -> seggested output")
            if (
                not self.__last_enh__["mermaid"]
                and not type(self.__last_enh__["mermaid"]) is str
            ):
                raise ValueError("ValueError -> mermaid output")
        except ValueError as e:
            sys.stderr.write(f"[BUILD_ERROR] {e}")
            return -1
        finally:
            dir = ".openhosta"
            path = f"{os.getcwd()}/{dir}"
            if not os.path.exists(dir):
                try:
                    os.mkdir(path)
                except OSError as e:
                    sys.stderr.write(f"[BUILD_ERROR] {e}")

        print(f"PATH: {path}")
        self.create_mermaid_file(self.__last_enh__["mermaid"], func.__name__, path)
        self.create_help_file(
            func.__name__,
            self.__last_enh__["enhanced"],
            self.__last_enh__["critique"],
            self.__last_enh__["suggested"],
            path,
        )
        return 0

    def enhance(self, func):
        def wrapper(*args, **kwargs):
            global enhancer_pre_prompt
            func_name, func_doc = func.__name__, func.__doc__

            sig = inspect.signature(func)
            func_prot = f"def {func_name} {sig}:\n"

            self.__last_enh_return__ = self.ai_call_enh(
                enhancer_pre_prompt, func_prot, func_doc
            )
            self.parse_data(self.__last_enh_return__)
            func.__doc__ = self.__last_enh__["enhanced"]
            if self.build_output(func) == -1:
                return None
            return func

        return wrapper
