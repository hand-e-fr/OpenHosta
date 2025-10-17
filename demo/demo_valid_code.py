from OpenHosta import emulate, Validator, ValidationError, reload_dotenv
import ast

reload_dotenv()


class ValidPythonValidator(Validator):
    def validate_test(self, value: str) -> None:
        try:
            ast.parse(value)
        except SyntaxError as e:
            raise ValidationError(f"Invalid Python syntax: {e}")


def generate_function(description: str) -> ValidPythonValidator:
    """Generate a Python function based on description. Return only the function code."""
    return emulate()


# Test
code = generate_function("Create a function that adds two numbers")

print(f"Generated code:\n{code}\n")
print("✓ Valid Python syntax")
