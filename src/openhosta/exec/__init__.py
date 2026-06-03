"""V4 execution bridge — all public entry-points still in use.

- ``ask``, ``ask_async``, ``ask_stream``, ``ask_stream_async``  (ask.py)
- ``emulate``, ``emulate_async``                                 (emulate.py)
- ``emulate_variants``                                          (emulate_variants.py)
- ``closure``, ``closure_async``                                (closure.py)

Do NOT remove — these are re-exported by ``openhosta.__init__`` and
exercised by functional / manual tests.  Migration to V5 streaming
(phase 5A) adds ``AgentSession.get_stream()`` and
``AgentEngine.auto_body()`` as the new API surface.
"""
