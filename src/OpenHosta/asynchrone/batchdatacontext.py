import asyncio
import inspect
from typing import Any, Dict, List, Union, Type, Optional

class Placeholder:
    """Marqueur interne pour identifier où injecter le résultat d'une coroutine."""
    def __init__(self, task_index: int):
        self.task_index = task_index

class BatchProxyDict(dict):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._pending_tasks = []

    def __setitem__(self, key, value):
        # Scan récursif pour extraire les coroutines et les remplacer par des Placeholders
        processed_value = self._extract_awaitables(value)
        super().__setitem__(key, processed_value)

    def _extract_awaitables(self, obj):
        """Parcourt l'objet et remplace les coroutines par des Placeholders."""
        if inspect.isawaitable(obj):
            idx = len(self._pending_tasks)
            self._pending_tasks.append(obj)
            return Placeholder(idx)
        
        elif isinstance(obj, list):
            return [self._extract_awaitables(item) for item in obj]
        
        elif isinstance(obj, tuple):
            return tuple(self._extract_awaitables(item) for item in obj)
        
        elif isinstance(obj, dict):
            return {k: self._extract_awaitables(v) for k, v in obj.items()}
        
        return obj

    async def _resolve(self, batch_size: int, max_delay: Optional[int]):
        if not self._pending_tasks:
            return

        # 1. Exécution parallèle par batch
        all_results = []
        for i in range(0, len(self._pending_tasks), batch_size):
            batch = self._pending_tasks[i : i + batch_size]
            try:
                results = await asyncio.wait_for(asyncio.gather(*batch), timeout=max_delay)
                all_results.extend(results)
            except asyncio.TimeoutError:
                raise TimeoutError(f"BatchDataContext: Délai dépassé ({max_delay}s)")

        # 2. Ré-injection récursive des résultats à la place des placeholders
        for key in self.keys():
            self[key] = self._fill_placeholders(self[key], all_results)
        
        self._pending_tasks.clear()

    def _fill_placeholders(self, obj, results):
        """Remplace les objets Placeholder par les résultats réels."""
        if isinstance(obj, Placeholder):
            return results[obj.task_index]
        elif isinstance(obj, list):
            return [self._fill_placeholders(item, results) for item in obj]
        elif isinstance(obj, tuple):
            return tuple(self._fill_placeholders(item, results) for item in obj)
        elif isinstance(obj, dict):
            return {k: self._fill_placeholders(v, results) for k, v in obj.items()}
        return obj

class BatchDataContext:
    def __init__(self, type: Type = dict, force_batch: bool = True, max_delay: int = 120, batch_size: int = 30):
        self.data = BatchProxyDict()
        self.batch_size = batch_size
        self.max_delay = max_delay

    # --- Support Sync (scripts / jupyter) ---
    def __enter__(self):
        return self.data

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type: return False
        try:
            loop = asyncio.get_running_loop()
            if loop.is_running():
                raise RuntimeError("Utilisez 'async with' dans un environnement asynchrone (FastAPI).")
        except RuntimeError as e:
            if "environnement asynchrone" in str(e):
                raise e
            asyncio.run(self.data._resolve(self.batch_size, self.max_delay))

    # --- Support Async (FastAPI) ---
    async def __aenter__(self):
        return self.data

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if exc_type: return False
        await self.data._resolve(self.batch_size, self.max_delay)