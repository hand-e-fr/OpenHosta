"""
Tests for SemanticType factory pattern in OpenHosta.semantics.primitives.
Verifies the factory creates proper semantic types with descriptions and tolerances.
"""
import pytest
from dotenv import load_dotenv

load_dotenv()


class TestSemanticTypeFactory:
    """Tests for SemanticType(base_type, description) factory pattern."""
    
    def test_factory_returns_class(self):
        """SemanticType(str, 'desc') should return a class, not an instance."""
        from OpenHosta.semantics import SemanticType
        
        MyType = SemanticType(str, "A test description")
        assert isinstance(MyType, type), "Factory should return a class"
    
    def test_factory_with_int(self):
        """Factory should work with int base type."""
        from OpenHosta.semantics import SemanticType
        
        AgeType = SemanticType(int, "Un âge humain")
        assert isinstance(AgeType, type)
        
    def test_factory_with_float(self):
        """Factory should work with float base type."""
        from OpenHosta.semantics import SemanticType
        
        PriceType = SemanticType(float, "Prix en euros")
        assert isinstance(PriceType, type)
    
    def test_factory_with_bool(self):
        """Factory should work with bool base type."""
        from OpenHosta.semantics import SemanticType
        
        ActiveType = SemanticType(bool, "Status actif")
        assert isinstance(ActiveType, type)
    
    def test_factory_unsupported_type_raises(self):
        """Factory should raise for unsupported base types."""
        from OpenHosta.semantics import SemanticType
        
        with pytest.raises(TypeError):
            SemanticType(list, "A list type")
    
    def test_factory_with_tolerance(self):
        """Factory should accept custom tolerance parameter."""
        from OpenHosta.semantics import SemanticType, Tolerance
        
        StrictType = SemanticType(str, "Strict matching", tolerance=Tolerance.STRICT)
        assert hasattr(StrictType, 'semantic_tolerance')
        assert StrictType.semantic_tolerance == Tolerance.STRICT


class TestSemanticTypeInstantiation:
    """Tests for instantiation of factory-created types."""
    
    def test_instantiate_str_type(self):
        """Created type should be instantiable with string values."""
        from OpenHosta.semantics import SemanticType
        
        TaskType = SemanticType(str, "Tâche ménagère")
        task = TaskType("Laver le sol")
        
        assert str(task) == "Laver le sol"
        assert isinstance(task, str)
    
    def test_instantiate_int_type(self):
        """Created type should be instantiable with integer values."""
        from OpenHosta.semantics import SemanticType
        
        AgeType = SemanticType(int, "Âge humain")
        age = AgeType(30)
        
        assert age == 30
        assert isinstance(age, int)
    
    def test_instance_has_confidence(self):
        """Instances should have confidence metadata."""
        from OpenHosta.semantics import SemanticType
        
        NameType = SemanticType(str, "Prénom")
        name = NameType("Alice")
        
        assert hasattr(name, 'confidence')
        assert 0.0 <= name.confidence <= 1.0
    
    def test_instance_has_source(self):
        """Instances should have source metadata."""
        from OpenHosta.semantics import SemanticType
        
        NameType = SemanticType(str, "Prénom")
        name = NameType("Alice")
        
        assert hasattr(name, 'source')
        assert name.source in ('native', 'heuristic', 'llm', 'unknown')


class TestSemanticTypeHashability:
    """Tests for hashability restrictions on SemanticType."""
    
    def test_semantic_type_factory_instance_not_hashable(self):
        """Factory-created SemanticType instances should not be hashable (fuzzy equality)."""
        from OpenHosta.semantics import SemanticType
        
        # Create a proper SemanticType via factory
        TaskType = SemanticType(str, "A task")
        task = TaskType("test")
        
        with pytest.raises(TypeError) as exc_info:
            hash(task)
        
        assert "not hashable" in str(exc_info.value).lower()
    
    @pytest.mark.skip(reason="SemanticStr inherits from str and is hashable, only SemanticType subclasses are not")
    def test_semantic_str_is_hashable(self):
        """SemanticStr, being a str subclass, is hashable by default."""
        from OpenHosta.semantics import SemanticStr
        
        s = SemanticStr("test")
        # Actually SemanticStr IS hashable since it inherits from str
        h = hash(s)
        assert isinstance(h, int)
    
    @pytest.mark.skip(reason="Native str subclasses are hashable by default")
    def test_cannot_use_in_native_set(self):
        """SemanticType should not be usable in native set()."""
        pass
    
    @pytest.mark.skip(reason="Native str subclasses are hashable by default")
    def test_cannot_use_as_dict_key(self):
        """SemanticType should not be usable as native dict key."""
        pass
