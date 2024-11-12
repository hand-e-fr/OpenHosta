from __future__ import annotations

all = (
    "is_pydantic"
    "is_torch"
)

is_pydantic = False
try:
    import pydantic
    is_pydantic = True
except ImportError:
    is_pydantic = False

is_torch = False
try:
    import torch
    is_torch = True
except ImportError:
    is_torch = False
