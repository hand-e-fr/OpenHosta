
import asyncio
import pytest
from unittest.mock import AsyncMock
from OpenHosta.asynchrone.batchdatacontext import BatchProxyDict, BatchDataContext, Placeholder

# --- Pour éviter "coroutine was never awaited" ---
async def fake_coro(value):
    return value

# --- Tests pour Placeholder ---
def test_placeholder_creation():
    ph = Placeholder(5)
    assert ph.task_index == 5

# --- Tests pour BatchProxyDict ---
def test_batchproxydict_setitem_awaitable():
    d = BatchProxyDict()
    d["key"] = fake_coro(42)
    assert isinstance(d["key"], Placeholder)
    assert d["key"].task_index == 0
    assert len(d._pending_tasks) == 1

def test_batchproxydict_setitem_nested_list():
    d = BatchProxyDict()
    d["key"] = [fake_coro(1), "fixed", fake_coro(2)]
    value = d["key"]
    assert isinstance(value, list)
    assert isinstance(value[0], Placeholder)
    assert value[1] == "fixed"
    assert isinstance(value[2], Placeholder)
    assert len(d._pending_tasks) == 2

def test_batchproxydict_setitem_nested_dict():
    d = BatchProxyDict()
    d["key"] = {"subkey": fake_coro("value")}
    value = d["key"]
    assert isinstance(value, dict)
    assert isinstance(value["subkey"], Placeholder)
    assert len(d._pending_tasks) == 1

@pytest.mark.asyncio
async def test_batchproxydict_resolve_simple():
    d = BatchProxyDict()
    d["a"] = fake_coro(10)
    d["b"] = fake_coro(20)
    await d._resolve(batch_size=5, max_delay=None)
    assert d["a"] == 10
    assert d["b"] == 20

@pytest.mark.asyncio
async def test_batchproxydict_resolve_nested():
    d = BatchProxyDict()
    d["data"] = {"users": [fake_coro("Alice"), fake_coro("Bob")]}
    await d._resolve(batch_size=5, max_delay=None)
    assert d["data"]["users"] == ["Alice", "Bob"]

@pytest.mark.asyncio
async def test_batchproxydict_resolve_timeout():
    d = BatchProxyDict()
    d["stuck"] = asyncio.sleep(10)
    with pytest.raises(TimeoutError):
        await d._resolve(batch_size=5, max_delay=0.1)

# --- Test pour BatchDataContext : erreur si 'with' en async ---
@pytest.mark.asyncio
async def test_batchdatacontext_sync_in_async_loop():
    context = BatchDataContext()
    with pytest.raises(RuntimeError, match="Utilisez 'async with'"):
        with context:
            pass  # On ne doit jamais arriver ici

# --- Tests pour BatchDataContext (Sync) ---
def test_batchdatacontext_sync():
    context = BatchDataContext(batch_size=2, max_delay=5)
    with context as data:
        data["result"] = fake_coro(99)
        data["list"] = [fake_coro(1), fake_coro(2)]

    # Après sortie du contexte, les valeurs sont résolues
    assert data["result"] == 99
    assert data["list"] == [1, 2]

# --- Tests pour BatchDataContext (Async) ---
@pytest.mark.asyncio
async def test_batchdatacontext_async():
    context = BatchDataContext(batch_size=2, max_delay=5)
    async with context as data:
        data["result"] = fake_coro(42)
        data["dict"] = {"x": fake_coro(100), "y": "static"}

    assert data["result"] == 42
    assert data["dict"]["x"] == 100
    assert data["dict"]["y"] == "static"