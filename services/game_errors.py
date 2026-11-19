"""Shared domain error types for the Game game and rewards services.

Split out of learning_game_service.py so services/game_rewards_service.py
can raise (and the router can translate) the same error types without the
two service modules importing each other.
"""

from __future__ import annotations


class GameGameError(Exception):
    """Base class for domain errors that API routes can translate."""


class ContentNotFoundError(GameGameError, KeyError):
    """The requested repository-backed content identifier does not exist."""


class LockedContentError(GameGameError, PermissionError):
    """The student has not yet met a content prerequisite."""


class InvalidStateError(GameGameError, RuntimeError):
    """The requested transition conflicts with already persisted state."""


class InvalidAnswerError(GameGameError, ValueError):
    """A submitted answer/profile is malformed."""
