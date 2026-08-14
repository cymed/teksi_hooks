Rights Framework
================

Overview
--------

The rights framework provides a declarative mechanism for defining:

* Privileges
* CRUD permissions
* Ownership rules
* Conditional access rules
* Transition rules
* Validation rules
* Derived rights relationships

Rights definitions are configured using YAML and parsed into typed framework
models. The parser only converts configuration into model objects. Inheritance,
defaults, wildcard expansion and resolution are handled separately by the
resolver layer.

Design Goals
------------

The rights framework is designed around the following principles:

* Configuration over hard-coded logic
* Separation of parsing and resolution
* Typed runtime models
* Capability-driven integration
* Domain-independent implementation

Concepts
--------

Privilege
~~~~~~~~~

A privilege represents a named permission that may be assigned to users,
providers or roles.

Privileges are identified by a ``PrivilegeId`` and may provide localized
metadata.

Example:

.. code-block:: yaml

    privileges:
      DBW_WI:
        labels:
          de: Datenbewirtschafter Werkinformation
          fr: Gestionnaire cadastral

      DBW_GEP:
        labels:
          de: Datenbewirtschafter GEP-Themen
          fr: Gestionnaire PGEE

Class Definition
~~~~~~~~~~~~~~~~

Rights are defined per canonical class.

Example:

.. code-block:: yaml

    classes:

      - id: wastewater_structure

        create_rules:
          - privileges:
              - DBW_GEP

A class definition may contain:

* CRUD rules
* Attribute definitions
* Rights inheritance
* Derived rights relationships

CRUD Rules
~~~~~~~~~~

Rules controlling object-level access.

Supported operations:

* Create
* Read
* Update
* Delete

Example:

.. code-block:: yaml

    create_rules:
      - privileges:
          - DBW_GEP

    read_rules:
      - privileges:
          - DBW_WI

Conditional Rules
~~~~~~~~~~~~~~~~~

Rules may be constrained using local or remote conditions.

Example:

.. code-block:: yaml

    update_rules:
      - privileges:
          - DBW_GEP

        when:
          local:
            attribute: status
            in:
              - other.planned
              - other.calculation_alternative

Local Conditions
^^^^^^^^^^^^^^^^

A local condition evaluates attributes on the current object.

Example:

.. code-block:: yaml

    when:
      local:
        attribute: status
        equals: released

Remote Conditions
^^^^^^^^^^^^^^^^^

A remote condition evaluates attributes on related objects.

Example:

.. code-block:: yaml

    when:
      remote:
        relation: provider
        attribute: active
        equals: true

Ownership Rules
~~~~~~~~~~~~~~~

Ownership rules grant permissions based on ownership information stored on an
