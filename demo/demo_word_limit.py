from OpenHosta import emulate, Validator, ValidationError, reload_dotenv

reload_dotenv()


class MaxWordsValidator(Validator):
    def validate_test(self, value: str) -> None:
        word_count = len(value.split())
        if word_count > 10:
            raise ValidationError(f"Summary has {word_count} words, maximum is 10")


def summarize_short(text: str) -> MaxWordsValidator:
    """Generate a summary with maximum 10 words."""
    return emulate()


# Test
article = """
Artificial intelligence is transforming healthcare through advanced diagnostic tools,
personalized treatment plans, and predictive analytics. Machine learning algorithms
can now detect diseases earlier than traditional methods, potentially saving lives.
"""

summary = summarize_short(article)

print(f"Summary: {summary}")
print(f"Word count: {len(summary.split())}")
