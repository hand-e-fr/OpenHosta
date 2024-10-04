import inspect

import json

from .cache import Hostacache
from .example import type_verificator
from .prompt import PromptMananger
from .config import DefaultManager
from .predict import load_cache

l_default = DefaultManager.get_default_model()
_x = PromptMananger()
_generate_sys_prompt = _x.get_prompt("generate")

class TrainingSet():
    def __init__(self, func : callable):
        assert callable(func), "Please provide an hosta-injected function"
        self.func = func
        self.infos_cache = None

    def get_func_info(self):
        """
        function for get the information of the function
        """
        print("Get func info")
        pass
    
    def generate(self, size: int):
        """
        function that call an llm for generate a list of example
        based on the context of the function
        """
        cache = Hostacache(self.func)
        self.infos_cache = cache.create_hosta_cache()
        l_user_prompt = (
            "Here is your job :\n\nGenerate "+ f"{size}" " examples for the function:\n"
            +" Here is the function definition : " + f"{self.infos_cache['function_def']}\n")

        response = l_default.api_call(
            sys_prompt=_generate_sys_prompt,
            user_prompt=l_user_prompt,
            creativity=0.5,
            diversity=0.5,
        )

        data = response.json()
        type_json = data["choices"][0]["message"]["content"]
        examples = json.loads(type_json)
        # print('#'*100)
        # print(examples, "#")
        # print('#'*100)
        cache_end = Hostacache(self.func, "ho_data", value=examples)
        cache_end.create_hosta_cache()
        return examples


    def visualize(self):
        """
        function for visualize the training set idk how for now
        maybe let the hostashpère do it
        """
        hosta_cache = load_cache(self.func)
        print("ho_example:")
        for i in range(len(hosta_cache["ho_example"])):
            print(hosta_cache["ho_example"][i])
        print("ho_data:")
        for i in range(len(hosta_cache["ho_data"])):
            print(hosta_cache["ho_data"][i])
        return [hosta_cache["ho_example"], hosta_cache["ho_data"]]

    def add(self, *args, hosta_out=None,**kwargs):
        """
        function for add an example to the training set
        """
        input_type = {}
        output_type = {}
        data_dict = {}
        hosta_func = self.func

        if hosta_out is None:
            raise ValueError("Please provide hosta_out for output.")
        if hosta_func is None:
                raise ValueError("Please provide hosta_func for specifying the function")
        elif callable(hosta_func):
            func = hosta_func
        else:
            raise ValueError("Please provide hosta_func for specifying the function")

        try:
            sig = inspect.signature(func)
            for param in sig.parameters.values():
                input_type[param.name] = param.annotation
            output_type["hosta_out"] = sig.return_annotation
        except:
            raise ValueError("Function does not have a signature")

        type_verificator(args, kwargs, input_type, output_type, hosta_out, func, data_dict)
        cache_id = "ho_data"
        cache = Hostacache(func, cache_id, data_dict)
        cache.create_hosta_cache()


    def validate(self):
        """
        function for validate the training set with a llm
        and with parameters of validation maybe
        """
        print("Validate not implemented yet")
        pass


    def same_as(self, func: callable):
        """
        function fo copy the training set of another function
        """
        print("Same as not implemented yet")
        pass


    def remove(self, *args, **kwargs):
        """
        function for remove an example to the training set
        """
        print("Remove not implemented yet")
        pass 

    def encode(self):
        """
        function for encode an input
        """
        print("Encode not implemented yet")
        pass

    def decode(self):
        """
        function for decode an input
        """
        print("Decode not implemented yet")
        pass

    def normalize(self):
        """
        function for normalize an input
        """
        print("Normalize not implemented yet")
        pass

    def denormalize(self):
        """
        function for denormalize an input
        """
        print("Denormalize not implemented yet")
        pass
