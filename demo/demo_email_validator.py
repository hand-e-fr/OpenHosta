from OpenHosta import emulate, Validator, ValidationError, reload_dotenv

reload_dotenv()


class InriaEmailValidator(Validator):
    def validate_test(self, value: str) -> None:
        if "@inria.fr" not in value:
            raise ValidationError("Email must be from @inria.fr domain")


def extract_inria_email(text: str) -> InriaEmailValidator:
    """Extract the @inria.fr email address from the text."""
    return emulate()


# Test
text = "Contact Dr. Marie Dupont at marie.dupont@inria.fr for more information."
email = extract_inria_email(text)

print(f"Extracted email: {email}")
print(f"Type: {type(email)}")
