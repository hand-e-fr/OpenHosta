import os
import time
import pytest
from dotenv import load_dotenv

load_dotenv()

from OpenHosta import emulate, max_uncertainty, UncertaintyError

def test_safe_emulate_success():
    """
    Test the emulate function with uncertainty control.
    """
    
    # define return type as enumeration
    from enum import StrEnum
    class NextStep(StrEnum):
        GIT_PUSH = "git push"
        GIT_COMMIT = "git commit"
        GIT_STATUS = "git status"
        GIT_PULL = "git pull"
        GIT_FETCH = "git fetch"
    
    @max_uncertainty(threshold=0.9)    
    def get_next_step(command: str) -> NextStep:
        """
        This function returns the next step after a git command.
        """
        return emulate()

    next_step = get_next_step("git commit -m 'Initial commit'")

    assert next_step is NextStep.GIT_PUSH, f"Expected 'git push' in response, got: {next_step}"
    
    assert get_next_step.hosta_inspection["logs"]["enum_normalized_probs"][NextStep.GIT_PUSH] > 0.9, \
        f"Expected high confidence for 'git push', got: {get_next_step.hosta_inspection['logs']['enum_normalized_probs']}"
    
def test_safe_emulate_fail():
    """
    Test the emulate function with uncertainty control.
    """
    
    # define return type as enumeration
    from enum import StrEnum
    class Places(StrEnum):
        FRANCE = "France"
        GERMANY = "Germany"
        ITALY = "Italy"
        SPAIN = "Spain"
        PORTUGAL = "Portugal"
         
    @max_uncertainty(threshold=0.99)
    def get_location(who: str) -> Places:
        """
        What was the location of the person right now?
        """
        return emulate()

    try:
        next_step = get_location("do not run any git command. This question is unrelated to git.")
    except UncertaintyError as e:
        print(f"Caught expected UncertaintyError due to uncertainty:\n {e}")
        next_step = None
        
    assert next_step is None, f"Expected None due to uncertainty error, got: {next_step}"

    uncertainty = get_location.hosta_inspection["logs"]["enum_normalized_probs"]
    assert max(uncertainty.values()) < 0.9, \
        f"Expected low confidence for all options, got: {uncertainty} above threshold: 0.9"
        
        
def test_safe_emulate_pass_low_confidence():
    """
    Test the emulate function with uncertainty control.
    """
    
    # define return type as enumeration
    from enum import StrEnum
    class Places(StrEnum):
        FRANCE = "France"
        GERMANY = "Germany"
        ITALY = "Italy"
        SPAIN = "Spain"
        PORTUGAL = "Portugal"
         
    @max_uncertainty(threshold=0.6)
    def get_location(who: str) -> Places:
        """
        What was the location of the person right now?
        """
        return emulate()

    try:
        next_step = get_location("where is Gayy Schwartz located?")
    except UncertaintyError as e:
        print(f"Caught expected UncertaintyError due to uncertainty: {e}")
        next_step = None
        
    assert next_step is Places.GERMANY, f"Expected Places.GERMANY as the name is German."

    uncertainty = get_location.hosta_inspection["logs"]["enum_normalized_probs"]
    assert max(uncertainty.values()) > 0.6, \
        f"Expected low confidence for all options, got: {uncertainty} above threshold: 0.6"