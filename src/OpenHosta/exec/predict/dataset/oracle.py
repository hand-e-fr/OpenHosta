import inspect
from typing import Optional, Dict, Any, List, Type, Union, Literal,  get_args, get_origin

from ....core.logger import Logger
from ....core.config import Model, DefaultManager
from ....core.hosta import Func

_PROMPT = "{func_name}{signature}:\n    \"\"\"{docstring}\"\"\"\n\nIMPORTANT RULES:\n1. Input values should respect the type hints\n2. Output values MUST be diverse - avoid generating the same output repeatedly\n3. Each row must be in CSV format\n4. For text outputs, enclose them in double quotes\n5. NO MORE THAN 20% of outputs should be the same value\n6. Generate inputs across the entire possible range\n7. Ensure proper formatting for {return_type} output type"



class LLMSyntheticDataGenerator:
    """Generates synthetic data using a Language Model."""


    @staticmethod
    def _validate_row(row: str, expected_fields: List[Type], logger: Logger) -> Optional[List[Union[str, float]]]:
        logger.log_custom("Data Generation", f"Validating row: {row}", one_line=False)
        try:
            values = row.strip().split(',')

            if len(values) != len(expected_fields):
                return None

            result = []

            for value, expected_type in zip(values, expected_fields):
                if expected_type == str:
                    result.append(value)

                elif expected_type == float:
                    result.append(float(value))

                elif expected_type == int:
                    result.append(float(value))  # Convert to integer

                elif expected_type == bool:
                    if value.lower() == "true":
                        result.append(True)
                    elif value.lower() == "false":
                        result.append(False)
                    else:
                        return None

                elif get_origin(expected_type) is Literal:
                    valid_literals = get_args(expected_type)
                    if value.strip('"') in valid_literals:
                        result.append(value.strip('"'))
                    else:
                        return None

                elif get_origin(expected_type) is Union and type(None) in get_args(expected_type):
                    non_none_types = [t for t in get_args(expected_type) if t is not type(None)]
                    for t in non_none_types:
                        if t == int:
                            try:
                                result.append(int(value))
                                break
                            except ValueError:
                                continue
                        elif t == float:
                            try:
                                result.append(float(value))
                                break
                            except ValueError:
                                continue
                        elif t == str:
                            result.append(value)
                            break
                    else:
                        return None
                else:
                    return None
            return result
        except (ValueError, TypeError):
            return None

    @staticmethod
    def _format_example(input_val: Any, output_val: Any) -> str:
        """
        Format a single example based on inputs/outputs types.
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

        user_prompt += f"\n\nGenerate {examples_in_req} new DIVERSE inputs-outputs pairs, one per line, in CSV format"
        if output_type == str:
            user_prompt += " (remember to enclose string outputs in quotes ex: \"outputs\")"
        user_prompt += ":\n"

        user_prompt += f"{','.join(func.f_sig.parameters.keys())},outputs"
        user_prompt += "\n" + "\n".join([
            f"- {a} is type {b.annotation.__name__ if b.annotation != inspect.Parameter.empty else 'Any'}"
            for a, b in func.f_sig.parameters.items()
        ]) + "\n"
        user_prompt += f"- outputs is type {output_type.__name__}\n"

        return user_prompt


    @staticmethod
    def generate_synthetic_data(
            func: Func, # The function to generate data for
            logger: Logger, # Logger to use for logging
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
                to_append["outputs"] = ex_output

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
            _PROMPT
            .replace("{func_name}", func.f_name)
            .replace("{signature}", str(func.f_sig))
            .replace("{docstring}", func.f_doc)
        )
        prompt += LLMSyntheticDataGenerator._build_user_prompt(examples, func, output_type, examples_in_req)

        generated_data: List = []
        result: List[Dict] = []
        conversation_history: List = []
        attempts = 0

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
                        already_generated += f"{','.join(map(str, row))}\n"
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
                    cleaned_row = LLMSyntheticDataGenerator._validate_row(row, list(input_types.values()) + [output_type], logger)
                    if cleaned_row:
                        if cleaned_row not in generated_data:
                            dictrow = dict(zip(input_types.keys(), cleaned_row[:-1]))
                            dictrow["outputs"] = cleaned_row[-1]
                            result.append(dictrow)
                            generated_data.append(cleaned_row)

                # Keep conversation history manageable by keeping only last 10 messages
                if len(conversation_history) > 10:
                    # Always keep the system message
                    conversation_history = [conversation_history[0]] + conversation_history[-9:]

            except Exception as e:
                logger.log_custom("Data Generation", f"Error during generation: {e} line {e.__traceback__.tb_lineno}")

            attempts += 1

        return result
