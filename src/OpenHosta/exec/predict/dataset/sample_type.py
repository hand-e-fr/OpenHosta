from typing import List, Any, Optional

# from pydantic import BaseModel


class Sample:
    """
    A class to handle data samples for machine learning.
    Expects a dictionary where all keys except '_outputs' are considered as _inputs.
    
    Example:
        data = {
            'feature1': [1, 2],     # Any key except '_outputs' is considered _inputs
            'feature2': {'a': 3},    # Can contain any nested structure
            'feature3': 4,           # Can contain any primitive type
            'feature4': BaseModel(), # Can contain Pydantic models 
            '_outputs': 9      # Optional _outputs
        }
        sample = Sample(data)
    """
    
    def __init__(self, data: dict):
        if not isinstance(data, dict):
            raise TypeError("Data must be a dictionary")
            
        self._inputs: List[Any] = []
        self._outputs: Optional[Any] = None
        
        output_data = data.pop('_outputs', None)
        if output_data is not None:
            output_flattened = self._flatten_data(output_data)
            self._outputs = output_flattened[0] if len(output_flattened) == 1 else output_flattened

        for value in data.values():
            self.input.extend(self._flatten_data(value))

    def _flatten_data(self, data: Any) -> List[Any]:
        """
        Flatten any nested data structure into a list.
        Handles: BaseModel, dict, list/tuple, primitive types
        """
        # if isinstance(data, BaseModel):
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

    @property
    def output(self) -> Optional[Any]:
        """Get the _outputs label (None if no _outputs was provided)"""
        return self._outputs

    def __repr__(self) -> str:
        return f"Sample(_inputs={self.input}, _outputs={self.output})"



############################################
# # Example usage:
# if __name__ == "__main__":
#     # Multiple _inputs
#     data1 = {
#         'feature1': [0, 1],
#         'feature2': 2,
#         'feature3': {'a': 3},
#         '_outputs': '6'
#     }
#     sample1 = Sample(data1)
#     print(f"{sample1}")
#     print(f"Input: {sample1._inputs}")
#     print(f"Output: {sample1._outputs}")

#     # Single _inputs
#     data2 = {
#         '_inputs': [0, 1, 2, 3]
#     }
#     sample2 = Sample(data2)
#     print(f"{sample2}")
#     print(f"Input: {sample2._inputs}")
#     print(f"Output: {sample2._outputs}")


#     # Complex nested structure
#     data3 = {
#         'deep_feature': {"zero": 0,'nested': {'value': 1}},
#         'array_feature': [2, 3],
#         '_outputs': {'label': 6}
#     }
#     sample3 = Sample(data3)
#     print(f"{sample3}")
#     print(f"Input: {sample3._inputs}")
#     print(f"Output: {sample3._outputs}")

#     # Pydantic model
#     class MyModel(BaseModel):
#         a: int
#         b: str
#         c: list

#     data4 = {
#         'feature': MyModel(a=1, b='2', c=[3]),
#         '_outputs': 6
#     }
#     sample4 = Sample(data4)
#     print(f"{sample4}")
#     print(f"Input: {sample4._inputs}")
#     print(f"Output: {sample4._outputs}")

