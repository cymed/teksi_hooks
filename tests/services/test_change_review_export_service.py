from __future__ import annotations

from dataclasses import dataclass, field

from teksi_hooks.capabilities.review import (
    ChangeObjectProvider,
)
from teksi_hooks.exceptions import (
    Severity,
)
from teksi_hooks.models.canonical_object import (
    CanonicalObject,
    CanonicalObjectIdentity,
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


@dataclass(slots=True)
class FakeChangeObjectProvider(
    ChangeObjectProvider,
):
    old_objects: dict[
        tuple[
            str,
            str,
        ],
        CanonicalObject,
    ] = field(
        default_factory=dict,
    )

    new_objects: dict[
        tuple[
            str,
            str,
        ],
        CanonicalObject,
    ] = field(
        default_factory=dict,
    )

    def old_object(
        self,
        change: Change,
    ) -> CanonicalObject | None:
        return self.old_objects.get(
            (
                change.table_name,
                change.object_id,
            )
        )

    def new_object(
        self,
        change: Change,
    ) -> CanonicalObject | None:
        return self.new_objects.get(
            (
                change.table_name,
                change.object_id,
            )
        )


def test_change_review_export_service_groups_features_by_class() -> None:
    change = Change(
        table_name="reach",
        object_id="ch000000re000001",
        operation=ChangeOperation.UPDATE,
        old_values={
            "obj_id": "ch000000re000001",
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
                    classification=ChangeClassification.ALTERED_OBJECT,
                    permitted=True,
                ),
            )
        ],
    )

    service = ChangeReviewExportService(
        object_provider=FakeChangeObjectProvider(),
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

    assert feature.attributes["obj_id"] == "ch000000re000001"
    assert feature.attributes["is_created"] is False
    assert feature.attributes["is_altered"] is True
    assert feature.attributes["is_deleted"] is False

    assert feature.attributes["import_values"] == {
        "status": "new",
    }

    assert feature.attributes["canonical_values"] == {
        "obj_id": "ch000000re000001",
        "status": "new",
    }

    assert feature.attributes["unpermitted_values"] == {}
    assert feature.attributes["permission_findings"] == ()
    assert feature.attributes["validation_findings"] == ()


def test_change_review_export_service_created_feature_uses_import_values() -> None:
    change = Change(
        table_name="wastewater_structure",
        object_id="ch000000ws000001",
        operation=ChangeOperation.INSERT,
        old_values={},
        new_values={
            "obj_id": "ch000000ws000001",
            "status": "created",
        },
    )

    classified = ClassifiedChanges(
        created_objects=[
            ClassifiedChange(
                change=change,
                metadata=ChangeClassificationMetadata(
                    classification=ChangeClassification.CREATED_OBJECT,
                    permitted=True,
                ),
            )
        ],
    )

    service = ChangeReviewExportService(
        object_provider=FakeChangeObjectProvider(),
        geometry_attribute_names_by_class={},
    )

    features_by_class = service.export(
        classified,
    )

    feature = features_by_class["wastewater_structure"][0]

    assert feature.attributes["is_created"] is True
    assert feature.attributes["is_altered"] is False
    assert feature.attributes["is_deleted"] is False

    assert feature.attributes["import_values"] == {
        "obj_id": "ch000000ws000001",
        "status": "created",
    }

    assert feature.attributes["canonical_values"] == {
        "obj_id": "ch000000ws000001",
        "status": "created",
    }


def test_change_review_export_service_deleted_feature_uses_old_values() -> None:
    change = Change(
        table_name="reach",
        object_id="ch000000re000002",
        operation=ChangeOperation.DELETE,
        old_values={
            "obj_id": "ch000000re000002",
            "status": "deleted",
        },
        new_values={},
    )

    classified = ClassifiedChanges(
        deleted_objects=[
            ClassifiedChange(
                change=change,
                metadata=ChangeClassificationMetadata(
                    classification=ChangeClassification.DELETED_OBJECT,
                    permitted=True,
                ),
            )
        ],
    )

    service = ChangeReviewExportService(
        object_provider=FakeChangeObjectProvider(),
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
        "obj_id": "ch000000re000002",
        "status": "deleted",
    }


def test_change_review_export_service_uses_metadata_driven_geometry_attributes() -> (
    None
):
    change = Change(
        table_name="reach",
        object_id="ch000000re000003",
        operation=ChangeOperation.UPDATE,
        old_values={
            "obj_id": "ch000000re000003",
            "progression_geometry": ewkb_from_wkt("LINESTRING(0 0, 1 1)"),
            "status": "old",
        },
        new_values={
            "progression_geometry": ewkb_from_wkt("LINESTRING(0 0, 2 2)"),
            "status": "new",
        },
    )

    classified = ClassifiedChanges(
        altered_objects=[
            ClassifiedChange(
                change=change,
                metadata=ChangeClassificationMetadata(
                    classification=ChangeClassification.ALTERED_OBJECT,
                    permitted=True,
                ),
            )
        ],
    )

    service = ChangeReviewExportService(
        object_provider=FakeChangeObjectProvider(),
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
    change = Change(
        table_name="reach",
        object_id="ch000000re000004",
        operation=ChangeOperation.UPDATE,
        old_values={
            "obj_id": "ch000000re000004",
            "geom_fake": "not a real geometry attribute",
        },
        new_values={
            "geom_fake": "still not a real geometry attribute",
        },
    )

    classified = ClassifiedChanges(
        altered_objects=[
            ClassifiedChange(
                change=change,
                metadata=ChangeClassificationMetadata(
                    classification=ChangeClassification.ALTERED_OBJECT,
                    permitted=True,
                ),
            )
        ],
    )

    service = ChangeReviewExportService(
        object_provider=FakeChangeObjectProvider(),
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

    change = Change(
        table_name="reach",
        object_id="ch000000re000005",
        operation=ChangeOperation.UPDATE,
        old_values={
            "obj_id": "ch000000re000005",
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
                    classification=ChangeClassification.UNPERMITTED_CHANGE,
                    permitted=True,
                    validation_findings=(finding,),
                ),
            )
        ],
    )

    service = ChangeReviewExportService(
        object_provider=FakeChangeObjectProvider(),
        geometry_attribute_names_by_class={
            "reach": ("progression_geometry",),
        },
    )

    features_by_class = service.export(
        classified,
    )

    feature = features_by_class["reach"][0]

    assert feature.attributes["unpermitted_values"] == {
        "progression_geometry": ewkb_from_wkt("LINESTRING(0 0, 2 2)"),
    }

    assert feature.attributes["progression_geometry_changed"] is True
    assert feature.attributes["progression_geometry_changed_without_permission"] is True

    assert feature.attributes["validation_findings"] == (finding,)


def test_change_review_export_service_prefers_provider_objects_for_geometries() -> None:
    change = Change(
        table_name="reach",
        object_id="ch000000re000006",
        operation=ChangeOperation.UPDATE,
        old_values={
            "obj_id": "ch000000re000006",
            "progression_geometry": ewkb_from_wkt("LINESTRING(0 0, 1 1)"),
        },
        new_values={
            "progression_geometry": ewkb_from_wkt("LINESTRING(0 0, 2 2)"),
        },
    )

    old_object = CanonicalObject(
        identity=CanonicalObjectIdentity(
            class_id="reach",
            attributes={
                "obj_id": "ch000000re000006",
            },
        ),
        values={
            "obj_id": "ch000000re000006",
            "progression_geometry": ewkb_from_wkt("LINESTRING(10 10, 11 11)"),
        },
    )

    new_object = CanonicalObject(
        identity=CanonicalObjectIdentity(
            class_id="reach",
            attributes={
                "obj_id": "ch000000re000006",
            },
        ),
        values={
            "obj_id": "ch000000re000006",
            "progression_geometry": ewkb_from_wkt("LINESTRING(20 20, 21 21)"),
        },
    )

    classified = ClassifiedChanges(
        altered_objects=[
            ClassifiedChange(
                change=change,
                metadata=ChangeClassificationMetadata(
                    classification=ChangeClassification.ALTERED_OBJECT,
                    permitted=True,
                ),
            )
        ],
    )

    service = ChangeReviewExportService(
        object_provider=FakeChangeObjectProvider(
            old_objects={
                (
                    "reach",
                    "ch000000re000006",
                ): old_object,
            },
            new_objects={
                (
                    "reach",
                    "ch000000re000006",
                ): new_object,
            },
        ),
        geometry_attribute_names_by_class={
            "reach": ("progression_geometry",),
        },
    )

    features_by_class = service.export(
        classified,
    )

    feature = features_by_class["reach"][0]

    assert feature.geometries == {
        "progression_geometry": ewkb_from_wkt("LINESTRING(20 20, 21 21)"),
    }


def test_change_review_export_service_falls_back_to_change_values_when_provider_returns_none() -> (
    None
):
    change = Change(
        table_name="reach",
        object_id="ch000000re000007",
        operation=ChangeOperation.UPDATE,
        old_values={
            "obj_id": "ch000000re000007",
            "progression_geometry": ewkb_from_wkt("LINESTRING(0 0, 1 1)"),
        },
        new_values={
            "progression_geometry": ewkb_from_wkt("LINESTRING(0 0, 2 2)"),
        },
    )

    classified = ClassifiedChanges(
        altered_objects=[
            ClassifiedChange(
                change=change,
                metadata=ChangeClassificationMetadata(
                    classification=ChangeClassification.ALTERED_OBJECT,
                    permitted=True,
                ),
            )
        ],
    )

    service = ChangeReviewExportService(
        object_provider=FakeChangeObjectProvider(),
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


def test_change_review_export_service_deleted_feature_uses_provider_old_geometry() -> (
    None
):
    change = Change(
        table_name="reach",
        object_id="ch000000re000008",
        operation=ChangeOperation.DELETE,
        old_values={
            "obj_id": "ch000000re000008",
        },
        new_values={},
    )

    old_object = CanonicalObject(
        identity=CanonicalObjectIdentity(
            class_id="reach",
            attributes={
                "obj_id": "ch000000re000008",
            },
        ),
        values={
            "obj_id": "ch000000re000008",
            "progression_geometry": ewkb_from_wkt("LINESTRING(5 5, 6 6)"),
        },
    )

    classified = ClassifiedChanges(
        deleted_objects=[
            ClassifiedChange(
                change=change,
                metadata=ChangeClassificationMetadata(
                    classification=ChangeClassification.DELETED_OBJECT,
                    permitted=True,
                ),
            )
        ],
    )

    service = ChangeReviewExportService(
        object_provider=FakeChangeObjectProvider(
            old_objects={
                (
                    "reach",
                    "ch000000re000008",
                ): old_object,
            },
        ),
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
