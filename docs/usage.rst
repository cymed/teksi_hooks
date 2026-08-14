Usage
=====

Overview
--------

``teksi_hooks`` provides a set of reusable framework components for:

* Parsing configuration
* Resolving definitions
* Evaluating rules
* Reporting findings
* Executing hooks

Applications compose these components through capabilities and runtime
configuration.


Creating a Hook
---------------

.. code-block:: python

    from teksi_hooks import (
        HookBase,
        HookContext,
        HookMetadata,
    )


    class Hook(HookBase):

        required_capabilities = frozenset()

        @property
        def metadata(
            self,
        ) -> HookMetadata:
            return HookMetadata(
                name="Example Hook",
                description="Example implementation.",
            )

        def run_hook(
            self,
            context: HookContext,
        ) -> None:
            context.logger.info(
                "Hello from a hook.",
            )


Executing a Hook
----------------

.. code-block:: python

    from teksi_hooks import (
        HookContext,
        HookHandler,
    )


    context = HookContext(
        parameters={},
        logger=logger,
        capabilities={},
    )

    HookHandler(
        file="example_hook.py",
    ).run(
        context,
    )


Working with Capabilities
-------------------------

Capabilities are application-provided services.

.. code-block:: python

    service = context.capability(
        MyCapability,
    )

Hooks may declare required capabilities.

.. code-block:: python

    class Hook(HookBase):

        required_capabilities = frozenset(
            {
                MyCapability,
            },
        )


Parsing Configuration
---------------------

Parsers convert external configuration into typed framework models.

.. code-block:: python

    from teksi_hooks.parser import (
        RightsParser,
    )


    rights = RightsParser().parse_file(
        "rights.yml",
    )

The parser validates document structure but does not resolve inheritance,
defaults or references.


Resolving Definitions
---------------------

Resolvers transform parsed definitions into runtime-ready models.

.. code-block:: python

    resolved_rights = rights_resolver.resolve(
        rights,
    )

Typical resolver responsibilities include:

* Applying defaults
* Resolving inheritance
* Resolving references
* Expanding derived rights


Evaluating Rules
----------------

Evaluators apply runtime logic and return findings.

.. code-block:: python

    findings = validation_evaluator.evaluate(
        change=change,
        resolved_rights=resolved_rights,
    )

Each finding contains a severity and a human-readable message.

.. code-block:: python

    Finding(
        severity=Severity.ERROR,
        message="Invalid transition.",
    )


Failing on Errors
-----------------

Framework findings can be converted into exceptions.

.. code-block:: python

    findings = validation_evaluator.evaluate(
        change=change,
        resolved_rights=resolved_rights,
    )

    TeksiHookError.raise_if_errors(
        findings,
    )

This raises a ``TeksiHookError`` when one or more findings have severity
``ERROR`` while allowing warnings and informational findings to continue.


Creating Framework Errors
-------------------------

Single errors can be created directly from a message.

.. code-block:: python

    raise TeksiHookError.from_message(
        "Provider OID is missing.",
    )

The framework automatically converts the message into an error-level
``Finding``.