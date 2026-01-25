# Tests for OpenHosta Guarded Types

This directory contains comprehensive unit tests for the `guarded` module.

## Test Structure

- `test_scalars.py` - Tests for scalar types (GuardedInt, GuardedFloat, GuardedUtf8)
- `test_proxy_types.py` - Tests for proxy wrapper types (GuardedBool, GuardedNone, GuardedAny)
- `test_collections.py` - Tests for collection types (GuardedList, GuardedDict, GuardedSet, GuardedTuple)
- `test_enum.py` - Tests for GuardedEnum
- `test_dataclass.py` - Tests for @guarded_dataclass decorator
- `test_resolver.py` - Tests for TypeResolver and type_returned_data
- `conftest.py` - Pytest configuration and fixtures

## Running Tests

Run all tests:
```bash
pytest tests/guarded/
```

Run specific test file:
```bash
pytest tests/guarded/test_scalars.py
```

Run with verbose output:
```bash
pytest tests/guarded/ -v
```

Run with coverage:
```bash
pytest tests/guarded/ --cov=src.OpenHosta.guarded
```

## Test Coverage

The tests cover:
- ✅ Native type conversion
- ✅ String parsing (heuristic level)
- ✅ Metadata preservation (uncertainty, abstraction_level)
- ✅ Type operations (arithmetic, comparison, etc.)
- ✅ Edge cases and error handling
- ✅ ProxyWrapper behavior
- ✅ Collection operations
- ✅ Enum functionality
- ✅ Dataclass integration
- ✅ Type resolution

## Adding New Tests

When adding new guarded types, create corresponding test files following the existing patterns:

1. Import the type from the appropriate module
2. Create a test class for the type
3. Test native conversion, string parsing, and operations
4. Test metadata preservation
5. Test edge cases and error conditions
