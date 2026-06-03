"""Agent status enumeration — defines the lifecycle states of an agent session."""

from enum import Enum, auto


class AgentStatus(Enum):
    """State of an agent session within its lifecycle.

    Transitions follow a strict state machine defined in the module docstring
    of ``agent_session`` and ``agent_engine``.
    """

    IDLE = auto()
    """Created, ready, no work in progress."""

    RUNNING = auto()
    """Active execution (tool calls, inference, processing)."""

    PAUSED = auto()
    """Suspended by user request; state preserved for later resumption."""

    WAITING = auto()
    """Waiting for external input (human-in-the-loop)."""

    TERMINATED = auto()
    """Finished normally (success)."""

    FAILED = auto()
    """Encountered a non-recoverable error."""

    TIMED_OUT = auto()
    """Execution exceeded the allowed timeout."""

    # ---- Transition helpers ----

    @staticmethod
    def valid_transitions() -> dict["AgentStatus", list["AgentStatus"]]:
        """Return the allowed state transitions.

        Returns
        -------
        dict[AgentStatus, list[AgentStatus]]
            Mapping from source status to list of allowed target statuses.
        """
        return {
            AgentStatus.IDLE: [AgentStatus.RUNNING],
            AgentStatus.RUNNING: [
                AgentStatus.IDLE,
                AgentStatus.PAUSED,
                AgentStatus.WAITING,
                AgentStatus.TERMINATED,
                AgentStatus.FAILED,
                AgentStatus.TIMED_OUT,
            ],
            AgentStatus.PAUSED: [AgentStatus.RUNNING, AgentStatus.TERMINATED],
            AgentStatus.WAITING: [AgentStatus.RUNNING, AgentStatus.FAILED],
            AgentStatus.TERMINATED: [],  # Terminal, no transitions
            AgentStatus.FAILED: [],  # Terminal, no transitions
            AgentStatus.TIMED_OUT: [],  # Terminal, no transitions
        }

    def can_transition_to(self, target: "AgentStatus") -> bool:
        """Check whether transitioning from *self* to *target* is valid.

        Parameters
        ----------
        target: AgentStatus
            The proposed next state.

        Returns
        -------
        bool
            ``True`` if the transition is allowed, ``False`` otherwise.
        """
        allowed = self.valid_transitions().get(self, [])
        return target in allowed

    @property
    def is_terminal(self) -> bool:
        """Return ``True`` if this status is a terminal state."""
        return self in (
            AgentStatus.TERMINATED,
            AgentStatus.FAILED,
            AgentStatus.TIMED_OUT,
        )

    @property
    def is_active(self) -> bool:
        """Return ``True`` if this status represents an active (non-terminal) state."""
        return not self.is_terminal

    @property
    def is_suspended(self) -> bool:
        """Return ``True`` if the session is paused or waiting."""
        return self in (AgentStatus.PAUSED, AgentStatus.WAITING)
