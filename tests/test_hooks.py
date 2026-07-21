import logging

import pytest

from teksi_hooks.hook import (
    HookBase,
    HookContext,
    HookHandler,
    HookMetadata,
)


class ExampleCapability:
    pass


def test_hook_context_returns_capability() -> None:
    capability = ExampleCapability()

    context = HookContext(
        parameters={},
        logger=logging.getLogger(__name__),
        capabilities={
            ExampleCapability: capability,
        },
    )

    assert context.capability(
        ExampleCapability,
    ) is capability


def test_hook_context_raises_key_error_for_missing_capability() -> None:
    context = HookContext(
        parameters={},
        logger=logging.getLogger(__name__),
        capabilities={},
    )

    with pytest.raises(KeyError):
        context.capability(
            ExampleCapability,
        )


def test_hook_metadata_stores_values() -> None:
    metadata = HookMetadata(
        name="Example hook",
        description="Does something useful.",
    )

    assert metadata.name == "Example hook"
    assert metadata.description == "Does something useful."