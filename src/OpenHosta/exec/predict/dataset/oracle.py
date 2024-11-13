import inspect
from collections import Counter
from typing import Optional, Dict, Any, List, Type

from ....core.config import Model, DefaultManager
from ....core.hosta import Func
from ....utils.prompt import PromptManager


class LLMSyntheticDataGenerator:
    """Generates synthetic data using a Language Model."""


    @staticmethod
    def _validate_row(row: str, expected_fields: int, return_type: Type) -> Optional[List[str]]:
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
            if return_type == str:
                values[-1] = f'"{values[-1]}"'
            elif return_type in (int, float):
                try:
                    num = float(values[-1])
                    values[-1] = str(int(num) if num.is_integer() else num)
                except ValueError:
                    return None

            return values
        except Any as _:
            return None

    @staticmethod
    def _format_example(input_val: Any, output_val: Any) -> str:
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

    @staticmethod
    def _is_diverse_enough(data: List[List[str]], new_row: List[str]) -> bool:
        if not data:
            return True

        outputs = [row[-1] for row in data]
        output_counts = Counter(outputs)
        new_output = new_row[-1]
        current_count = output_counts.get(new_output, 0)
        max_frequency = 0.2

        return (current_count / (len(outputs) + 1)) < max_frequency

    @staticmethod
    def _build_user_prompt(
            examples: List[Dict],
            func: Func,
            output_type: Type,
            examples_in_req: int,
    ):
        user_prompt = ""

        if examples:
            user_prompt += "\nReference examples (Input → Output):\n"
            for input_val, output_val in examples.items():
                user_prompt += f"{LLMSyntheticDataGenerator._format_example(input_val, output_val)}\n"

        user_prompt += f"\n\nGenerate {examples_in_req} new DIVERSE input-output pairs, one per line, in CSV format"
        if output_type == str:
            user_prompt += " (remember to enclose string outputs in quotes ex: \"output\")"
        user_prompt += ":\n"

        user_prompt += f"{','.join(func.f_sig.parameters.keys())},output"
        user_prompt += f"\n{','.join([str(f"\n- {a} is type {b.annotation.__name__ if b.annotation != inspect.Parameter.empty else 'Any'}")\
                                      for a, b in func.f_sig.parameters.items()])}\n"
        user_prompt += f"- output is type {output_type.__name__}\n"

        return user_prompt


    @staticmethod
    def generate_synthetic_data(
            func: Func, # The function to generate data for
            request_amounts: int = 3, # Amount of requests to the model
            examples_in_req: int = 50, # Examples amount in each request
            model: Optional[Model] = None # Model to use for data generation
    ) -> List[Dict]:
        input_types: Dict[str, Type] = dict(zip(func.f_args.keys(), func.f_type[0]))
        output_type: Type = func.f_type[1]
        examples: List[Dict] = []
        if func.f_mem:
            for ex in func.f_mem:
                ex_inputes = list(ex.value["in_"].values())
                ex_output = ex.value["out"]
                to_append = {}
                for i, key in enumerate(input_types.keys()):
                    to_append[key] = ex_inputes[i]
                to_append["output"] = ex_output

        if not model:
            model = DefaultManager.get_default_model()

        try:
            assert input_types and len(input_types) > 0, "Input types must be provided."
            assert output_type, "Output type must be provided."
            assert request_amounts > 0, "Request amount must be greater than 0."
            assert examples_in_req > 0, "Examples amount in each request must be greater than 0."
            assert model, "Model must be provided."
        except AssertionError as e:
            raise ValueError(f"Invalid parameters: {e}")

        prompt: str = (
            PromptManager().get_prompt("synthetic_data_generator")
            .replace("{func_name}", func.f_name)
            .replace("{signature}", str(func.f_sig))
            .replace("{docstring}", func.f_doc)
        )
        prompt += LLMSyntheticDataGenerator._build_user_prompt(examples, func, output_type, examples_in_req)

        # TODO: Implement data generation logic
        generated_data: List = []
        result: List[Dict] = []
        conversation_history: List = []
        attempts = 0
        expected_fields = len(input_types) + 1

        conversation_history.append({
            "role": "system",
            "content": "You are a data generation assistant focused on creating diverse, realistic data. Avoid repetitive patterns."
        })

        while attempts < request_amounts:
            try:
                content = prompt

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

                response = model.api_call(
                    messages=conversation_history,
                    temperature=1.0,
                    json_form=False,
                )

                # Add the assistant's response to conversation history
                conversation_history.append({
                    "role": "assistant",
                    "content": response["choices"][0]["message"]["content"]
                })

                rows = response["choices"][0]["message"]["content"].strip().split('\n')

                for row in rows:
                    cleaned_row = LLMSyntheticDataGenerator._validate_row(row, expected_fields, output_type)
                    if cleaned_row and LLMSyntheticDataGenerator._is_diverse_enough(generated_data, cleaned_row):
                        # append cleaned_row if it is not already in generated_data
                        if cleaned_row not in generated_data:
                            dictrow = dict(zip(input_types.keys(), cleaned_row[:-1]))
                            dictrow["output"] = cleaned_row[-1]
                            result.append(dictrow)
                            generated_data.append(cleaned_row)

                # Keep conversation history manageable by keeping only last 10 messages
                if len(conversation_history) > 10:
                    # Always keep the system message
                    conversation_history = [conversation_history[0]] + conversation_history[-9:]

            except Exception as e:
                print(f"Error during generation: {e}")

            attempts += 1

        return result
