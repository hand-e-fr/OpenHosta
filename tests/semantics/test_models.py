"""
Tests for SemanticModel in OpenHosta.semantics.models.
Verifies structure, extraction from text, and validation.
"""
import pytest
from typing import List
from dotenv import load_dotenv

load_dotenv()


class TestSemanticModelBasic:
    """Basic tests for SemanticModel definition and instantiation."""
    
    def test_model_definition(self):
        """Should be able to define a SemanticModel with type annotations."""
        from OpenHosta.semantics import SemanticModel, SemanticInt
        
        class User(SemanticModel):
            name: str
            age: SemanticInt
            
        assert "name" in User.__annotations__
        assert "age" in User.__annotations__
    
    def test_manual_instantiation(self):
        """Should be able to instantiate with kwargs."""
        from OpenHosta.semantics import SemanticModel, SemanticInt
        
        class User(SemanticModel):
            name: str
            age: SemanticInt
            
        u = User(name="Alice", age=30)
        assert u.name == "Alice"
        assert u.age == 30
        assert isinstance(u.age, int)


class TestSemanticModelCoherence:
    """Tests for SemanticModel.validate_coherence hook."""
    
    def test_validate_coherence_called(self):
        """validate_coherence should be available as a hook."""
        from OpenHosta.semantics import SemanticModel
        
        class CoherentModel(SemanticModel):
            value: int
            
            def validate_coherence(self):
                # This is just a hook, we check it exists
                pass
                
        m = CoherentModel(value=10)
        assert hasattr(m, 'validate_coherence')


class TestSemanticModelExtraction:
    """Tests for SemanticModel text extraction (requires LLM)."""
    
    @pytest.mark.skip(reason="Requires LLM call for extraction")
    def test_extract_from_text(self):
        """Should extract fields from raw text."""
        from OpenHosta.semantics import SemanticModel, SemanticInt
        
        class User(SemanticModel):
            name: str
            age: SemanticInt
            
        # This would trigger _extract_from_text
        u = User("Je m'appelle Alice et j'ai 30 ans")
        
        assert u.name == "Alice"
        assert u.age == 30


class TestSemanticModelSchema:
    """Tests for JSON schema generation."""
    
    def test_generate_extraction_schema(self):
        """Should generate a valid JSON schema for extraction."""
        from OpenHosta.semantics import SemanticModel, SemanticInt
        
        class User(SemanticModel):
            name: str
            age: SemanticInt
            
        schema = User._generate_extraction_schema()
        assert schema['type'] == 'object'
        assert 'name' in schema['properties']
        assert 'age' in schema['properties']
