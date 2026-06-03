from openhosta.semantics.semantic_set import SemanticSet 

def test():
    self = SemanticSet(axis="Règlement FEDIAF sur le perimètre Purina")
    from openhosta import print_last_prompt
    print_last_prompt(self.extend_classes_within_thematic)
    print_last_prompt(self.reformulate_as_exclusive_classes)
    self.print_frame()
    
    