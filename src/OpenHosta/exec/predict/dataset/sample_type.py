from typing import List, Any, Optional

class Sample:
    """
    A class to handle data samples for machine learning.
    Expects a dictionary where all keys except  "outputs' are considered as _inputs.
    
    Example:
        data = {
            'feature1': [1, 2],     # Any key except 'outputs' is considered _inputs
            'feature2': {'a': 3},    # Can contain any nested structure
            'feature3': 4,           # Can contain any primitive type
            'outputs': 9      # Optional outputs
        }
        sample = Sample(data)
    """
    
    def __init__(self, data: dict):
        if not isinstance(data, dict):
            raise TypeError("Data must be a dictionary")
            
        self._inputs: List[Any] = []
        self._outputs: Optional[Any] = None
        
        output_data = data.pop('outputs', None)
        if output_data is not None:
            output_flattened = self._flatten_data(output_data)
            self._outputs = output_flattened[0] if len(output_flattened) == 1 else output_flattened

        for value in data.values():
            self.input.extend(self._flatten_data(value))

    def _flatten_data(self, data: Any) -> List[Any]:
        """
        Flatten any nested data structure into a list.
        Handles: Model, dict, list/tuple, primitive types
        """
        # if isinstance(data, Model):
        #     return self._flatten_data(data.model_dump())
        if isinstance(data, dict):
            result = []
            for value in data.values():
                result.extend(self._flatten_data(value))
            return result
        if isinstance(data, (list, tuple)):
            result = []
            for item in data:
                result.extend(self._flatten_data(item))
            return result
        return [data]

    @property
    def input(self) -> List[Any]:
        """Get the _inputs features"""
        return self._inputs

    @input.setter
    def input(self, value: List[Any]) -> None:
        """Set the input features."""
        if not isinstance(value, list):
            raise ValueError("The 'input' property must be a list.")
        self._inputs = value

    @property
    def output(self) -> Optional[Any]:
        """Get the _outputs label (None if no _outputs was provided)"""
        return self._outputs

    @output.setter
    def output(self, value: Optional[Any]) -> None:
        """Set the output label."""
        self._outputs = value

    def __repr__(self) -> str:
        return f"Sample(_inputs={self.input}, _outputs={self.output})"
