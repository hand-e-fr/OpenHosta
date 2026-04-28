"""
Tests for OpenHosta.utils.gather_data module.

Two categories:
  1. Unit tests – plain coroutines (no LLM), fast, isolated.
  2. Functional tests – use emulate_async() with real LLM calls (marked slow).
"""

import asyncio
import pytest

from OpenHosta.utils.gather_data import (
    _Placeholder,
    _extract_tasks,
    _inject_results,
    gather_data_async,
    gather_data,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

async def fake_coro(value):
    """Trivial awaitable that returns *value*."""
    return value


async def slow_coro(seconds: float):
    """Awaitable that sleeps before returning."""
    await asyncio.sleep(seconds)
    return f"done-{seconds}"


# ===================================================================
#  1. UNIT TESTS – _Placeholder
# ===================================================================

class TestPlaceholder:
    def test_stores_index(self):
        p = _Placeholder(7)
        assert p.index == 7


# ===================================================================
#  2. UNIT TESTS – _extract_tasks
# ===================================================================

class TestExtractTasks:
    def test_plain_value_unchanged(self):
        tasks = []
        result = _extract_tasks("hello", tasks)
        assert result == "hello"
        assert tasks == []

    def test_awaitable_replaced(self):
        tasks = []
        coro = fake_coro(42)
        result = _extract_tasks(coro, tasks)
        assert isinstance(result, _Placeholder)
        assert result.index == 0
        assert len(tasks) == 1
        # cleanup
        tasks[0].close()

    def test_list_with_awaitables(self):
        tasks = []
        coro1 = fake_coro(1)
        coro2 = fake_coro(2)
        result = _extract_tasks([coro1, "static", coro2], tasks)
        assert isinstance(result, list)
        assert isinstance(result[0], _Placeholder)
        assert result[1] == "static"
        assert isinstance(result[2], _Placeholder)
        assert len(tasks) == 2
        for t in tasks:
            t.close()

    def test_dict_with_awaitables(self):
        tasks = []
        coro = fake_coro("v")
        result = _extract_tasks({"k": coro, "s": 1}, tasks)
        assert isinstance(result["k"], _Placeholder)
        assert result["s"] == 1
        assert len(tasks) == 1
        tasks[0].close()

    def test_tuple_with_awaitables(self):
        tasks = []
        coro = fake_coro(99)
        result = _extract_tasks((coro, "x"), tasks)
        assert isinstance(result, tuple)
        assert isinstance(result[0], _Placeholder)
        assert result[1] == "x"
        tasks[0].close()

    def test_nested_structures(self):
        tasks = []
        coro = fake_coro("deep")
        result = _extract_tasks({"a": [coro]}, tasks)
        assert isinstance(result["a"][0], _Placeholder)
        assert len(tasks) == 1
        tasks[0].close()


# ===================================================================
#  3. UNIT TESTS – _inject_results
# ===================================================================

class TestInjectResults:
    def test_placeholder_replaced(self):
        results = ["alpha", "beta"]
        assert _inject_results(_Placeholder(0), results) == "alpha"
        assert _inject_results(_Placeholder(1), results) == "beta"

    def test_plain_value_unchanged(self):
        assert _inject_results(42, []) == 42

    def test_list_injection(self):
        results = [10, 20]
        data = [_Placeholder(0), "fixed", _Placeholder(1)]
        out = _inject_results(data, results)
        assert out == [10, "fixed", 20]

    def test_dict_injection(self):
        results = ["resolved"]
        data = {"key": _Placeholder(0), "other": "static"}
        out = _inject_results(data, results)
        assert out == {"key": "resolved", "other": "static"}

    def test_tuple_injection(self):
        results = [100]
        data = (_Placeholder(0), "x")
        out = _inject_results(data, results)
        assert isinstance(out, tuple)
        assert out == (100, "x")

    def test_nested_injection(self):
        results = ["deep_val"]
        data = {"a": [_Placeholder(0)]}
        out = _inject_results(data, results)
        assert out == {"a": ["deep_val"]}


# ===================================================================
#  4. UNIT TESTS – gather_data_async
# ===================================================================

class TestGatherDataAsync:

    @pytest.mark.asyncio
    async def test_dict_simple(self):
        data = {"a": fake_coro(10), "b": fake_coro(20)}
        result = await gather_data_async(data)
        assert result["a"] == 10
        assert result["b"] == 20

    @pytest.mark.asyncio
    async def test_list_simple(self):
        data = [fake_coro("x"), fake_coro("y")]
        result = await gather_data_async(data)
        assert result == ["x", "y"]

    @pytest.mark.asyncio
    async def test_dict_nested_list(self):
        data = {"items": [fake_coro(1), fake_coro(2), "static"]}
        result = await gather_data_async(data)
        assert result["items"] == [1, 2, "static"]

    @pytest.mark.asyncio
    async def test_dict_nested_dict(self):
        data = {"outer": {"inner": fake_coro("nested")}}
        result = await gather_data_async(data)
        assert result["outer"]["inner"] == "nested"

    @pytest.mark.asyncio
    async def test_mixed_static_and_coroutine(self):
        data = {
            "dynamic": fake_coro("resolved"),
            "static": "plain",
            "number": 42,
        }
        result = await gather_data_async(data)
        assert result["dynamic"] == "resolved"
        assert result["static"] == "plain"
        assert result["number"] == 42

    @pytest.mark.asyncio
    async def test_empty_dict(self):
        data = {}
        result = await gather_data_async(data)
        assert result == {}

    @pytest.mark.asyncio
    async def test_empty_list(self):
        data = []
        result = await gather_data_async(data)
        assert result == []

    @pytest.mark.asyncio
    async def test_no_coroutines(self):
        data = {"a": 1, "b": "hello"}
        result = await gather_data_async(data)
        assert result == {"a": 1, "b": "hello"}

    @pytest.mark.asyncio
    async def test_batching(self):
        """Ensure batching with small batch_size still resolves all."""
        data = [fake_coro(i) for i in range(10)]
        result = await gather_data_async(data, batch_size=3)
        assert result == list(range(10))

    @pytest.mark.asyncio
    async def test_timeout(self):
        data = {"stuck": asyncio.sleep(10)}
        with pytest.raises(TimeoutError):
            await gather_data_async(data, max_delay=0.1)

    @pytest.mark.asyncio
    async def test_no_timeout(self):
        """max_delay=None should skip timeout wrapping."""
        data = {"fast": fake_coro("ok")}
        result = await gather_data_async(data, max_delay=None)
        assert result["fast"] == "ok"

    @pytest.mark.asyncio
    async def test_rejects_non_dict_non_list(self):
        with pytest.raises(TypeError):
            await gather_data_async("not a dict or list")

    @pytest.mark.asyncio
    async def test_rejects_int(self):
        with pytest.raises(TypeError):
            await gather_data_async(123)

    @pytest.mark.asyncio
    async def test_modifies_in_place(self):
        """The original dict reference should be mutated."""
        data = {"a": fake_coro("val")}
        returned = await gather_data_async(data)
        assert data is returned
        assert data["a"] == "val"

    @pytest.mark.asyncio
    async def test_list_modifies_in_place(self):
        data = [fake_coro(1), fake_coro(2)]
        returned = await gather_data_async(data)
        assert data is returned
        assert data == [1, 2]

    @pytest.mark.asyncio
    async def test_tuple_in_dict(self):
        data = {"t": (fake_coro("a"), "b")}
        result = await gather_data_async(data)
        assert result["t"] == ("a", "b")
        assert isinstance(result["t"], tuple)

    @pytest.mark.asyncio
    async def test_large_batch(self):
        """All 50 coroutines with default batch_size=30 → 2 batches."""
        data = {f"k{i}": fake_coro(i) for i in range(50)}
        result = await gather_data_async(data)
        for i in range(50):
            assert result[f"k{i}"] == i


# ===================================================================
#  5. UNIT TESTS – gather_data (sync wrapper)
# ===================================================================

class TestGatherDataSync:

    def test_dict_simple(self):
        data = {"a": fake_coro(10), "b": fake_coro(20)}
        gather_data(data)
        assert data["a"] == 10
        assert data["b"] == 20

    def test_list_simple(self):
        data = [fake_coro("x"), fake_coro("y")]
        gather_data(data)
        assert data == ["x", "y"]

    def test_nested_dict_in_list(self):
        data = [{"sub": fake_coro("val")}, fake_coro("top")]
        gather_data(data)
        assert data[0]["sub"] == "val"
        assert data[1] == "top"

    def test_batching_sync(self):
        data = [fake_coro(i) for i in range(7)]
        gather_data(data, batch_size=2)
        assert data == list(range(7))

    def test_timeout_sync(self):
        data = {"stuck": asyncio.sleep(10)}
        with pytest.raises(TimeoutError):
            gather_data(data, max_delay=0.1)

    def test_rejects_bad_type(self):
        with pytest.raises(TypeError):
            gather_data("oops")


# ===================================================================
#  6. SYNC-IN-ASYNC GUARD
# ===================================================================

class TestSyncInAsyncGuard:

    @pytest.mark.asyncio
    async def test_sync_gather_data_raises_in_async_context(self):
        """Calling the sync wrapper inside a running loop must raise."""
        with pytest.raises(RuntimeError, match="environnement asynchrone"):
            gather_data({"a": fake_coro(1)})


# ===================================================================
#  7. FUNCTIONAL TESTS – with emulate_async()  (require LLM)
# ===================================================================

@pytest.mark.slow
class TestGatherDataWithEmulate:
    """
    These tests call real LLM endpoints via emulate_async().
    They require proper .env configuration (API keys, model, etc.).
    Run with:  pytest -m slow  (or without -m to include them)
    """

    def test_gather_data_dict_with_emulate(self):
        """
        Mirrors the documentation example from parallel_processing.md § 2.
        Builds a dict mixing emulate_async coroutines and static data,
        then resolves everything with gather_data (sync).
        """
        from OpenHosta import emulate_async

        async def name_list(topic: str) -> list[str]:
            """Generates three names related to the topic."""
            return await emulate_async()

        async def first_name(person: str) -> str:
            """Returns the first name of the famous person."""
            return await emulate_async()

        async def alt_name(person: str) -> str:
            """Returns an alternative alias of the person."""
            return await emulate_async()

        my_data = {}
        my_data["A"] = name_list("Macron")
        my_data["B"] = [first_name("Trump"), alt_name("Trump")]
        my_data["C"] = "Static Data"

        gather_data(my_data, batch_size=10, max_delay=120)

        # A should be a list of strings
        assert isinstance(my_data["A"], list), f"Expected list, got {type(my_data['A'])}"
        assert len(my_data["A"]) > 0, "name_list should return a non-empty list"
        assert all(isinstance(n, str) for n in my_data["A"]), "All items in A should be strings"

        # B should be a list of two strings
        assert isinstance(my_data["B"], list)
        assert len(my_data["B"]) == 2
        assert all(isinstance(n, str) for n in my_data["B"]), "All items in B should be strings"

        # C is static
        assert my_data["C"] == "Static Data"

    def test_gather_data_async_with_emulate(self):
        """
        Same scenario but using gather_data_async directly in an async test.
        """
        from OpenHosta import emulate_async
        import asyncio

        async def capital_of(country: str) -> str:
            """Returns the capital city of the given country."""
            return await emulate_async()

        async def app():
            data = {
                "france": capital_of("France"),
                "germany": capital_of("Germany"),
                "static": "untouched",
            }

            return await gather_data_async(data, batch_size=5, max_delay=120)

        result = asyncio.run(app())

        assert "Paris" in result["france"], f"Expected Paris, got: {result['france']}"
        assert isinstance(result["germany"], str)
        assert len(result["germany"]) > 0
        assert result["static"] == "untouched"

    def test_gather_data_list_with_emulate(self):
        """
        Resolve a list of emulate_async coroutines via the sync API.
        """
        from OpenHosta import emulate_async

        async def sentiment(text: str) -> str:
            """Classify the sentiment of the text as 'positive', 'negative', or 'neutral'."""
            return await emulate_async()

        data = [
            sentiment("I love this product!"),
            sentiment("This is terrible."),
            sentiment("The weather is okay."),
        ]

        gather_data(data, batch_size=10, max_delay=120)

        assert all(isinstance(s, str) for s in data)
        assert len(data) == 3

    def test_gather_data_dataclass_with_emulate(self):
        """
        Mirrors the invoice extraction pattern from parallel_processing.md § 1,
        but resolved through gather_data instead of manual asyncio.gather.
        """
        from dataclasses import dataclass
        from OpenHosta import emulate_async

        @dataclass
        class InvoiceSender:
            company_name: str
            address: str
            city: str
            postal_code: str
            siret_number: str

        async def extract_sender(invoice_text: str) -> InvoiceSender:
            """
            Parses the invoice text to find the exact coordinates of the invoice sender.
            Does not extract the recipient!
            """
            return await emulate_async()

        invoice_1 = "From: ACME Corp Ltd. 12 rue de la Paix, Paris, 75000. SIRET: 123456789. Billed to: John Doe."
        invoice_2 = "Facture envoyée le 12 Mars. Expéditeur: BricoPro. 5 impasse des artisans, 69002 Lyon. N° SIRET : 987654321."

        data = [extract_sender(invoice_1), extract_sender(invoice_2)]

        gather_data(data, batch_size=10, max_delay=120)

        for item in data:
            assert isinstance(item, InvoiceSender), f"Expected InvoiceSender, got {type(item)}"
            assert len(item.company_name) > 0
            assert len(item.city) > 0
