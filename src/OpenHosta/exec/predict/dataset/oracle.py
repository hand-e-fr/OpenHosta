import inspect
from collections import Counter
from typing import Optional, Dict, Any, List, Type

from .dataset import HostaDataset, SourceType
from ....core.config import Model, DefaultManager
from ....core.hosta import Func
from ....utils.prompt import PromptManager


class LLMSyntheticDataGenerator:
    """
    Generates synthetic data using a Language Model.
    """

    @staticmethod
    def _validate_row(row: str, expected_fields: int, return_type: Type) -> Optional[List[str]]:
        """
        Validate and clean up a generated row according to the expected number of fields and return type.
        """
        try:
            values = LLMSyntheticDataGenerator._parse_row(row)
            if len(values) != expected_fields:
                return None
            values = LLMSyntheticDataGenerator._format_row_values(values, return_type)
            return values
        except Exception as exc:
            print(f"Error during row validation: {exc}")
            return None

    @staticmethod
    def _parse_row(row: str) -> List[str]:
        """
        Parse a CSV-like row into a list of values, handling quotes and commas.
        """
        values, in_quotes, current_value = [], False, []
        for char in row.strip():
            if char == '"':
                in_quotes = not in_quotes
            elif char == ',' and not in_quotes:
                values.append(''.join(current_value))
                current_value = []
            else:
                current_value.append(char)
        values.append(''.join(current_value))
        return [v.strip().strip('"') for v in values]

    @staticmethod
    def _format_row_values(values: List[str], return_type: Type) -> List[str]:
        """
        Format row values, converting numeric inputs and ensuring output type is correct.
        """
        for i in range(len(values) - 1):  # Exclude the output value
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

    @staticmethod
    def _format_example(input_val: Any, output_val: Any) -> str:
        """
        Format a single example for display, handling both input and output types appropriately.
        """
        input_str = ','.join(map(str, input_val)) if isinstance(input_val, (list, tuple)) else str(input_val)
        output_str = f'"{output_val}"' if isinstance(output_val, str) else str(output_val)
        return f"{input_str},{output_str}"

    @staticmethod
    def _is_diverse_enough(data: List[List[str]], new_row: List[str]) -> bool:
        """
        Check if a new row is diverse enough based on the distribution of outputs in the data.
        """
        if not data:
            return True

        outputs = [row[-1] for row in data]
        output_counts = Counter(outputs)
        new_output = new_row[-1]
        max_frequency = 0.2

        current_count = output_counts.get(new_output, 0)
        return (current_count / (len(outputs) + 1)) < max_frequency

    @staticmethod
    def _build_user_prompt(
        examples: List[Dict],
        func: Func,
        output_type: Type,
        examples_in_req: int,
    ) -> str:
        """
        Construct the user prompt for generating synthetic data.
        """
        user_prompt = LLMSyntheticDataGenerator._generate_example_block(examples)
        user_prompt += LLMSyntheticDataGenerator._generate_prompt_footer(func, output_type, examples_in_req)
        return user_prompt

    @staticmethod
    def _generate_example_block(examples: List[Dict]) -> str:
        """
        Generate a section in the prompt showing reference examples.
        """
        if not examples:
            return ""
        example_block = "\nReference examples (Input → Output):\n"
        for input_val, output_val in examples.items():
            example_block += f"{LLMSyntheticDataGenerator._format_example(input_val, output_val)}\n"
        return example_block

    @staticmethod
    def _generate_prompt_footer(func: Func, output_type: Type, examples_in_req: int) -> str:
        """
        Generate the footer of the prompt, specifying the function and output details.
        """
        prompt_footer = f"\n\nGenerate {examples_in_req} new DIVERSE input-output pairs, one per line, in CSV format"
        if output_type == str:
            prompt_footer += ' (remember to enclose string outputs in quotes ex: "output")'
        prompt_footer += ":"

        prompt_footer += f"\n{','.join(func.f_sig.parameters.keys())},output"
        prompt_footer += f"\n{','.join([f'\n- {a} is type {b.annotation.__name__ if b.annotation != inspect.Parameter.empty else 'Any'}' \
                                        for a, b in func.f_sig.parameters.items()])}\n"
        prompt_footer += f"- output is type {output_type.__name__}\n"

        return prompt_footer

    @staticmethod
    def _create_conversation_history(prompt: str) -> List[Dict]:
        """
        Initialize conversation history with a system message.
        """
        return [
            {
                "role": "system",
                "content": "You are a data generation assistant focused on creating diverse, realistic data. Avoid repetitive patterns."
            },
            {
                "role": "user",
                "content": prompt
            }
        ]

    @staticmethod
    def _add_previous_data_to_prompt(generated_data: List[List[str]]) -> str:
        """
        Add already generated data to the user prompt to avoid duplicates.
        """
        if not generated_data:
            return ""
        already_generated = "\nAlready generated data (please avoid these exact combinations):\n"
        for row in generated_data:
            already_generated += f"{','.join(row)}\n"
        return already_generated

    @staticmethod
    def _send_request_to_model(model: Model, conversation_history: List[Dict]) -> Dict:
        """
        Send a request to the language model API.
        """
        return model.api_call(messages=conversation_history, temperature=1.0, json_form=False)

    @staticmethod
    def generate_synthetic_data(
        func: Func,
        request_amounts: int = 3,
        examples_in_req: int = 50,
        model: Optional[Model] = None
    ) -> HostaDataset:
        """
        Main function to generate synthetic data using a Language Model.
        """
        input_types = dict(zip(func.f_args.keys(), func.f_type[0]))
        output_type = func.f_type[1]
        examples = LLMSyntheticDataGenerator._extract_previous_examples(func)

        model, prompt = LLMSyntheticDataGenerator._prepare_generation_params(model, func, examples, output_type, examples_in_req)
        conversation_history = LLMSyntheticDataGenerator._create_conversation_history(prompt)

        generated_data, result, attempts, expected_fields = [], [], 0, len(input_types) + 1

        while attempts < request_amounts:
            try:
                # Add details of already generated data to the prompt
                content = prompt + LLMSyntheticDataGenerator._add_previous_data_to_prompt(generated_data)

                conversation_history[-1]["content"] = content  # Update the last user message
                response = LLMSyntheticDataGenerator._send_request_to_model(model, conversation_history)

                # Add the assistant's response to the conversation history
                conversation_history.append({
                    "role": "assistant",
                    "content": response["choices"][0]["message"]["content"]
                })

                # Process the response and validate new rows
                new_rows = response["choices"][0]["message"]["content"].strip().split('\n')
                for row in new_rows:
                    cleaned_row = LLMSyntheticDataGenerator._validate_row(row, expected_fields, output_type)
                    if cleaned_row and LLMSyntheticDataGenerator._is_diverse_enough(generated_data, cleaned_row):
                        if cleaned_row not in generated_data:
                            dict_row = dict(zip(input_types.keys(), cleaned_row[:-1]))
                            dict_row["output"] = cleaned_row[-1]
                            result.append(dict_row)
                            generated_data.append(cleaned_row)

                # Keep conversation history manageable
                conversation_history = LLMSyntheticDataGenerator._prune_history(conversation_history)

            except Exception as e:
                print(f"Error during generation: {e}")

            attempts += 1

        return HostaDataset.from_list(result)
