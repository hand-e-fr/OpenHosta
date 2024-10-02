import os
import os

from .cache import Hostacache
from .builder import Builder
from .datapreparator import Datapreparator
from .example import type_verificator
import inspect

CACHE_DIR = "__hostacache__"
os.makedirs(CACHE_DIR, exist_ok=True)

def _exec_predict(
        _function_infos: dict = None,
        _function_obj: object = None,

        encoder = None,
        decoder = None,
        skip_data: list = [],
        out_data: list = [],
        complexity: int = None,
        config: dict = None,
        optimizer: str = None,
        loss: str = None,
        epochs: int = None,
        batch_size: int = None,
        force_train: bool = False,
        norm_max: float = None,
        norm_min: float = None
):
    hidden_dir = os.path.join(CACHE_DIR, f".model_{_function_obj.__name__}_{_function_infos['hash_function']}")
    os.makedirs(hidden_dir, exist_ok=True)

    config_path = os.path.join(hidden_dir, "config.json")
    weight_path = os.path.join(hidden_dir, "model.pth")
    normalisation_path = os.path.join(hidden_dir, "normalisation.json")

    preparator = Datapreparator(norm_max, norm_min, encoder, decoder)
    builder = Builder(hidden_dir)

    if not os.path.exists(config_path) or not os.path.exists(weight_path) or not os.path.exists(normalisation_path) or force_train==True:
        assert _function_infos["ho_example_links"] != [], "No example provided please provide at least one example for the model"

        dataset = preparator.prepare(_function_infos["ho_example_links"], skip_data, out_data)
        dataset_normalize = preparator.normalize_dataset(dataset)
        preparator.save_normalization_params(normalisation_path)

        len_input = len(dataset_normalize[0][0])
        len_output = len(dataset_normalize[0][1])
        #TODO : we will need to add architecture choice after for other type of model
        architecture = builder.build(len_input, len_output, complexity, config, optimizer, loss)
        if batch_size is None:
            batch_size = int(0.05 * len(dataset_normalize)) if 0.05 * len(dataset_normalize) > 1 else 1 # 5% of the dataset or one 
        else:
            batch_size = batch_size
        train, eval = preparator.split(dataset_normalize, batch_size)

        epochs = int(2*len(dataset_normalize) / batch_size) if epochs is None else epochs
        builder.trains(config, train, eval, epochs=epochs)
    else:
        print("\033[93mModel already trained, skipping training\033[0m")
        preparator.load_normalization_params(normalisation_path)
    
    inference = preparator.prepare_input(_function_infos["function_args"], skip_data)

    inference_normalize = preparator.normalize_inference(inference)
    torch_inference = preparator.convert(inference_normalize)

    prediction = builder.load_inference(config_path, weight_path, torch_inference)
    prediction_denormalize = preparator.denormalize_prediction(prediction)
    result = prediction_denormalize[0]

    return result

def continue_train():
    """
    Continue the training of the model
    - Reload a pth and add a dataset or not for the model
    save a new pth after the training decided in the emulate or not or in this function also (diff parameters
    of training and not architecture)
    """
    print("Continue training")
    pass

def to_emulate():
    """
    This function is used to emulate 
    the function as like he is emulated by the model
    just translate the function to be emulated
    """
    print("To emulate")
    pass

def retrain():
    """
    This function is used to retrain the model
    with the same dataset or not and for the start
    """
    pass

def save():
    """
    Save the model in a specified path and a specified name or not
    """
    print("Save")
    pass

def architecture():
    """
    This function is used to change the architecture
    of the model manually or with the help of a llm
    """
    print("Architecture")
    pass


class TrainingSet():
    def __init__(self, func : callable):
        assert callable(func), "Please provide a function"
        self.func = func

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
        print("Generate")
        pass

    def visualize(self):
        """
        function for visualize the training set idk how for now
        maybe let the hostashpère do it
        """
        print("Visualize")
        pass

    def validate(self):
        """
        function for validate the training set with a llm
        and with parameters of validation maybe
        """
        print("Validate")
        pass

    def same_as(self, func: callable):
        """
        function fo copy the training set of another function
        """
        print("Same as")
        pass

    def add(self, *args, hosta_out=None,**kwargs):
        """
        function for add an example to the training set
        """
        input_type = {}
        output_type = {}
        data_dict = {}
        hosta_func = self.func

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


    def remove(self, *args, **kwargs):
        """
        function for remove an example to the training set
        """
        print("Remove")
        pass 

    def encode(self):
        """
        function for encode an input
        """
        print("Encode")
        pass

    def decode(self):
        """
        function for decode an input
        """
        print("Decode")
        pass

    def normalize(self):
        """
        function for normalize an input
        """
        print("Normalize")
        pass

    def denormalize(self):
        """
        function for denormalize an input
        """
        print("Denormalize")
        pass

def load_training_example(hosta_path: str, hosta_func: callable):
    """
    Load the training example from a file
    """
    print("Load training example")
    pass