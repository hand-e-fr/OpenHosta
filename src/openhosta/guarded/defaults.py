"""Global guarded flags and constants."""

import os

ALLOW_CODE_EXECUTION: bool = os.environ.get(
    "OPENHOSTA_ALLOW_CODE_EXECUTION", "0"
) in ("1", "true", "yes")
