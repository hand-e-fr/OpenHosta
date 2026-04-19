import asyncio
import inspect
from typing import Any, Optional, Union, Dict, List

class _Placeholder:
    """Marqueur interne pour se souvenir d'où vient une coroutine."""
    def __init__(self, index: int):
        self.index = index

def _extract_tasks(obj: Any, tasks: list) -> Any:
    """Parcourt récursivement et remplace les coroutines par des Placeholders."""
    if inspect.isawaitable(obj):
        idx = len(tasks)
        tasks.append(obj)
        return _Placeholder(idx)
    elif isinstance(obj, list):
        return [_extract_tasks(item, tasks) for item in obj]
    elif isinstance(obj, tuple):
        return tuple(_extract_tasks(item, tasks) for item in obj)
    elif isinstance(obj, dict):
        return {k: _extract_tasks(v, tasks) for k, v in obj.items()}
    return obj

def _inject_results(obj: Any, results: list) -> Any:
    """Parcourt récursivement et remplace les Placeholders par les vrais résultats."""
    if isinstance(obj, _Placeholder):
        return results[obj.index]
    elif isinstance(obj, list):
        for i in range(len(obj)):
            obj[i] = _inject_results(obj[i], results)
        return obj
    elif isinstance(obj, tuple):
        return tuple(_inject_results(item, results) for item in obj)
    elif isinstance(obj, dict):
        for k in obj.keys():
            obj[k] = _inject_results(obj[k], results)
        return obj
    return obj

async def gather_data_async(data: Union[Dict, List], batch_size: int = 30, max_delay: Optional[int] = 120):
    """Version asynchrone pour FastAPI ou les boucles d'événements existantes."""
    tasks = []
    
    # 1. Extraction (modification temporaire in-place)
    if isinstance(data, dict):
        for k, v in data.items():
            data[k] = _extract_tasks(v, tasks)
    elif isinstance(data, list):
        for i, v in enumerate(data):
            data[i] = _extract_tasks(v, tasks)
    else:
        raise TypeError("gather_data ne supporte que les dictionnaires ou les listes à la racine.")

    if not tasks:
        return data

    # 2. Résolution par lots
    all_results = []
    for i in range(0, len(tasks), batch_size):
        batch = tasks[i : i + batch_size]
        try:
            if max_delay:
                batch_res = await asyncio.wait_for(asyncio.gather(*batch), timeout=max_delay)
            else:
                batch_res = await asyncio.gather(*batch)
            all_results.extend(batch_res)
        except asyncio.TimeoutError:
            raise TimeoutError(f"gather_data : Timeout de {max_delay}s dépassé.")

    # 3. Ré-injection in-place
    if isinstance(data, dict):
        for k in data.keys():
            data[k] = _inject_results(data[k], all_results)
    elif isinstance(data, list):
        for i in range(len(data)):
            data[i] = _inject_results(data[i], all_results)

    return data

def gather_data(data: Union[Dict, List], batch_size: int = 30, max_delay: Optional[int] = 120):
    """
    Version synchrone pour les scripts standards et les débutants.
    Modifie l'objet 'data' en place.
    """
    try:
        loop = asyncio.get_running_loop()
        if loop.is_running():
            raise RuntimeError(
                "Vous êtes dans un environnement asynchrone. Utilisez 'await gather_data_async(data)'."
            )
    except RuntimeError as e:
        if "environnement asynchrone" in str(e):
            raise e
        # Si aucune boucle ne tourne, on en crée une pour exécuter le travail
        asyncio.run(gather_data_async(data, batch_size, max_delay))