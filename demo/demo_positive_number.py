from OpenHosta import emulate, Validator, ValidationError, reload_dotenv

reload_dotenv()


class PositiveIntValidator(Validator):
    def validate_test(self, value: int) -> None:
        if value <= 0:
            raise ValidationError(f"Number must be positive, got {value}")


def extract_age(text: str) -> PositiveIntValidator:
    """Extract the age from the text (must be positive)."""
    return emulate()


# Test
text = "Marie is 28 years old and works as a researcher."
age = extract_age(text)

print(f"Extracted age: {age}")
print(f"Type: {type(age)}")
