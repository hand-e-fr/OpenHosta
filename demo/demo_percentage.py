from OpenHosta import emulate, Validator, ValidationError, reload_dotenv

reload_dotenv()


class PercentageValidator(Validator):
    def validate_test(self, value: int) -> None:
        if not 0 <= value <= 100:
            raise ValidationError(f"Percentage must be between 0 and 100, got {value}")


def estimate_completion(task_description: str) -> PercentageValidator:
    """Estimate task completion percentage (0-100)."""
    return emulate()


# Test
task = "Built the database schema and API, still need frontend and testing"
completion = estimate_completion(task)

print(f"Task completion: {completion}%")
print(f"Type: {type(completion)}")
