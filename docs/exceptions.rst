Exceptions and Findings
=======================

Overview
--------

The framework uses structured findings and typed exceptions to communicate
validation issues, evaluation failures and runtime errors.

Unlike traditional error handling based solely on strings, TEKSI framework
errors are backed by findings that provide machine-readable severity levels and
human-readable messages.

Core Concepts
-------------

Findings
~~~~~~~~

A finding represents an individual issue discovered during validation,
evaluation or resolution.

Each finding contains:

* A severity level
* A human-readable message

Example:

.. code-block:: python

    Finding(
        severity=Severity.ERROR,
        message="Provider does not match context provider.",
    )

Severity
~~~~~~~~

Severity levels indicate the importance of a finding.

The framework provides three severity levels:

.. code-block:: python

    Severity.INFO
    Severity.WARNING
    Severity.ERROR

Severity values:

* ``info``

  Informational message. Processing may continue.

* ``warning``

  Unexpected or undesirable condition. Processing may continue.

* ``error``

  Invalid state or operation. Processing should fail.

Example:

.. code-block:: python

    Finding(
        severity=Severity.WARNING,
        message="Attribute value is deprecated.",
    )

Framework Exception Hierarchy
-----------------------------

The exception hierarchy is rooted at:

.. code-block:: text

    TeksiHookException
    └── TeksiHookError
        ├── ValidationError
        │   ├── EffectValidationError
        │   └── SnapshotValidationError
        └── RightsEvaluationError

TeksiHookException
~~~~~~~~~~~~~~~~~~

Base class for all framework exceptions.

Applications may catch this exception to handle any TEKSI-related failure.

Example:

.. code-block:: python

    try:
        ...
    except TeksiHookException:
        ...

TeksiHookError
~~~~~~~~~~~~~~

Base class for framework failures backed by findings.

A ``TeksiHookError`` aggregates one or more findings and exposes them through
the ``findings`` attribute.

Example:

.. code-block:: python

    raise TeksiHookError(
        (
            Finding(
                severity=Severity.ERROR,
                message="Invalid provider.",
            ),
        ),
    )

Accessing Findings
^^^^^^^^^^^^^^^^^^

The findings that caused the exception remain available.

Example:

.. code-block:: python

    try:
        ...
    except TeksiHookError as error:
        for finding in error.findings:
            print(
                finding.message,
            )

Raising Errors from Findings
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The framework provides a convenience method for raising exceptions when error
findings are present.

Example:

.. code-block:: python

    TeksiHookError.raise_if_errors(
        findings,
    )

Only findings with severity ``ERROR`` result in an exception.

ValidationError
~~~~~~~~~~~~~~~

Base class for validation-related failures.

Validation errors indicate that runtime data, configuration or framework
objects violate defined constraints.

Example:

.. code-block:: python

    raise ValidationError(
        findings,
    )

EffectValidationError
~~~~~~~~~~~~~~~~~~~~~

Raised when an effect configuration is invalid.

Examples include:

* Contradictory effects
* Invalid effect definitions
* Unsupported effect combinations

Example:

.. code-block:: python

    raise EffectValidationError(
        findings,
    )

SnapshotValidationError
~~~~~~~~~~~~~~~~~~~~~~~

Raised when snapshot validation fails.

Examples include:

* Missing identifiers
* Invalid snapshot state
* Inconsistent object state

Example:

.. code-block:: python

    raise SnapshotValidationError(
        findings,
    )

RightsEvaluationError
~~~~~~~~~~~~~~~~~~~~~

Raised when rights evaluation cannot be completed.

Examples include:

* Invalid rights configuration
* Unresolvable privilege references
* Missing ownership information
* Unsupported evaluation scenarios

Example:

.. code-block:: python

    raise RightsEvaluationError(
        findings,
    )

Using Findings Instead of Strings
---------------------------------

Framework components should prefer findings over unstructured error messages.

Preferred:

.. code-block:: python

    Finding(
        severity=Severity.ERROR,
        message="Unknown privilege 'DBW_XYZ'.",
    )

Avoid:

.. code-block:: python

    raise Exception(
        "Unknown privilege.",
    )

Using findings provides:

* Severity classification
* Aggregation of multiple issues
* Consistent reporting
* Better UI integration
* Future localization opportunities

Aggregated Errors
-----------------

A single exception may contain multiple findings.

Example:

.. code-block:: python

    raise ValidationError(
        (
            Finding(
                severity=Severity.ERROR,
                message="Unknown privilege.",
            ),
            Finding(
                severity=Severity.ERROR,
                message="Unknown class definition.",
            ),
        ),
    )

The exception message is generated from all finding messages.

This allows validators and evaluators to report all discovered errors rather
than stopping at the first failure.

Typical Workflow
----------------

.. code-block:: text

    Validation
         │
         ▼
      Findings
         │
         ▼
    raise_if_errors()
         │
         ▼
    TeksiHookError
         │
         ▼
      Caller

Design Principles
-----------------

The exception system is designed around the following principles:

* Structured error reporting
* Aggregation of related issues
* Explicit severity levels
* Consistent framework-wide behaviour
* Separation between findings and exception handling

Related Components
------------------

* ``Finding``
* ``Severity``
* ``TeksiHookException``
* ``TeksiHookError``
* ``ValidationError``
* ``EffectValidationError``
* ``SnapshotValidationError``
* ``RightsEvaluationError``
