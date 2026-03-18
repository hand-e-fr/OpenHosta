"""Pytest configuration and fixtures for guarded tests."""

import pytest
import sys
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent.parent.parent / "src"
sys.path.insert(0, str(src_path))


@pytest.fixture
def sample_int():
    """Fixture providing a sample GuardedInt."""
    from src.OpenHosta.guarded.subclassablescalars import GuardedInt
    return GuardedInt(42)


@pytest.fixture
def sample_string():
    """Fixture providing a sample GuardedUtf8."""
    from src.OpenHosta.guarded.subclassablescalars import GuardedUtf8
    return GuardedUtf8("hello")


@pytest.fixture
def sample_list():
    """Fixture providing a sample GuardedList."""
    from src.OpenHosta.guarded.subclassablecollections import GuardedList
    return GuardedList([1, 2, 3])


@pytest.fixture
def sample_dict():
    """Fixture providing a sample GuardedDict."""
    from src.OpenHosta.guarded.subclassablecollections import GuardedDict
    return GuardedDict({"a": 1, "b": 2})


@pytest.fixture
def sample_enum():
    """Fixture providing a sample GuardedEnum."""
    from src.OpenHosta.guarded.subclassableclasses import GuardedEnum
    
    class Status(GuardedEnum):
        PENDING = "pending"
        ACTIVE = "active"
        DONE = "done"
    
    return Status
