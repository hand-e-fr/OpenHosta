from __future__ import annotations

all = (
    "is_pydantic_available"
    "is_torch_available"
)

is_pydantic_available = False
try:
    import pydantic
    is_pydantic_available = True
except ImportError:
    is_pydantic_available = False

is_torch_available = False
try:
    import torch
    is_torch_available = True
except ImportError:
    is_torch_available = False
