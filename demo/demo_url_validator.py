from OpenHosta import emulate, Validator, ValidationError, reload_dotenv
import re

reload_dotenv()


class ValidURLValidator(Validator):
    def validate_test(self, value: str) -> None:
        url_pattern = r'^https?://[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        if not re.match(url_pattern, value):
            raise ValidationError("Must be a valid HTTP/HTTPS URL")


def extract_website(text: str) -> ValidURLValidator:
    """Extract the website URL from the text."""
    return emulate()


# Test
text = "Visit our website at https://inria.fr for more details."
url = extract_website(text)

print(f"Extracted URL: {url}")
print(f"Type: {type(url)}")
