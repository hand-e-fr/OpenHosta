import inspect
import requests
import json



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
        api_key=self.api_key
        l_body={"model": "gpt-4o", 
                "messages": [
                    {
                    "role": "system",
                    "content": [{
                        "type": "text",
                        "text": """
You are an emulator of impossible to code functions. 
I give you the description of the function using python way of declaring function. 
I cannot give you the function body as I do not have any idea how to code it. 
It might even not be possible to code it. So you shall not try to write the body. Instead, directly imagine the function output.
In the conversation I directly write the function call as if it was called in python. 
You directly answer whatever you believe would be a good return for the function.
When you produce an answer, you estimate the confidence level: 
  - "low": You did your best, but with the provided description and your knowledge,  you are not confident about the answer.
  - "medium-instance": You did your best, and with the provided description and your knowledge,  you are pretty sure this answer is valid but not the only valid answer.
  - "medium-unique": You did your best, and with the provided description and your knowledge,  you are pretty sure this answer is the unique and valid answer.
  - "high-instance": You did your best, and you are sure that your provided answer is a valid answer. It is a well known function or you can easely implement a python code that yield elements from de list of valid answers. this answer is randomly chosen from the list of valid answers.
  - "high-unique": You did your best, and you are sure that your provided answer is the unique valid answer. It is a well known function or you can easely implement a python code that solve the question and calculate this answer given this input.
  
If outout is documented as python structure, you translates it to JSON.
You encode the return in valid JSON format, without comment, using the following format:
{"return":..., "confidence":...}

This is the function documentation:
---
"""+function_doc+"""
---

"""}]},{
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
