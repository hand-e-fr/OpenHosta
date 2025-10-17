from OpenHosta import emulate, Validator, ValidationError, reload_dotenv

reload_dotenv()


class Top3Validator(Validator):
    def validate_test(self, value: list) -> None:
        if len(value) != 3:
            raise ValidationError(f"Must return exactly 3 items, got {len(value)}")


def extract_top_skills(text: str) -> Top3Validator:
    """Extract the top 3 skills mentioned in the text."""
    return emulate()


# Test
cv = """
John has expertise in Python, JavaScript, Docker, Kubernetes, React, and SQL.
He particularly excels in Python and Docker.
"""

skills = extract_top_skills(cv)

print(f"Top 3 skills: {skills}")
print(f"Type: {type(skills)}")
