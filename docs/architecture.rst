Architecture
============

Overview
--------

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

Application
^^^^^^^^^^^

The hosting application creates capabilities, builds the hook context and executes hooks.

HookHandler
^^^^^^^^^^^

Responsible for loading, validating and executing hooks.

Hook
^^^^

A hook implements workflow logic and declares its required capabilities.

HookContext
^^^^^^^^^^^

Provides runtime parameters, logging and capabilities.

Capabilities
^^^^^^^^^^^^

Capabilities provide services to hooks. The framework itself does not know or enforce domain concepts.

Design Principles
-----------------

* Explicit over implicit
* No global state
* Service-oriented design
* Framework does not know domain concepts
* Applications define capabilities
* Hooks define workflows
