# from __future__ import annotations

# import asyncio
# from  concurrent.futures import ThreadPoolExecutor
# from typing import Any, Dict

# from ..core.config import Model as SyncModel

# class Model(SyncModel):

#     def __init__(self, 
#         model: str = None, 
#         base_url: str = None, 
#         api_key: str = None, 
#         timeout: int = 30,
#         additionnal_headers: Dict[str, Any] = {},
#         max_workers:int = 5
#     ):
#         super().__init__(model, base_url, api_key, timeout, additionnal_headers)
#         self.max_workers = max_workers
#         self.async_executor = None

#     def __exit__(self):
#         if self.async_executor is not None:
#             self.async_executor.shutdown()

#     def get_executor(self):
#         if self.async_executor is None:
#             self.async_executor = ThreadPoolExecutor(max_workers=self.max_workers)
#         return self.async_executor

#     async def api_call_async(
#         self,
#         messages: list[dict[str, str]],
#         json_form: bool = True,
#         **llm_args
#     ) -> Dict:
#         thread = await asyncio.get_event_loop().run_in_executor(
#                 self.get_executor(),
#                 self.api_call,
#                 messages, json_form, **llm_args
#             )
#         return thread