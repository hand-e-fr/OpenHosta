from __future__ import annotations

all = (
    "is_pydantic"
)

is_pydantic = False
try:
    import pydantic
    is_pydantic = True
except ImportError:
    is_pydantic = False
