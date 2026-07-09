
A lightweight capability-based hook framework for the TEKSI ecosystem.

## Overview

teksi_hooks provides a generic mechanism for loading and executing Python hooks at runtime.

Hooks are regular Python files that implement a small contract consisting of:

- Hook metadata
- Required capabilities
- A single execution method

Applications provide capabilities through a `HookContext`, allowing hooks to access services without creating dependencies on specific implementations.

## Features

- Dynamic hook loading
- Contract validation
- Capability-based dependency injection
- Isolated hook execution
- Extensible architecture
- GPL2 compatible
- No dependency on QGIS
- No dependency on PostgreSQL
- No dependency on TEKSI domain models

## Example Hook

```python
from teksi_hooks.hook import (
    HookBase,
    HookContext,
    HookMetadata,
)


class Hook(HookBase):

    required_capabilities = frozenset()

    @property
    def metadata(self) -> HookMetadata:
        return HookMetadata(
            name="Example Hook",
            description="Example hook implementation.",
        )

    def run_hook(
        self,
        context: HookContext,
    ) -> None:
        context.logger.info(
            "Hello from a hook."
        )
```

## Hook Execution

```python
from teksi_hooks.hook import (
    HookContext,
    HookHandler,
)

context = HookContext(
    parameters={
        "name": "TEKSI",
    },
    logger=logger,
    capabilities={},
)

HookHandler(
    file="example_hook.py",
).run(
    context,
)
```

## Capabilities

Capabilities provide services to hooks.

Example:
```python
context = HookContext(
    parameters={},
    logger=logger,
    capabilities={
        SqlCapability: SqlCapability(connection),
    },
)
```

Access inside a hook

```python
sql = context.capability(
    SqlCapability,
)

```
## Architecture

```text
Application
      │
      ▼
 HookHandler
      │
      ▼
   Hook
      │
      ▼
 HookContext
      │
      ▼
Capabilities
```

### Components

#### Application

The hosting application is responsible for:

- Creating and configuring capabilities
- Constructing the `HookContext`
- Providing runtime parameters
- Executing hooks through `HookHandler`

The framework intentionally does not depend on any specific application, plugin, database schema, or business domain.

#### HookHandler

`HookHandler` is responsible for:

- Loading hook modules
- Validating hook contracts
- Verifying required capabilities
- Executing hooks
- Managing hook lifecycle and cleanup

#### Hook

A hook encapsulates a workflow or extension point.

Hooks:

- Declare metadata
- Declare required capabilities
- Implement business logic in `run_hook()`

Hooks should contain workflow logic but should not be responsible for creating services or managing application infrastructure.

#### HookContext

`HookContext` transports runtime information to hooks.

It contains:

- Parameters provided by the application
- A logger instance
- Registered capabilities

The context acts as the boundary between the framework and the hosting application.

#### Capabilities

Capabilities provide services to hooks.

Examples include:

- Database access
- INTERLIS import/export services
- Mail services
- Diff services
- Application-specific functionality

The framework treats capabilities as opaque objects and does not know their implementation details.

---

## Design Principles

- Explicit over implicit
- No global state
- Service-oriented design
- Framework does not know domain concepts
- Applications define capabilities
- Hooks define workflows

