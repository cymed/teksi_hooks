Capabilities
============

Overview
--------

Capabilities provide application-specific services to framework components and
hooks.

The framework depends on capability contracts rather than concrete
implementations. This allows applications to integrate databases, metadata
registries, relation lookup services and other infrastructure without creating
hard dependencies inside the framework.

::

    Application
          |
          v
    Capability
          |
          v
     Framework

Capabilities form the primary extension mechanism of ``teksi_hooks``.


Purpose
-------

Capabilities are used when framework components require information or
behaviour that depends on the hosting application.

Typical examples include:

* Metadata lookup
* Relationship lookup
* Persistence services
* External system integration
* Runtime configuration access

The framework itself does not know how these services are implemented.


Capability Contracts
--------------------

Capabilities define what functionality is available rather than how it is
implemented.

For example:

.. code-block:: python

    class MetadataCapability(
        Protocol,
    ):

        def class_metadata(
            self,
            class_id: str,
        ) -> ClassMetadata:
            ...

Framework components depend on the capability contract while the application
provides the concrete implementation.


Providing Capabilities
----------------------

Applications register capability implementations through the
``HookContext``.

.. code-block:: python

    context = HookContext(
        parameters={},
        logger=logger,
        capabilities={
            MetadataCapability: metadata_capability,
        },
    )

Hooks and services can then request the capability they need.


Accessing Capabilities
----------------------

Capabilities are retrieved from the runtime context.

.. code-block:: python

    metadata = context.capability(
        MetadataCapability,
    )

The framework validates capability requirements before hook execution.


Required Capabilities
---------------------

Hooks can explicitly declare required capabilities.

.. code-block:: python

    class Hook(HookBase):

        required_capabilities = frozenset(
            {
                MetadataCapability,
            },
        )

The hook handler verifies that all required capabilities are available before
execution begins.


When to Use a Capability
------------------------

A capability is appropriate when functionality depends on application-specific
data or infrastructure.

Examples:

* Looking up class metadata
* Resolving relationships
* Reading external configuration
* Persisting data
* Accessing a database
* Integrating external services

These concerns belong outside the framework core because they vary between
applications.


When Not to Use a Capability
----------------------------

Capabilities should not be used for functionality that can be represented as a
pure model, parser, resolver or evaluator.

Examples:

* Value objects
* Data models
* Configuration definitions
* Validation findings
* Pure business logic
* Stateless helper functions

Keeping these concerns outside capabilities helps maintain clear architectural
boundaries.


Design Principles
-----------------

Capabilities in ``teksi_hooks`` follow several principles:

* Depend on contracts, not implementations.
* Keep infrastructure concerns outside the framework core.
* Make dependencies explicit.
* Avoid global state.
* Support application-specific extensions.
* Remain independent of business domains.

This approach allows the framework to remain lightweight while supporting a
wide range of applications and deployment environments.
