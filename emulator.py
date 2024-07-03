import inspect
import requests
import json

emulator_pre_prompt:str = """
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
    """"""
    This is an example function.
    It adds two numbers.
    """"""
    pass

Example imagined function output:

result = example_function(3, {"value": 7})

Expected JSON output:

{"return": 10, "confidence": "medium-unique"}

This is the function documentation:
"""

class emulator:
    __last_return__ = None
    __last_content__ = None
    __last_data__ = { "return": None, "confidence": "low" }

    _default_api_key = "sk-proj-T7o4z8S4q9fnBNTdSq4iT3BlbkFJ82uVDLRaIAkx1sjwyE5C"

    def __init__(self, api_key=None):
        if api_key == None:
            self.api_key = emulator._default_api_key
        else:
            self.api_key = api_key

    def gpt4o(self, function_doc, function_call):
        global emulator_pre_prompt
        api_key=self.api_key
        l_body={"model": "gpt-4o",
                "messages": [
                    {
                    "role": "system",
                    "content": [{
                        "type": "text",
                        "text":emulator_pre_prompt + "---\n" + function_doc + "\n---"}]},{
                    "role": "user",
                    "content": [
                        {
                        "type": "text",
                        "text": function_call
                        }
                    ]}]
        }

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }

        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            json=l_body,
            headers=headers)

        self.__last_return__ = {"code": response.status_code,
                           "text": response.text}


        if response.status_code == 200:
            data = response.json()  # Assuming the response is in JSON format
            json_string = data["choices"][0]["message"]["content"]
            # Charger la chaîne JSON en un dictionnaire Python
            self.__last_content__ = json_string
            try:
                l_ret_data = json.loads(json_string)
            except json.JSONDecodeError as e:
                l_cleand = "\n".join(json_string.split('\n')[1:-1])
                l_ret_data = json.loads(l_cleand)

            self.__last_data__ = l_ret_data

            # Accéder à la valeur de "return" et la convertir en entier
            l_ret = l_ret_data["return"]
        else:
            print(f"Error {response.status_code}: {response.text}")
            self.__last_data__ = { "return": None, "confidence": "low" }
            l_ret = None



        return(l_ret)

    def emulate(self, func):
        def wrapper(*args, **kwargs):
            # Obtenir la signature de la fonction
            sig = inspect.signature(func)

            # Affiche les valeurs des arguments
            bound_args = sig.bind(*args, **kwargs)
            bound_args.apply_defaults()

            # Construct the function definition
            func_name = func.__name__
            func_params = ", ".join([f"{param_name}: {param.annotation.__name__}" if param.annotation != inspect.Parameter.empty else param_name for param_name, param in sig.parameters.items()])
            func_return = f" -> {sig.return_annotation.__name__}" if sig.return_annotation != inspect.Signature.empty else ""
            function_def = f"def {func_name}({func_params}):{func_return}\n    '''\n    {func.__doc__}\n    '''"

            # Construct the function call string
            func_call_args = ", ".join([str(value) for value in bound_args.arguments.values()])
            function_call = f"{func_name}({func_call_args})"

            # Call the LLM with dynamically constructed definition and function call
            try:
                result = self.gpt4o(function_def, function_call)
            except:
                print(function_def, function_call)
                result = None

            return result
        return wrapper


def test():
    llm=emulator()

    # Exemple d'utilisation du décorateur
    @llm.emulate
    def example_function(a:int, b:dict) -> int:
        """
        This is an example function.
        It adds two numbers.
        """
        pass
