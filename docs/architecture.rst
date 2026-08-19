Architecture
============

Overview
--------

``teksi_hooks`` is composed of several independent layers which transform
configuration into executable runtime behaviour.

::

    Configuration
           |
           v
        Parsers
           |
           v
         Models
           |
           v
        Resolvers
           |
           v
       Evaluators
           |
           v
       Capabilities
           |
           v
      Application

Hook execution builds on top of these same components.

::

    Application
           |
           v
      HookHandler
           |
           v
          Hook
           |
           v
      HookContext
           |
           v
      Capabilities


Components
----------

Models
^^^^^^

Models define the framework contracts and value objects.

Examples include:

* Rights definitions
* Validation definitions
* Findings
* Object identifiers (``Oid``)
* Capability contracts

Models are intentionally lightweight and independent of application-specific
implementations.

Parsers
^^^^^^^

Parsers convert external configuration into typed model definitions.

Examples include:

* RightsParser
* ProviderRightsParser
* WildcardRightsParser

Parsers validate structure but do not resolve inheritance, defaults or
cross-references.

Resolvers
^^^^^^^^^

Resolvers transform parsed definitions into fully resolved runtime
configurations.

Typical responsibilities include:

* Inheritance resolution
* Default application
* Rule expansion
* Cross-reference resolution

Evaluators
^^^^^^^^^^

Evaluators apply runtime logic against resolved definitions.

Examples include:

* Rights evaluation
* Validation evaluation
* State transition evaluation

Evaluators produce findings rather than directly modifying application state.

Capabilities
^^^^^^^^^^^^

Capabilities provide services to framework components and hooks.

Examples include:

* Metadata lookup
* Relationship resolution
* Persistence services
* Application integrations

The framework depends only on capability contracts and never on concrete
implementations.

HookContext
^^^^^^^^^^^

The hook context provides runtime access to:

* Parameters
* Logging
* Capabilities

It forms the boundary between the framework and the hosting application.

Hook
^^^^

A hook implements workflow logic and declares its required capabilities.

Hooks orchestrate framework functionality but should not construct services or
manage infrastructure.

HookHandler
^^^^^^^^^^^

The hook handler is responsible for:

* Loading hook modules
* Validating hook contracts
* Verifying capability requirements
* Executing hooks
* Managing hook lifecycle

Application
^^^^^^^^^^^

The hosting application composes the framework by:

* Providing capabilities
* Loading configuration
* Creating hook contexts
* Executing hooks
* Handling persistence and integration concerns

The framework itself does not depend on any specific business domain,
application, database or external service.
