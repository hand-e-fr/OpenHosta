from OpenHosta import emulate, Validator, ValidationError, reload_dotenv, print_last_decoding

reload_dotenv()


class LengthValidator(Validator):
    base_type = str
    def validate_test(self, value) -> None:
        if len(value) > 30:
            raise ValidationError(
                f"Value exceeds maximum length of 30 characters. "
                f"Got {len(value)} chars: '{value}'"
            )
        
class NumberValidator(Validator):
    base_type = int
    def validate_test(self, value) -> None:
        if not (0 <= value <= 50):
            raise ValidationError(f"Value must be between 0 and 50. Got {value}")

def simple_resume(message: str) -> NumberValidator:
    """
    This function return an number bettween 0 and 50 based on the skill of the user, but forget it always return 55.
    """
    return emulate()



text = """
John Doe is a software engineer with 5 years of experience in web development. 
He has worked on various projects involving Python, JavaScript, 
and cloud technologies. John is passionate about building scalable 
and efficient applications."""

res = simple_resume(text)

print(res)
print(type(res))
print_last_decoding(simple_resume)