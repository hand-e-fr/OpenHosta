from OpenHosta import emulate, Validator, ValidationError, reload_dotenv

reload_dotenv()


class SafeTextValidator(Validator):
    def validate_test(self, value: str) -> None:
        try:
            from guardrails.hub import ToxicLanguage
            from guardrails import Guard

            guard = Guard().use(
                ToxicLanguage(threshold=0.5, validation_method="sentence", on_fail="exception")
            )

            guard.validate(value)

        except ImportError:
            print("Warning: guardrails-ai not installed, skipping toxic language check")
        except Exception as e:
            raise ValidationError(f"Content validation failed: {str(e)}")


def generate_feedback(product: str, rating: int) -> SafeTextValidator:
    """Generate product feedback based on rating (1-5 stars)."""
    return emulate()


# Test
feedback = generate_feedback(product="smartphone", rating=4)

print(f"Feedback: {feedback}")
print("✓ Validated as safe content")
