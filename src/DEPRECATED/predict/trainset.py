import inspect

from ..utils.cache import Hostacache
from ..body.example import type_verificator
from ..core.config import DefaultManager
from .predict import load_cache

l_default = DefaultManager.get_default_model()

class TrainingSet():
    def __init__(self, func : callable):
        assert callable(func), "Please provide an hosta-injected function"
        self.func = func
        self.infos_cache = None

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
