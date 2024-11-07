from inspect import Signature
from typing import Optional, Dict, Any, List, Tuple, Type

from .dataset import HostaDataset

from ....utils.prompt import PromptManager
from ....core.config import Model, DefaultManager
from ....core.hosta import Hosta, Func


class LLMSyntheticDataGenerator:
    """Generates synthetic data using a Language Model."""


    @staticmethod
    def _validate_row(row: str, expected_fields: int, return_type: str) -> Optional[List[str]]:
        try:
            values = []
            in_quotes = False
            current_value = []

            for char in row.strip():
                if char == '"':
                    in_quotes = not in_quotes
                elif char == ',' and not in_quotes:
                    values.append(''.join(current_value))
                    current_value = []
                else:
                    current_value.append(char)
            values.append(''.join(current_value))

            # Clean up the values
            values = [v.strip().strip('"') for v in values]

            if len(values) != expected_fields:
                return None

            # Convert numeric inputs to proper format
            for i in range(len(values) - 1):  # All except last value
                try:
                    num = float(values[i])
                    values[i] = str(int(num) if num.is_integer() else num)
                except ValueError:
                    pass

            # Handle the output value based on return type
            if return_type == "str":
                values[-1] = f'"{values[-1]}"'
            elif return_type in ["int", "float"]:
                try:
                    num = float(values[-1])
                    values[-1] = str(int(num) if num.is_integer() else num)
                except ValueError:
                    return None

            return values
        except Any as _:
            return None

    @staticmethod
    def generate_synthetic_data(
            func: Func, # The function to generate data for
            request_amounts: int = 3, # Amount of requests to the model
            examples_in_req: int = 50, # Examples amount in each request
            model: Optional[Model] = None, # Model to use for data generation
            examples: Optional[List[Dict[str, Any]]] = None # Examples to use for data generation (ex: {"input1": 1, "input2": "hello", "output": 2})
    ) -> HostaDataset:
        input_types: Dict[str, Type] = dict(zip(func.f_args.keys(), func.f_type[0]))
        output_type: Type = func.f_type[1]
        try:
            assert input_types and len(input_types) > 0, "Input types must be provided."
            assert output_type, "Output type must be provided."
            assert request_amounts > 0, "Request amount must be greater than 0."
            assert examples_in_req > 0, "Examples amount in each request must be greater than 0."

            if not model:
                model = DefaultManager.get_default_model()
            assert model, "Model must be provided."

            # Check if examples are provided respect input types and output type
            if examples:
                for i, ex in enumerate(examples):
                    assert "output" in ex, f"ex[{i}]: Output \"output\" (type: {output_type.__name__}) must be provided."
                    assert isinstance(ex["output"], output_type), f"ex[{i}]: Output type must be {output_type}."
                    for key in input_types:
                        if key not in ex:
                            assert input_types[key] == str, f"ex[{i}]: Input \"{key}\" (type: {input_types[key].__name__}) must be provided."
                        assert isinstance(ex[key], input_types[key]), f"ex[{i}]: Input type for \"{key}\" must be {input_types[key]}."
        except AssertionError as e:
            raise ValueError(f"Invalid parameters: {e}")

        pm = PromptManager()
        meta_prompt: str = (
            pm.get_prompt("synthetic_data_generator")
            .replace("{func_name}", func.f_name)
            .replace("{signature}", str(func.f_sig))
            .replace("{docstring}", func.f_doc)
        )

        # TODO: Implement data generation logic
        generated_data: List = []

        return HostaDataset()
