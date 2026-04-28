from typing import overload, cast
import functools
# from openhosta import auto, emulate, formulate, use, Guarded, oh
from typing import TypeAlias, TypeVar, Any, Callable

T = TypeVar('T')

DefaultModel: TypeAlias = T
F = TypeVar('F', bound=Callable[..., Any])


@dataclass  
class GuardMetadata:  
    uncertainty: float = 0.0  
    time_consumed: float = 0.0  
    llm_logs: list[dict] = field(default_factory=list)  
    heal_traces: list[str] = field(default_factory=list)  
  
    def __add__(self, other: 'GuardMetadata') -> 'GuardMetadata':  
          """Permet l'agrégation facile des métadonnées."""  
          return GuardMetadata(  
              uncertainty=self.uncertainty + other.uncertainty,  
              time_consumed=self.time_consumed + other.time_consumed,  
              llm_logs=self.llm_logs + other.llm_logs,  
              heal_traces=self.heal_traces + other.heal_traces  
        )
from dataclasses import dataclass

from typing import Generic
class Guarded(Generic[T]):  
    """Le Proxy transparent (Zero-Collision Duck Typing)."""  
    def __init__(self, value: T, metadata: GuardMetadata):  
        self.__guard_value__ = value  
        self.__guard_data__ = metadata  
    
    def __getattr__(self, name: str) -> Any: return getattr(self.__guard_value__, name)  
    def __eq__(self, other: Any) -> bool:  
        if isinstance(other, Guarded): return self.__guard_value__ == other.__guard_value__  
        return self.__guard_value__ == other  
    def __hash__(self) -> int: return hash(self.__guard_value__)  
    def __repr__(self) -> str: return repr(self.__guard_value__)  


def guarded_to_python(obj:Guarded[Any]|Any) -> str:
    return ''

@dataclass  
class GuardConfig:  
    max_uncertainty: float = 1  
    max_effort_ms: int = 120000
    heal_retries_per_layer: int = 2
  

def unguard(guarded: Guarded[T]) -> T:
    ...
    
def guard(value: T, config:GuardConfig|None=None) -> Guarded[T]:
    ...

class HostaModel:
    def __init__(self, model:str, base_url:str, capabilities:set[str]):
    
    # 1. Signature pour le linter : Cas SANS parenthèses (@oh.auto_body)
    @overload
    def auto_body(self, func: F) -> F: ...

    # 2. Signature pour le linter : Cas AVEC parenthèses (@oh.auto_body(4, sd=3))
    @overload
    def auto_body(self, *args: Any, **kwargs: Any) -> Callable[[F], F]: ...

    # 3. Implémentation réelle (exécutée au runtime)
    def auto_body(self, *args: Any, **kwargs: Any) -> Any:
        
        def decorator(func: F) -> F:
            @functools.wraps(func)
            def wrapper(*f_args: Any, **f_kwargs: Any) -> Any:
                # --- Ta logique auto_body ici ---
                print(f"[Décorateur] arguments reçus -> args: {args}, kwargs: {kwargs}")
                
                # Appel de la fonction originale
                return func(*f_args, **f_kwargs)
            return cast(F, wrapper)

        # Vérification du cas 1 : appelé SANS parenthèses
        # S'il y a un seul argument positionnel, pas de kwargs, et que l'argument est appelable (la fonction)
        if len(args) == 1 and not kwargs and callable(args[0]):
            func = args[0]
            args = () # On vide les args pour que le wrapper ne croie pas que la fonction est un argument '4'
            return decorator(func)

        # Cas 2 : appelé AVEC parenthèses (avec ou sans arguments à l'intérieur)
        return decorator
    
    def emulate_body(self, *args: Any, **kwargs: Any) -> Any:
        
        def decorator(func: F) -> F:
            @functools.wraps(func)
            def wrapper(*f_args: Any, **f_kwargs: Any) -> Any:
                # --- Ta logique auto_body ici ---
                print(f"[Décorateur] arguments reçus -> args: {args}, kwargs: {kwargs}")
                
                # Appel de la fonction originale
                return func(*f_args, **f_kwargs)
            return cast(F, wrapper)

        # Vérification du cas 1 : appelé SANS parenthèses
        # S'il y a un seul argument positionnel, pas de kwargs, et que l'argument est appelable (la fonction)
        if len(args) == 1 and not kwargs and callable(args[0]):
            func = args[0]
            args = () # On vide les args pour que le wrapper ne croie pas que la fonction est un argument '4'
            return decorator(func)

        # Cas 2 : appelé AVEC parenthèses (avec ou sans arguments à l'intérieur)
        return decorator


    @overload
    def formulate_body(self, func: F) -> Guarded[F]: ...

    # 2. Signature pour le linter : Cas AVEC parenthèses (@oh.formulate_body(4, sd=3))
    @overload
    def formulate_body(self, *args: Any, **kwargs: Any) -> Callable[[F], F]: ...

    def formulate_body(self, *args: Any, **kwargs: Any) -> Any:
        

        def decorator(func: F) -> F:
            @functools.wraps(func)
            def wrapper(*f_args: Any, **f_kwargs: Any) -> Any:
                # --- Ta logique auto_body ici ---
                print(f"[Décorateur] arguments reçus -> args: {args}, kwargs: {kwargs}")
                
                # Appel de la fonction originale
                return func(*f_args, **f_kwargs)
            return cast(F, wrapper)

        # Vérification du cas 1 : appelé SANS parenthèses
        # S'il y a un seul argument positionnel, pas de kwargs, et que l'argument est appelable (la fonction)
        if len(args) == 1 and not kwargs and callable(args[0]):
            func = args[0]
            args = () # On vide les args pour que le wrapper ne croie pas que la fonction est un argument '4'
            return decorator(func)

        # Cas 2 : appelé AVEC parenthèses (avec ou sans arguments à l'intérieur)
        return decorator

    
   
import os
def envmodel():
    return HostaModel(
    base_url=os.environ.get("HOSTA_MODEL", "gpt-4.1"),
    model="gpt-4.1",
    capabilities={"logprobs", "streaming"}
)

@dataclass  
class GuardMetadata:  
    uncertainty: float = 0.0  
    time_consumed: float = 0.0  
    llm_logs: list[dict] = field(default_factory=list)  
    heal_traces: list[str] = field(default_factory=list)  
  
    def __add__(self, other: 'GuardMetadata') -> 'GuardMetadata':  
          """Permet l'agrégation facile des métadonnées."""  
          return GuardMetadata(  
              uncertainty=self.uncertainty + other.uncertainty,  
              time_consumed=self.time_consumed + other.time_consumed,  
              llm_logs=self.llm_logs + other.llm_logs,  
              heal_traces=self.heal_traces + other.heal_traces  
          )  
  
from typing import Any    
    
def guard_info(val:Guarded[Any]) -> GuardMetadata:
    ...