from __future__ import annotations

import abc
import dataclasses
import importlib.util
import inspect
import logging
import sys
import time
import uuid
from pathlib import Path
from typing import Any, TypeVar

from .exceptions import TeksiHookError


T = TypeVar("T")
logger = logging.getLogger(__name__)


@dataclasses.dataclass(slots=True, frozen=True)
class HookMetadata:
    """
    Describes a hook implementation.

    Metadata is used for validation, logging and user-facing diagnostics.
    """

    name: str = dataclasses.field(
        metadata={
            "doc": (
                "Human-readable hook name used in logs and diagnostics."
            )
        },
    )

    description: str = dataclasses.field(
        metadata={
            "doc": (
                "Short description of what the hook does."
            )
        },
    )


@dataclasses.dataclass(slots=True)
class HookContext:
    """
    Runtime context passed to hook implementations.

    The context contains user/configuration parameters, a logger and the
    capabilities available to the current hook run.
    """

    parameters: dict[str, Any] = dataclasses.field(
        default_factory=dict,
        metadata={
            "doc": (
                "Runtime parameters passed to the hook. These may come from "
                "configuration, command-line options or the calling workflow."
            )
        },
    )

    logger: logging.Logger = dataclasses.field(
        default_factory=lambda: logging.getLogger(__name__),
        metadata={
            "doc": (
                "Logger that hook implementations should use for runtime "
                "messages."
            )
        },
    )

    capabilities: dict[type[Any], Any] = dataclasses.field(
        default_factory=dict,
        metadata={
            "doc": (
                "Available capabilities keyed by their capability type. Hooks "
                "declare required capability types via `required_capabilities` "
                "and retrieve them with `capability(...)`."
            )
        },
    )

    def capability(
        self,
        capability_type: type[T],
    ) -> T:
        """
        Return a capability instance by type.

        Raises KeyError if the capability was not provided by the caller.
        """

        return self.capabilities[capability_type]


class HookBase(abc.ABC):
    """
    Base class for executable TEKSI hooks.

    Hook implementations must inherit from this class, provide metadata and
    implement `run_hook`.
    """

    required_capabilities: frozenset[type[Any]] = frozenset()

    @abc.abstractmethod
    def run_hook(
        self,
        context: HookContext,
    ) -> None:
        """
        Execute the hook.

        Hooks may use the supplied context to access parameters, logging and
        capabilities.
        """

        raise NotImplementedError(
            "The run_hook method must be implemented in the subclass."
        )

    @property
    @abc.abstractmethod
    def metadata(
        self,
    ) -> HookMetadata:
        """
        Return hook metadata.
        """

        raise NotImplementedError(
            "HookMetadata must be implemented in the subclass."
        )