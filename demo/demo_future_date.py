from OpenHosta import emulate, closure, Validator, ValidationError, reload_dotenv
from datetime import datetime

reload_dotenv()


class FutureDateValidator(Validator):
    def validate_test(self, value: str) -> None:
        current_day = datetime.now().date()
        judge = closure(
            "Is this date in the future (after current day : {current_day})? Answer only 'yes' or 'no': {date}",
            force_return_type=str
        )

        result = judge(date=value).lower().strip()

        if result != "yes":
            raise ValidationError(f"Date must be in the future: {value}")


def extract_deadline(text: str) -> FutureDateValidator:
    """Extract the deadline date from the text."""
    return emulate()


# Test
text = "The project deadline is set for March 15, 2026."
deadline = extract_deadline(text)

print(f"Deadline: {deadline}")
print("✓ Validated as future date")
