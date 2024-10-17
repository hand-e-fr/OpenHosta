from typing import Any
import types
import weakref
import inspect

class MethodAttribute:
    def __init__(self):
        self.data = weakref.WeakKeyDictionary()

    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
        if obj not in self.data:
            bound_method = types.MethodType(obj.__class__.__dict__[self.name], obj)
            self.data[obj] = bound_method
        return self.data[obj]

    def __set_name__(self, owner, name):
        self.name = name

def attach_attribute(method, name:str, value:Any):
    print(method)
    # if not inspect.ismethod(method):
    #     raise ValueError("La méthode fournie n'est pas une méthode de classe")
    
    # func = method.__func__
    # print(func)
    
    # if not hasattr(func, '__attributes__'):
    #     func.__attributes__ = {}
    # func.__attributes__[name] = value

    # Créer un nouveau descripteur MethodAttribute si nécessaire
    # class_name = func.__qualname__.split('.')[0]
    # class_ = globals()[class_name]
    # if not isinstance(getattr(class_, func.__name__), MethodAttribute):
    #     setattr(class_, func.__name__, MethodAttribute(func))

    # Ajouter l'attribut à la méthode liée actuelle
    setattr(method, name, value)
    

class MyClass:
    def class_method(self):
        attach_attribute(MyClass.class_method ,"my_attribute", "World")

obj = MyClass()
obj.class_method()
print(obj.class_method.my_attribute)
