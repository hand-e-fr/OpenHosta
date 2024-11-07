import os
from typing import Callable, Dict, List, Tuple, Union, Any, Optional, Literal
import inspect
import openai
import csv
import random
from collections import Counter


class SyntheticDataGenerator:
    def __init__(self, api_key: str):
        openai.api_key = api_key

    def _format_example(self, input_val: Any, output_val: Any) -> str:
        """
        Format a single example based on input/output types.
        """
        if isinstance(input_val, (list, tuple)):
            input_str = ','.join(map(str, input_val))
        else:
            input_str = str(input_val)

        if isinstance(output_val, str):
            output_str = f'{output_val}'  # Enclose strings in quotes
        else:
            output_str = str(output_val)

        return f"{input_str},{output_str}"

    def _create_prompt(self, example_per_request: int, func: Callable, examples: Dict[Any, Any] = None) -> str:
        signature = inspect.signature(func)
        docstring = inspect.getdoc(func) or ""
        return_type = signature.return_annotation.__name__ if signature.return_annotation != inspect.Parameter.empty else "Any"

        prompt = f"""

{func.__name__}{signature}:
    \"\"\"{docstring}\"\"\"

IMPORTANT RULES:
1. Input values should respect the type hints
2. Output values MUST be diverse - avoid generating the same output repeatedly
3. Each row must be in CSV format
4. For text outputs, enclose them in double quotes
5. NO MORE THAN 20% of outputs should be the same value
6. Generate inputs across the entire possible range
7. Ensure proper formatting for {return_type} output type
"""

        if examples:
            prompt += "\nReference examples (Input → Output):\n"
            for input_val, output_val in examples.items():
                prompt += f"{self._format_example(input_val, output_val)}\n"

        prompt += f"\nGenerate {example_per_request} new DIVERSE input-output pairs, one per line, in CSV format"
        if return_type == "str":
            prompt += " (remember to enclose string outputs in quotes ex: \"output\")"
        prompt += ":\n"

        prompt += f"{','.join(signature.parameters.keys())},output\n"
        prompt += f"\n{','.join([str(f"- {a} is type {b.annotation.__name__ if b.annotation != inspect.Parameter.empty else 'Any'}") for a, b in signature.parameters.items()])}\n"
        prompt += f"- output is type {return_type}\n"

        return prompt

    def _validate_row(self, row: str, expected_fields: int, return_type: str) -> Optional[List[str]]:
        try:
            # Handle quoted strings in CSV
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
        except:
            return None

    def _is_diverse_enough(self, data: List[List[str]], new_row: List[str]) -> bool:
        if not data:
            return True

        outputs = [row[-1] for row in data]
        output_counts = Counter(outputs)
        new_output = new_row[-1]
        current_count = output_counts.get(new_output, 0)
        max_frequency = 0.2

        return (current_count / (len(outputs) + 1)) < max_frequency

    def generate_data(self,
                      func: Callable,
                      attempts_number: int = 100,
                      examples: Dict[Any, Any] = None,
                      output_file: str = "synthetic_data.csv",
                      example_per_request: int = 10) -> None:

        signature = inspect.signature(func)
        params = list(signature.parameters.keys())
        return_type = signature.return_annotation.__name__ if signature.return_annotation != inspect.Parameter.empty else "Any"
        expected_fields = len(params) + 1
        headers = params + ['output']

        generated_data = []
        conversation_history = []

        # Initialize conversation with system message
        conversation_history.append({
            "role": "system",
            "content": "You are a data generation assistant focused on creating diverse, realistic data. Avoid repetitive patterns."
        })

        attempts = 0

        while attempts < attempts_number:
            try:
                content = self._create_prompt(example_per_request, func, examples)

                # Add information about already generated data
                if generated_data:
                    already_generated = "\nAlready generated data (please avoid these exact combinations):\n"
                    for row in generated_data:
                        already_generated += f"{','.join(row)}\n"
                    content += already_generated

                # Add the user message to conversation history
                conversation_history.append({
                    "role": "user",
                    "content": content
                })

                response = openai.ChatCompletion.create(
                    model="gpt-4o-mini",
                    messages=conversation_history,
                    temperature=1.0
                )

                # Add the assistant's response to conversation history
                conversation_history.append({
                    "role": "assistant",
                    "content": response.choices[0].message.content
                })

                rows = response.choices[0].message.content.strip().split('\n')

                for row in rows:
                    cleaned_row = self._validate_row(row, expected_fields, return_type)
                    if cleaned_row and self._is_diverse_enough(generated_data, cleaned_row):
                        # append cleaned_row if it is not already in generated_data
                        if cleaned_row not in generated_data:
                            generated_data.append(cleaned_row)

                # Keep conversation history manageable by keeping only last 10 messages
                if len(conversation_history) > 10:
                    # Always keep the system message
                    conversation_history = [conversation_history[0]] + conversation_history[-9:]

            except Exception as e:
                print(f"Error during generation: {e}")

            attempts += 1

        random.shuffle(generated_data)

        with open(output_file, 'w', newline='', encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(headers)
            writer.writerows(generated_data)






# def addition(x: int, y: int) -> int:
#     """
#     Adds two integers and returns their sum.
#     The inputs should be positive integers between 0 and 100.
#     """
#     return x + y
#
# # Example input-output pairs
# examples = {
#     1: ([5, 3], 8),
#     2: ([10, 20], 30),
#     3: ([0, 7], 7)
# }

# def get_lattitude(city: str, country: str) -> float:
#     """
#     This function returns the lattitude of a city in a country.
#     """
#     pass
#
# examples = {
#     1: (["New York", "USA"], 40.7128),
#     2: (["Paris", "France"], 48.8566),
#     3: (["Tokyo", "Japan"], 35.6895)
# }

def average_seasonal_temperature(city: str, season: Literal["winter", "spring", "summer", "fall"], latitude: float, longitude: float) -> float:
    """
    This function returns the average seasonal temperature in a city.
    """
    pass

_examples = {
    1: (["New York", "winter", 40.7128, -74.0060], 0),
    2: (["Paris", "spring", 48.8566, 2.3522], 0),
    3: (["Tokyo", "summer", 35.6895, 139.6917], 0)
}

# Initialize the generator
generator = SyntheticDataGenerator(os.environ['OPENAI_API_KEY'])

# Generate synthetic data
generator.generate_data(
    func=average_seasonal_temperature,
    attempts_number=5,
    examples=_examples,
    output_file='build/average_seasonal_temperature.csv',
    example_per_request=100
)
