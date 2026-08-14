OID Types
=========

Overview
--------

Object identifiers (OIDs) are used throughout the framework to uniquely
identify domain objects, organizations, providers and data owners.

The framework defines a generic ``Oid`` contract and allows applications to
provide concrete implementations appropriate for their environment.

This design keeps the framework independent of any specific identifier format.


Oid
---

``Oid`` is the abstract base type for all framework object identifiers.

Concrete implementations define their own validation rules while exposing a
consistent API.

.. code-block:: python

    oid: Oid

The framework depends on ``Oid`` rather than on specific implementations.


Standardoid
-----------

``Standardoid`` is the default INTERLIS-compatible OID implementation.

A Standardoid consists of a 16-character alphanumeric identifier.

Example:

.. code-block:: python

    oid = Standardoid(
        "ch000000geping01",
    )

    print(
        oid.value,
    )

Invalid values raise a ``TeksiHookError``.

.. code-block:: python

    Standardoid(
        "invalid",
    )


Using OIDs
----------

Framework models reference ``Oid`` rather than concrete implementations.

.. code-block:: python

    @dataclass(
        frozen=True,
        slots=True,
    )
    class Provider:

        organisation_oid: Oid

This allows the application to choose the concrete identifier type while
keeping framework models unchanged.


Configuring OID Types
---------------------

Parsers and services that create identifiers accept a concrete OID type.

Example:

.. code-block:: python

    parser = ProviderRightsParser(
        oid_type=Standardoid,
    )

The parser validates all parsed identifiers using the supplied OID
implementation.


Creating Custom OID Types
-------------------------

Applications may provide their own OID implementation by inheriting from
``Oid``.

Example:

.. code-block:: python

    @dataclass(
        frozen=True,
        slots=True,
    )
    class UuidOid(Oid):

        _pattern = re.compile(
            r"...",
        )

Custom implementations automatically integrate with framework parsers,
resolvers, evaluators and services as long as they derive from ``Oid``.


Design Principles
-----------------

* Framework components depend on ``Oid`` rather than concrete implementations.
* Applications select the OID implementation that matches their environment.
* Validation is performed by the OID implementation itself.
* OIDs are immutable value objects.
* The framework is independent of INTERLIS-specific identifier formats.