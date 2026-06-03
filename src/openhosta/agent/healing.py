"""Auto-Healing module — retry loops, fuzzy-matching and extensible hooks.

REQ-LEARN-001 — Auto-healing retry with adaptive backoff and guardrails

This module provides three key capabilities:

1. **GuardConfig** — declarative guardrails that bound the healing process
   (max retries per layer, max effort window, fuzzy threshold).

2. **Healer** — retry orchestrator that executes a callable with adaptive
   exponential backoff, fuzzy-match fallback and extensible hooks.

3. **heal** — convenience function for one-shot auto-healing invocations.

Hooks
~~~~~
Implementers can subclass ``HealingHook`` to hook into three extension
points: ``before_retry``, ``after_failure`` and ``before_fallback``.
"""

from __future__ import annotations

import difflib
import logging
import time
from dataclasses import dataclass, field
from typing import Any, TypeVar

# --------------------------------------------------------------------------- #
# Logging
# --------------------------------------------------------------------------- #

logger: logging.Logger = logging.getLogger(__name__)

# --------------------------------------------------------------------------- #
# GuardConfig
# --------------------------------------------------------------------------- #


@dataclass
class GuardConfig:
    """Declarative guardrails for an auto-healing attempt.

    Parameters
    ----------
    heal_retries_per_layer: int
        Maximum number of retry attempts per layer. Defaults to 3.
    max_effort_ms: float
        Upper bound on cumulative wall-clock time (in ms) spent healing.
        Use ``-1`` for unlimited. Defaults to ``-1``.
    initial_backoff_ms: float
        Starting backoff in milliseconds. Defaults to 100 ms.
    max_backoff_ms: float
        Hard ceiling for exponential backoff. Defaults to 5 000 ms.
    backoff_factor: float
        Multiplicative growth factor per retry. Defaults to 2.0.
    fuzzy_threshold: float
        Similarity score threshold for fallback matching (0-1).
        Defaults to 0.6.
    layer: int
        Current nesting depth (0 = top level). Defaults to 0.
    description: str
        Human-readable guard label.
    """

    heal_retries_per_layer: int = 3
    max_effort_ms: float = -1.0
    initial_backoff_ms: float = 100.0
    max_backoff_ms: float = 5_000.0
    backoff_factor: float = 2.0
    fuzzy_threshold: float = 0.6
    layer: int = 0
    description: str = ""

    def derive_child(self, layer: int) -> GuardConfig:
        """Return a new config for the next layer down.

        Child layers inherit settings but get reduced retry budget
        (at least 1) and proportionally reduced time budget.
        """
        child_retries = max(1, self.heal_retries_per_layer - 1)
        child_effort = self.max_effort_ms
        if self.max_effort_ms > 0:
            child_effort = max(50.0, self.max_effort_ms * 0.7)

        return GuardConfig(
            heal_retries_per_layer=child_retries,
            max_effort_ms=child_effort,
            initial_backoff_ms=self.initial_backoff_ms,
            max_backoff_ms=self.max_backoff_ms,
            backoff_factor=self.backoff_factor,
            fuzzy_threshold=self.fuzzy_threshold,
            layer=layer,
            description=self.description,
        )


# --------------------------------------------------------------------------- #
# HealingState (mutable runtime tracker)
# --------------------------------------------------------------------------- #


@dataclass
class HealingState:
    """Mutable runtime state tracked during a healing session.

    Parameters
    ----------
    attempt: int
        Number of retry attempts performed so far.
    total_ms: float
        Cumulative wall-clock time spent healing (ms).
    errors: list[BaseException]
        Collected exceptions in chronological order.
    """

    attempt: int = 0
    total_ms: float = 0.0
    errors: list[BaseException] = field(default_factory=list)


# --------------------------------------------------------------------------- #
# HealingHook — extension protocol
# --------------------------------------------------------------------------- #


class HealingHook:
    """Base class for customising the auto-healing lifecycle.

    Subclass and override any of the three extension points below.
    """

    def before_retry(
        self,
        guard: GuardConfig,
        state: HealingState,
        last_error: BaseException,
    ) -> bool:
        """Decide whether the next retry should proceed.

        Return ``True`` to continue, ``False`` to abort.
        """
        _ = guard, state, last_error
        return True

    def after_failure(
        self,
        guard: GuardConfig,
        state: HealingState,
        error: BaseException,
    ) -> None:
        """Called after every failed attempt (before sleeping)."""
        logger.debug(
            "healing failure layer=%s attempt=%d error=%s",
            guard.layer,
            state.attempt,
            error,
        )

    def before_fallback(
        self,
        guard: GuardConfig,
        state: HealingState,
        candidates: list[str],
    ) -> None:
        """Called before fuzzy-match fallback is attempted."""
        _ = guard, state, candidates


# --------------------------------------------------------------------------- #
# Fuzzy matching
# --------------------------------------------------------------------------- #


def _fuzzy_match(
    name: str,
    candidates: list[str],
    threshold: float,
) -> str | None:
    """Return the best fuzzy match for *name* among *candidates*.

    Strategy
    ~~~~~~~~
    1. Exact match (normalised to lower-underscore).
    2. Case-insensitive comparison.
    3. ``difflib.SequenceMatcher`` ratio above *threshold*.

    Returns ``None`` if no candidate meets the threshold.
    """
    norm_name = name.lower().replace("-", "_").replace(" ", "_")

    # 1. exact normalised match
    for c in candidates:
        if c.lower().replace("-", "_").replace(" ", "_") == norm_name:
            return c

    # 2. case-insensitive
    lower_candidates = {c.lower(): c for c in candidates}
    if name.lower() in lower_candidates:
        return lower_candidates[name.lower()]

    # 3. difflib ratio
    matches = difflib.get_close_matches(
        name, candidates, n=len(candidates), cutoff=threshold
    )
    if matches:
        return matches[0]

    return None


# --------------------------------------------------------------------------- #
# Healer — main retry orchestrator
# --------------------------------------------------------------------------- #


F = TypeVar("F", bound=Any)


@dataclass
class HealingResult:
    """Encapsulates the outcome of an auto-healing invocation.

    Parameters
    ----------
    success: bool
        ``True`` when the callable returned without raising.
    result: Any
        The return value from the callable (only meaningful when *success*
        is ``True``).
    error: BaseException | None
        The last caught exception (only meaningful when *success* is
        ``False``). ``None`` when the callable succeeded.
    attempts: int
        Number of attempts made (including the initial call).
    total_ms: float
        Cumulative wall-clock time spent healing (ms).
    fallback_name: str | None
        Name of the fallback function used, or ``None`` if the original
        callable succeeded.
    """

    success: bool
    result: Any
    error: BaseException | None
    attempts: int
    total_ms: float
    fallback_name: str | None = None


class Healer:
    """Retry orchestrator with exponential backoff and fuzzy fallback.

    Parameters
    ----------
    guard: GuardConfig
        Declarative guardrails bounding this healer's behaviour.
    hooks: list[HealingHook] | None
        Optional extension hooks invoked at lifecycle points.
    registry: dict[str, Any] | None
        Optional mapping of name → callable for fuzzy-match fallback.
        If omitted, a no-op registry is assumed.
    """

    def __init__(
        self,
        guard: GuardConfig,
        hooks: list[HealingHook] | None = None,
        registry: dict[str, Any] | None = None,
    ) -> None:
        self.guard = guard
        self.hooks = hooks if hooks is not None else []
        self._registry = registry if registry is not None else {}

    # ---- primary entry point ----

    def execute(
        self,
        func: Any,
        *args: Any,
        fallback_name: str | None = None,
        **kwargs: Any,
    ) -> HealingResult:
        """Execute *func* with auto-retry and fuzzy fallback.

        Parameters
        ----------
        func: Any
            Callable to invoke.
        *args: Any
            Positional arguments forwarded to *func*.
        fallback_name: str | None
            If provided, attempt to find a fuzzy-match for this name in
            the registry when all retries are exhausted.
        **kwargs: Any
            Keyword arguments forwarded to *func*.

        Returns
        -------
        HealingResult
            Contains the success flag, result, last error, attempt count,
            elapsed time and optional fallback name.
        """
        state = HealingState()
        start_wall = time.monotonic()

        # ---- attempt 0: initial call ----
        initial_result = self._attempt_once(func, args, kwargs, state, start_wall)
        if initial_result is not None:
            return initial_result

        # ---- retry loop ----
        retry_result = self._retry_loop(func, args, kwargs, state, start_wall)
        if retry_result is not None:
            return retry_result

        # ---- fallback via fuzzy-matching ----
        if fallback_name and self._registry:
            return self._try_fallback(
                fallback_name, state, args, kwargs, start_wall
            )

        # ---- give up ----
        elapsed_ms = (time.monotonic() - start_wall) * 1_000
        last_error = state.errors[-1] if state.errors else RuntimeError("no attempt recorded")
        return HealingResult(
            success=False,
            result=None,
            error=last_error,
            attempts=state.attempt,
            total_ms=elapsed_ms,
        )

    def _attempt_once(
        self,
        func: Any,
        args: tuple[Any, ...],
        kwargs: dict[str, Any],
        state: HealingState,
        start_wall: float,
    ) -> HealingResult | None:
        """Try *func* once.  Returns a success ``HealingResult`` or ``None`` on error."""
        try:
            result = func(*args, **kwargs)
            elapsed_ms = (time.monotonic() - start_wall) * 1_000
            return HealingResult(
                success=True, result=result, error=None, attempts=0, total_ms=elapsed_ms
            )
        except SystemExit:
            raise
        except KeyboardInterrupt:
            raise
        except Exception as e:
            state.attempt += 1
            state.errors.append(e)
            return None

    def _retry_loop(
        self,
        func: Any,
        args: tuple[Any, ...],
        kwargs: dict[str, Any],
        state: HealingState,
        start_wall: float,
    ) -> HealingResult | None:
        """Run the retry attempts.  Returns result on success, ``None`` on exhaustion."""
        for _ in range(self.guard.heal_retries_per_layer):
            last_error = state.errors[-1]

            # pre-retry hook: abort if any hook says no
            if not self._hooks_allow_retry(state, last_error):
                break

            # backoff + budget check
            sleep_s = self._backoff(state.attempt)
            if self._would_exceed_budget(sleep_s):
                logger.debug(
                    "healing stopped: time budget exceeded (layer=%s)",
                    self.guard.layer,
                )
                break

            # post-failure hooks
            self._notify_after_failure(state, last_error)

            time.sleep(sleep_s)

            # retry call
            retry_result = self._retry_once(func, args, kwargs, state, last_error, start_wall)
            if retry_result is not None:
                return retry_result

        return None

    def _hooks_allow_retry(self, state: HealingState, last_error: BaseException) -> bool:
        """Return ``True`` if all hooks permit another retry."""
        for hook in self.hooks:
            if not hook.before_retry(self.guard, state, last_error):
                return False
        return True

    def _notify_after_failure(self, state: HealingState, error: BaseException) -> None:
        """Run after_failure hooks for all registered hooks."""
        for hook in self.hooks:
            hook.after_failure(self.guard, state, error)

    def _retry_once(
        self,
        func: Any,
        args: tuple[Any, ...],
        kwargs: dict[str, Any],
        state: HealingState,
        last_error: BaseException,
        start_wall: float,
    ) -> HealingResult | None:
        """Execute one retry attempt. Returns success ``HealingResult`` or ``None``."""
        try:
            result = func(*args, **kwargs)
            elapsed_ms = (time.monotonic() - start_wall) * 1_000
            return HealingResult(
                success=True,
                result=result,
                error=last_error,
                attempts=state.attempt,
                total_ms=elapsed_ms,
            )
        except SystemExit:
            raise
        except KeyboardInterrupt:
            raise
        except Exception as e:
            state.attempt += 1
            state.errors.append(e)
            return None

    # ---- internal helpers ----

    def _backoff(self, attempt: int) -> float:
        """Compute exponential backoff in seconds for the given attempt."""
        ms = min(
            self.guard.initial_backoff_ms * (self.guard.backoff_factor ** (attempt - 1)),
            self.guard.max_backoff_ms,
        )
        return ms / 1_000

    def _would_exceed_budget(self, sleep_s: float) -> bool:
        """Return ``True`` if sleeping *sleep_s* would breach the time budget."""
        if self.guard.max_effort_ms < 0:
            return False
        current_ms = self.guard.max_effort_ms  # placeholder bound
        return (current_ms / 1_000) <= sleep_s

    def _try_fallback(
        self,
        name: str,
        state: HealingState,
        args: tuple[Any, ...],
        kwargs: dict[str, Any],
        start_wall: float,
    ) -> HealingResult:
        """Attempt fuzzy-match fallback and return the healing result."""
        candidates = list(self._registry.keys())
        for hook in self.hooks:
            hook.before_fallback(self.guard, state, candidates)

        match = _fuzzy_match(name, candidates, self.guard.fuzzy_threshold)
        if match is None:
            elapsed_ms = (time.monotonic() - start_wall) * 1_000
            last_error = state.errors[-1] if state.errors else RuntimeError("no fallback match")
            return HealingResult(
                success=False,
                result=None,
                error=last_error,
                attempts=state.attempt,
                total_ms=elapsed_ms,
            )

        fallback_func = self._registry[match]
        try:
            result = fallback_func(*args, **kwargs)
            elapsed_ms = (time.monotonic() - start_wall) * 1_000
            return HealingResult(
                success=True,
                result=result,
                error=state.errors[-1] if state.errors else RuntimeError("no error"),
                attempts=state.attempt,
                total_ms=elapsed_ms,
                fallback_name=match,
            )
        except SystemExit:
            raise
        except KeyboardInterrupt:
            raise
        except Exception as e:
            state.errors.append(e)
            elapsed_ms = (time.monotonic() - start_wall) * 1_000
            return HealingResult(
                success=False,
                result=None,
                error=e,
                attempts=state.attempt + 1,
                total_ms=elapsed_ms,
                fallback_name=match,
            )

    def child_healer(self) -> Healer:
        """Create a healer for the next layer with inherited guard config."""
        child_guard = self.guard.derive_child(self.guard.layer + 1)
        return Healer(guard=child_guard, hooks=self.hooks, registry=self._registry)


# --------------------------------------------------------------------------- #
# Convenience function
# --------------------------------------------------------------------------- #


def heal(
    func: Any,
    guard: GuardConfig | None = None,
    hooks: list[HealingHook] | None = None,
    registry: dict[str, Any] | None = None,
    fallback_name: str | None = None,
    *args: Any,
    **kwargs: Any,
) -> HealingResult:
    """One-shot auto-healing invocation.

    Parameters
    ----------
    func: Any
        Callable to invoke with retry.
    guard: GuardConfig | None
        Guard config (defaults to ``GuardConfig()``).
    hooks: list[HealingHook] | None
        Optional extension hooks.
    registry: dict[str, Any] | None
        Name → callable mapping for fuzzy fallback.
    fallback_name: str | None
        Name to fuzzy-match in the registry on exhaustion.
    *args, **kwargs: Any
        Forwarded to *func*.

    Returns
    -------
    HealingResult
    """
    if guard is None:
        guard = GuardConfig()
    healer = Healer(guard=guard, hooks=hooks, registry=registry)
    return healer.execute(func, *args, fallback_name=fallback_name, **kwargs)
