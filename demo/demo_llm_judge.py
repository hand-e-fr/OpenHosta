from OpenHosta import emulate, closure, Validator, ValidationError, reload_dotenv

reload_dotenv()


class ProfessionalToneValidator(Validator):
    def validate_test(self, value: str) -> None:
        judge = closure(
            "Is this text written in a professional tone? Answer only 'yes' or 'no': {text}",
            force_return_type=str
        )

        result = judge(text=value).lower().strip()

        if result != "yes":
            raise ValidationError("Text must be written in a professional tone")


def write_professional_email(topic: str) -> ProfessionalToneValidator:
    """Write a professional email about the given topic."""
    return emulate()


# Test
email = write_professional_email("Request for meeting next week")

print(f"Email:\n{email}\n")
print("✓ Validated as professional")
