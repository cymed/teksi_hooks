from teksi_hooks.models.canonical_object import (
    CanonicalObjectIdentity,
)
from teksi_hooks.models.effects import (
    EffectDocument,
    EffectSource,
    UpdateAttributeEffect,
)
from teksi_hooks.services.diff_snapshot_builder import (
    DiffSnapshotBuilder,
)
from teksi_hooks.capabilities.relation_lookup import RelationLookupCapability

def test_build_snapshot_from_single_effect() -> None:
    builder = DiffSnapshotBuilder(relation_lookup=RelationLookupCapability)

    identity = CanonicalObjectIdentity(
        class_id="wastewater_structure",
        attributes={
            "obj_id": "ch000000ws000001",
        },
    )

    document = EffectDocument(
        version=1,
        source=EffectSource(
            model="ag64",
            class_id="GepKnoten",
            object_id="ch123456AG987654",
        ),
        effects=(
            UpdateAttributeEffect(
                identity=identity,
                attribute_id="status",
                value=1234,
            ),
        ),
    )

    snapshot = builder.build(
        document,
    )

    assert (
        len(
            snapshot.objects,
        )
        == 1
    )

    assert snapshot.objects[0].identity == identity


def test_build_snapshot_groups_effects_by_object() -> None:
    builder = DiffSnapshotBuilder(relation_lookup=RelationLookupCapability)

    identity = CanonicalObjectIdentity(
        class_id="wastewater_structure",
        attributes={
            "obj_id": "ch000000ws000001",
        },
    )

    document = EffectDocument(
        version=1,
        source=EffectSource(
            model="ag64",
            class_id="GepKnoten",
            object_id="ch123456AG987654",
        ),
        effects=(
            UpdateAttributeEffect(
                identity=identity,
                attribute_id="status",
                value=1,
            ),
            UpdateAttributeEffect(
                identity=identity,
                attribute_id="remark",
                value="test",
            ),
        ),
    )

    snapshot = builder.build(
        document,
    )

    assert (
        len(
            snapshot.objects,
        )
        == 1
    )

    assert (
        len(
            snapshot.effects,
        )
        == 2
    )


def test_build_snapshot_keeps_distinct_objects() -> None:
    builder = DiffSnapshotBuilder(relation_lookup=RelationLookupCapability)

    document = EffectDocument(
        version=1,
        source=EffectSource(
            model="ag64",
            class_id="GepKnoten",
            object_id="ch123456AG987654",
        ),
        effects=(
            UpdateAttributeEffect(
                identity=CanonicalObjectIdentity(
                    class_id="wastewater_structure",
                    attributes={
                        "obj_id": "object_1",
                    },
                ),
                attribute_id="status",
                value=1,
            ),
            UpdateAttributeEffect(
                identity=CanonicalObjectIdentity(
                    class_id="wastewater_structure",
                    attributes={
                        "obj_id": "object_2",
                    },
                ),
                attribute_id="status",
                value=1,
            ),
        ),
    )

    snapshot = builder.build(
        document,
    )

    assert (
        len(
            snapshot.objects,
        )
        == 2
    )


def test_build_snapshot_copies_metadata() -> None:
    builder = DiffSnapshotBuilder(relation_lookup=RelationLookupCapability)

    document = EffectDocument(
        version=1,
        source=EffectSource(
            model="ag64",
            class_id="GepKnoten",
            object_id="ch123456AG987654",
        ),
        effects=(),
    )

    snapshot = builder.build(
        document,
    )

    assert snapshot.metadata.source_model == "ag64"

    assert snapshot.metadata.source_class_id == "GepKnoten"

    assert snapshot.metadata.source_object_id == "ch123456AG987654"


def test_build_snapshot_initializes_without_last_modification() -> None:
    builder = DiffSnapshotBuilder(relation_lookup=RelationLookupCapability)

    document = EffectDocument(
        version=1,
        source=EffectSource(
            model="ag64",
            class_id="GepKnoten",
            object_id="ch123456AG987654",
        ),
        effects=(
            UpdateAttributeEffect(
                identity=CanonicalObjectIdentity(
                    class_id="wastewater_structure",
                    attributes={
                        "obj_id": "ch000000ws000001",
                    },
                ),
                attribute_id="status",
                value="active",
            ),
        ),
    )

    snapshot = builder.build(
        document,
    )

    assert (
        len(
            snapshot.objects,
        )
        == 1
    )

    assert snapshot.objects[0].last_modification is None
