import pytest
from typing import Literal
from dataclasses import dataclass
from OpenHosta import emulate

type RegimeMatrimonial = Literal["Marié", "PACS", "Concubin"]

@dataclass
class Family:
    name: str
    status: RegimeMatrimonial

def identify_family(document: str) -> Family:
    """
    Extract the family information from the given text.
    """
    return emulate()

@pytest.mark.asyncio
async def test_type_alias_literal():
    doc = "Jean et Marie sont liés par un PACS."
    result = identify_family(doc)
    assert isinstance(result, Family)
    assert result.status == "PACS"
    assert result.name == "Jean et Marie"
