from abc import ABC, abstractmethod


class ValidationError(ValueError):
    """Raised when validation fails."""
    pass


class Validator(ABC):
    """
    Abstract base class for validated types.

    The validator validates a value after it has been parsed to its base type.
    The base type is inferred from the annotation of validate_test().
    """

    def __init__(self, value):
        """
        Initialize the validator with a value.

        Args:
            value: The value to validate (already parsed to base type)

        Raises:
            TypeError: If value doesn't match expected base type
            ValidationError: If validation fails
        """
        # Step 1: Get expected base type
        base_type = self._get_base_type()

        # Step 2: Check type (raise TypeError if wrong)
        if not isinstance(value, base_type):
            raise TypeError(
                f"{self.__class__.__name__} expects {base_type.__name__}, "
                f"got {type(value).__name__}"
            )

        # Step 3: Validate (raise ValidationError if invalid)
        self.validate_test(value)

        # Step 4: Store
        self.value = value

    @abstractmethod
    def validate_test(self, value) -> None:
        """
        Validate the value. Raise ValidationError if invalid.

        Args:
            value: The value to validate (already parsed to base type)

        Raises:
            ValidationError: If validation fails
        """
        raise NotImplementedError(
            "You must implement validate_test() in your Validator subclass"
        )

    def _get_base_type(self) -> type:
        """
        Get the base type from validate_test annotation.
        Falls back to str if no annotation found.

        Returns:
            The expected base type
        """
        import inspect

        try:
            # Get validate_test signature
            sig = inspect.signature(self.validate_test)

            # Get 'value' parameter annotation
            if 'value' in sig.parameters:
                annotation = sig.parameters['value'].annotation

                # If annotation exists and is not empty
                if annotation is not inspect.Parameter.empty:
                    return annotation
        except Exception:
            pass

        # Fallback: check for base_type class attribute
        if hasattr(self.__class__, 'base_type'):
            return self.__class__.base_type

        # Ultimate fallback: str
        return str

    def __repr__(self):
        return f"{self.__class__.__name__}({self.value!r})"

    def __str__(self):
        return str(self.value)
