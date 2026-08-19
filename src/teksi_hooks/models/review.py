from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class ReviewFeature:
    """
    Feature prepared for review artifact export.

    A ReviewFeature is not necessarily a database row. It is a review/export
    representation of a classified change.

    A review writer may turn this into any geospatial storage type that can
    hold its corresponding geometry types
    """

    class_id: str = field(
        metadata={
            "doc": ("Canonical class identifier represented by this review feature.")
        },
    )

    object_id: str = field(
        metadata={
            "doc": ("Canonical object identifier represented by this review feature.")
        },
    )

    attributes: dict[
        str,
        Any,
    ] = field(
        default_factory=dict,
        metadata={
            "doc": (
                "Canonical attribute values and review metadata attributes "
                "to be exported for this feature."
            )
        },
    )

    geometries: dict[
        str,
        Any,
    ] = field(
        default_factory=dict,
        metadata={
            "doc": (
                "Geometry values keyed by canonical geometry attribute name. "
                "Multiple geometry attributes are supported because some "
                "canonical classes may expose more than one geometry."
            )
        },
    )
