from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import pytest

from teksi_hooks.capabilities.review import (
    ChangeObjectProvider,
    ReviewGeometryConverter,
)
from teksi_hooks.exceptions import (
    Severity,
)
from teksi_hooks.models.canonical_object import (
    CanonicalObject,
    CanonicalObjectIdentity,
)
from teksi_hooks.models.review import (
    ReviewGeometry,
    ReviewGeometryFamily,
)
from teksi_hooks.models.validation import (
    Change,
    ChangeClassification,
    ChangeClassificationMetadata,
    ChangeOperation,
    ClassifiedChange,
    ClassifiedChanges,
    ValidationFinding,
)
from teksi_hooks.services.change_review_export import (
    ChangeReviewExportService,
)

from ..helpers import ewkb_from_wkt


@dataclass(
    slots=True,
)
class FakeReviewGeometryConverter(
    ReviewGeometryConverter,
):
    """
    Convert test EWKB values using configured geometry families.
    """

    families: Mapping[
        tuple[
            str,
            str,
        ],
        ReviewGeometryFamily,
    ]

    def review_geometry(
        self,
        *,
        class_id: str,
        attribute_id: str,
        value: Any,
    ) -> ReviewGeometry:
        if not isinstance(
            value,
            bytes,
        ):
            raise TypeError("Test geometry values must be EWKB bytes.")

        return ReviewGeometry(
            ewkb=value,
            family=self.families[
                (
                    class_id,
                    attribute_id,
                )
            ],
        )


def _geometry_converter() -> FakeReviewGeometryConverter:
    return FakeReviewGeometryConverter(
        families={
            (
                "reach",
                "progression_geometry",
            ): ReviewGeometryFamily.LINE,
        },
    )


def _identity(
    *,
    class_id: str,
    object_id: str,
    identity_attribute: str = "obj_id",
) -> CanonicalObjectIdentity:
    """
    Return one single-attribute canonical identity.
    """

    return CanonicalObjectIdentity(
        class_id=class_id,
        attributes={
            identity_attribute: object_id,
        },
    )


def _change(
    *,
    class_id: str,
    object_id: str,
    operation: ChangeOperation,
    old_values: dict,
    new_values: dict,
    identity_attribute: str = "obj_id",
) -> Change:
    """
    Return one canonical change for use in review-export tests.
    """

    return Change(
        identity=_identity(
            class_id=class_id,
            object_id=object_id,
            identity_attribute=identity_attribute,
        ),
        operation=operation,
        old_values=old_values,
        new_values=new_values,
    )


@dataclass(
    slots=True,
)
class FakeChangeObjectProvider(
    ChangeObjectProvider,
):
    old_objects: dict[
        tuple,
        CanonicalObject,
    ] = field(
        default_factory=dict,
    )

    new_objects: dict[
        tuple,
        CanonicalObject,
    ] = field(
        default_factory=dict,
    )

    def old_object(
        self,
        change: Change,
    ) -> CanonicalObject | None:
        return self.old_objects.get(
            change.identity.key(),
        )

    def new_object(
        self,
        change: Change,
    ) -> CanonicalObject | None:
        return self.new_objects.get(
            change.identity.key(),
        )


def test_change_review_export_service_groups_features_by_class() -> None:
    change = _change(
        class_id="reach",
        object_id="ch000000re000001",
        operation=ChangeOperation.UPDATE,
        old_values={
            "status": "old",
        },
        new_values={
            "status": "new",
        },
    )

    classified = ClassifiedChanges(
        altered_objects=[
            ClassifiedChange(
                change=change,
                metadata=ChangeClassificationMetadata(
                    classification=(ChangeClassification.ALTERED_OBJECT),
                    permitted=True,
                ),
            )
        ],
    )

    service = ChangeReviewExportService(
        object_provider=FakeChangeObjectProvider(),
        geometry_converter=_geometry_converter(),
        geometry_attribute_names_by_class={},
    )

    features_by_class = service.export(
        classified,
    )

    assert set(
        features_by_class,
    ) == {
        "reach",
    }

    assert (
        len(
            features_by_class["reach"],
        )
        == 1
    )

    feature = features_by_class["reach"][0]

    assert feature.class_id == "reach"
    assert feature.object_id == "ch000000re000001"

    assert feature.attributes["identity"] == {
        "class_id": "reach",
        "attributes": {
            "obj_id": "ch000000re000001",
        },
    }

    assert feature.attributes["is_created"] is False

    assert feature.attributes["is_altered"] is True

    assert feature.attributes["is_deleted"] is False

    assert feature.attributes["import_values"] == {
        "status": "new",
    }

    assert feature.attributes["canonical_values"] == {
        "status": "new",
    }

    assert feature.attributes["unpermitted_values"] == {}

    assert feature.attributes["permission_findings"] == ()

    assert feature.attributes["validation_findings"] == ()


def test_change_review_export_service_created_feature_uses_import_values() -> None:
    change = _change(
        class_id="wastewater_structure",
        object_id="ch000000ws000001",
        operation=ChangeOperation.INSERT,
        old_values={},
        new_values={
            "status": "created",
        },
    )

    classified = ClassifiedChanges(
        created_objects=[
            ClassifiedChange(
                change=change,
                metadata=ChangeClassificationMetadata(
                    classification=(ChangeClassification.CREATED_OBJECT),
                    permitted=True,
                ),
            )
        ],
    )

    service = ChangeReviewExportService(
        object_provider=FakeChangeObjectProvider(),
        geometry_converter=_geometry_converter(),
        geometry_attribute_names_by_class={},
    )

    features_by_class = service.export(
        classified,
    )

    feature = features_by_class["wastewater_structure"][0]

    assert feature.attributes["identity"] == {
        "class_id": "wastewater_structure",
        "attributes": {
            "obj_id": "ch000000ws000001",
        },
    }

    assert feature.attributes["is_created"] is True

    assert feature.attributes["is_altered"] is False

    assert feature.attributes["is_deleted"] is False

    assert feature.attributes["import_values"] == {
        "status": "created",
    }

    assert feature.attributes["canonical_values"] == {
        "status": "created",
    }


def test_change_review_export_service_deleted_feature_uses_old_values() -> None:
    change = _change(
        class_id="reach",
        object_id="ch000000re000002",
        operation=ChangeOperation.DELETE,
        old_values={
            "status": "deleted",
        },
        new_values={},
    )

    classified = ClassifiedChanges(
        deleted_objects=[
            ClassifiedChange(
                change=change,
                metadata=ChangeClassificationMetadata(
                    classification=(ChangeClassification.DELETED_OBJECT),
                    permitted=True,
                ),
            )
        ],
    )

    service = ChangeReviewExportService(
        object_provider=FakeChangeObjectProvider(),
        geometry_converter=_geometry_converter(),
        geometry_attribute_names_by_class={},
    )

    features_by_class = service.export(
        classified,
    )

    feature = features_by_class["reach"][0]

    assert feature.attributes["is_created"] is False

    assert feature.attributes["is_altered"] is False

    assert feature.attributes["is_deleted"] is True

    assert feature.attributes["import_values"] == {}

    assert feature.attributes["canonical_values"] == {
        "status": "deleted",
    }


def test_change_review_export_service_uses_metadata_driven_geometry_attributes() -> (
    None
):
    change = _change(
        class_id="reach",
        object_id="ch000000re000003",
        operation=ChangeOperation.UPDATE,
        old_values={
            "progression_geometry": ReviewGeometry(
                ewkb=ewkb_from_wkt("LINESTRING(0 0, 1 1)"),
                family=ReviewGeometryFamily.LINE,
            ),
            "status": "old",
        },
        new_values={
            "progression_geometry": ReviewGeometry(
                ewkb=ewkb_from_wkt("LINESTRING(0 0, 2 2)"),
                family=ReviewGeometryFamily.LINE,
            ),
            "status": "new",
        },
    )

    classified = ClassifiedChanges(
        altered_objects=[
            ClassifiedChange(
                change=change,
                metadata=ChangeClassificationMetadata(
                    classification=(ChangeClassification.ALTERED_OBJECT),
                    permitted=True,
                ),
            )
        ],
    )

    service = ChangeReviewExportService(
        object_provider=FakeChangeObjectProvider(),
        geometry_converter=_geometry_converter(),
        geometry_attribute_names_by_class={
            "reach": ("progression_geometry",),
        },
    )

    features_by_class = service.export(
        classified,
    )

    feature = features_by_class["reach"][0]

    assert feature.geometries == {
        "progression_geometry": ewkb_from_wkt("LINESTRING(0 0, 2 2)"),
    }

    assert feature.attributes["progression_geometry_changed"] is True

    assert (
        feature.attributes["progression_geometry_changed_without_permission"] is False
    )


def test_change_review_export_service_ignores_geometry_like_names_not_in_metadata() -> (
    None
):
    change = _change(
        class_id="reach",
        object_id="ch000000re000004",
        operation=ChangeOperation.UPDATE,
        old_values={
            "geom_fake": "not a real geometry attribute",
        },
        new_values={
            "geom_fake": ("still not a real geometry attribute"),
        },
    )

    classified = ClassifiedChanges(
        altered_objects=[
            ClassifiedChange(
                change=change,
                metadata=ChangeClassificationMetadata(
                    classification=(ChangeClassification.ALTERED_OBJECT),
                    permitted=True,
                ),
            )
        ],
    )

    service = ChangeReviewExportService(
        object_provider=FakeChangeObjectProvider(),
        geometry_converter=_geometry_converter(),
        geometry_attribute_names_by_class={
            "reach": (),
        },
    )

    features_by_class = service.export(
        classified,
    )

    feature = features_by_class["reach"][0]

    assert feature.geometries == {}

    assert "geom_fake_changed" not in feature.attributes


def test_change_review_export_service_marks_rejected_geometry_change() -> None:
    finding = ValidationFinding(
        code="invalid_geometry",
        severity=Severity.ERROR,
        message="Geometry is invalid.",
        attribute_name="progression_geometry",
    )

    change = _change(
        class_id="reach",
        object_id="ch000000re000005",
        operation=ChangeOperation.UPDATE,
        old_values={
            "progression_geometry": ewkb_from_wkt("LINESTRING(0 0, 1 1)"),
        },
        new_values={
            "progression_geometry": ewkb_from_wkt("LINESTRING(0 0, 2 2)"),
        },
    )

    classified = ClassifiedChanges(
        unpermitted_changes=[
            ClassifiedChange(
                change=change,
                metadata=ChangeClassificationMetadata(
                    classification=(ChangeClassification.UNPERMITTED_CHANGE),
                    permitted=True,
                    validation_findings=(finding,),
                ),
            )
        ],
    )

    service = ChangeReviewExportService(
        object_provider=FakeChangeObjectProvider(),
        geometry_converter=_geometry_converter(),
        geometry_attribute_names_by_class={
            "reach": ("progression_geometry",),
        },
    )

    features_by_class = service.export(
        classified,
    )

    feature = features_by_class["reach"][0]

    assert feature.attributes["unpermitted_values"] == {}

    assert feature.attributes["progression_geometry_changed"] is True

    assert feature.attributes["progression_geometry_changed_without_permission"] is True

    assert feature.attributes["validation_findings"] == (finding,)


def test_change_review_export_service_prefers_provider_objects_for_geometries() -> None:
    identity = _identity(
        class_id="reach",
        object_id="ch000000re000006",
    )

    change = Change(
        identity=identity,
        operation=ChangeOperation.UPDATE,
        old_values={
            "progression_geometry": ewkb_from_wkt("LINESTRING(0 0, 1 1)"),
        },
        new_values={
            "progression_geometry": ewkb_from_wkt("LINESTRING(0 0, 2 2)"),
        },
    )

    old_object = CanonicalObject(
        identity=identity,
        values={
            "progression_geometry": ewkb_from_wkt("LINESTRING(10 10, 11 11)"),
        },
    )

    new_object = CanonicalObject(
        identity=identity,
        values={
            "progression_geometry": ewkb_from_wkt("LINESTRING(20 20, 21 21)"),
        },
    )

    classified = ClassifiedChanges(
        altered_objects=[
            ClassifiedChange(
                change=change,
                metadata=ChangeClassificationMetadata(
                    classification=(ChangeClassification.ALTERED_OBJECT),
                    permitted=True,
                ),
            )
        ],
    )

    service = ChangeReviewExportService(
        object_provider=FakeChangeObjectProvider(
            old_objects={
                identity.key(): old_object,
            },
            new_objects={
                identity.key(): new_object,
            },
        ),
        geometry_converter=_geometry_converter(),
        geometry_attribute_names_by_class={
            "reach": ("progression_geometry",),
        },
    )

    features_by_class = service.export(
        classified,
    )

    feature = features_by_class["reach"][0]

    assert feature.geometries == {
        "progression_geometry": ReviewGeometry(
            ewkb_from_wkt("LINESTRING(20 20, 21 21)"),
            family=ReviewGeometryFamily.LINE,
        )
    }


def test_change_review_export_service_falls_back_to_change_values_when_provider_returns_none() -> (
    None
):
    change = _change(
        class_id="reach",
        object_id="ch000000re000007",
        operation=ChangeOperation.UPDATE,
        old_values={
            "progression_geometry": ReviewGeometry(
                ewkb_from_wkt("LINESTRING(0 0, 1 1)"),
                family=ReviewGeometryFamily.LINE,
            )
        },
        new_values={
            "progression_geometry": ReviewGeometry(
                ewkb_from_wkt("LINESTRING(0 0, 2 2)"),
                family=ReviewGeometryFamily.LINE,
            )
        },
    )

    classified = ClassifiedChanges(
        altered_objects=[
            ClassifiedChange(
                change=change,
                metadata=ChangeClassificationMetadata(
                    classification=(ChangeClassification.ALTERED_OBJECT),
                    permitted=True,
                ),
            )
        ],
    )

    service = ChangeReviewExportService(
        object_provider=FakeChangeObjectProvider(),
        geometry_converter=_geometry_converter(),
        geometry_attribute_names_by_class={
            "reach": ("progression_geometry",),
        },
    )

    features_by_class = service.export(
        classified,
    )

    feature = features_by_class["reach"][0]

    assert feature.geometries == {
        "progression_geometry": ReviewGeometry(
            ewkb=ewkb_from_wkt("LINESTRING(0 0, 2 2)"),
            family=ReviewGeometryFamily.LINE,
        ),
    }


def test_change_review_export_service_deleted_feature_uses_provider_old_geometry() -> (
    None
):
    identity = _identity(
        class_id="reach",
        object_id="ch000000re000008",
    )

    change = Change(
        identity=identity,
        operation=ChangeOperation.DELETE,
        old_values={},
        new_values={},
    )

    old_object = CanonicalObject(
        identity=identity,
        values={
            "progression_geometry": ewkb_from_wkt("LINESTRING(5 5, 6 6)"),
        },
    )

    classified = ClassifiedChanges(
        deleted_objects=[
            ClassifiedChange(
                change=change,
                metadata=ChangeClassificationMetadata(
                    classification=(ChangeClassification.DELETED_OBJECT),
                    permitted=True,
                ),
            )
        ],
    )

    service = ChangeReviewExportService(
        object_provider=FakeChangeObjectProvider(
            old_objects={
                identity.key(): old_object,
            },
        ),
        geometry_converter=_geometry_converter(),
        geometry_attribute_names_by_class={
            "reach": ("progression_geometry",),
        },
    )

    feature = service.export(
        classified,
    )["reach"][0]

    assert feature.geometries == {
        "progression_geometry": ewkb_from_wkt("LINESTRING(5 5, 6 6)"),
    }


def test_change_review_export_service_preserves_relation_backed_identity() -> None:
    """
    Ensure review export does not reconstruct every identity as ``obj_id``.
    """

    change = _change(
        class_id="agxx_last_modification",
        object_id="ch000000ca000001",
        identity_attribute="fk_element",
        operation=ChangeOperation.UPDATE,
        old_values={
            "ag96_last_modification": "2025-01-01",
        },
        new_values={
            "ag96_last_modification": "2026-01-01",
        },
    )

    classified = ClassifiedChanges(
        altered_objects=[
            ClassifiedChange(
                change=change,
                metadata=ChangeClassificationMetadata(
                    classification=(ChangeClassification.ALTERED_OBJECT),
                    permitted=True,
                ),
            )
        ],
    )

    service = ChangeReviewExportService(
        object_provider=FakeChangeObjectProvider(),
        geometry_converter=_geometry_converter(),
        geometry_attribute_names_by_class={},
    )

    feature = service.export(
        classified,
    )["agxx_last_modification"][0]

    assert feature.object_id == "ch000000ca000001"

    assert feature.attributes["identity"] == {
        "class_id": "agxx_last_modification",
        "attributes": {
            "fk_element": "ch000000ca000001",
        },
    }

    assert feature.attributes["canonical_values"] == {
        "ag96_last_modification": "2026-01-01",
    }


def test_review_geometry_accepts_ewkb_and_family() -> None:
    ewkb = ewkb_from_wkt("LINESTRING(0 0, 1 1)")

    geometry = ReviewGeometry(
        ewkb=ewkb,
        family=ReviewGeometryFamily.LINE,
    )

    assert geometry.ewkb == ewkb
    assert geometry.family == ReviewGeometryFamily.LINE


def test_review_geometry_normalizes_bytearray() -> None:
    ewkb = ewkb_from_wkt("POINT(1 2)")

    geometry = ReviewGeometry(
        ewkb=bytearray(
            ewkb,
        ),
        family="point",
    )

    assert isinstance(
        geometry.ewkb,
        bytes,
    )

    assert geometry.family == ReviewGeometryFamily.POINT


def test_review_geometry_rejects_empty_ewkb() -> None:
    with pytest.raises(
        ValueError,
        match="must not be empty",
    ):
        ReviewGeometry(
            ewkb=b"",
            family=(ReviewGeometryFamily.POINT),
        )


def test_review_geometry_rejects_unknown_family() -> None:
    with pytest.raises(
        ValueError,
        match="family",
    ):
        ReviewGeometry(
            ewkb=ewkb_from_wkt("POINT(1 2)"),
            family="volume",
        )
