"""Add src/ to Python path for development runs (editable without pip install)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))
