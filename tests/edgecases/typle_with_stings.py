# Les types tuple peuvent avoit du text sut plusieurs lignes. Qwen s'en sert et cela but OpenHosta v4.3.1
"""(MyEnum.VALUE1,
 "this is an explanation on"
 " multilpe lines in the 2nd element of the tuple."
 "This is valid python so it should be parsed correctly by the Guarded Type.")"""
 
assert False, "Tuples with multiple lines str are not yet supported. Use dtaclass instead."  