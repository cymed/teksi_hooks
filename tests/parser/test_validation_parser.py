from __future__ import annotations

from teksi_hooks.exceptions import (
    Severity,
)
from teksi_hooks.models.validation import (
    AttributeValidation,
    ChangeOperation,
    ObjectValidation,
    ValidationDefinition,
)

AGXX_EXTENSION_CLASSES = frozenset(
    {
        "agxx_wastewater_networkelement",
        "agxx_last_modification",
        "agxx_wastewater_node",
        "agxx_wastewater_structure",
        "agxx_reach",
        "agxx_reach_point",
        "agxx_overflow",
        "agxx_building_group",
        "agxx_catchment_area_totals",
        "agxx_infiltration_zone",
    }
)


def test_validation_parser_parses_validation_definition(
    validation_definition: ValidationDefinition,
) -> None:
    default_mandatory_attributes = frozenset(
        {
            "obj_id",
            "identifier",
            "fk_provider",
            "fk_dataowner",
        }
    )

    default_attribute_validations = {
        "last_modification": (
            AttributeValidation(
                id="newer_than_existing",
                level=Severity.INFO,
                operations=(
                    ChangeOperation.INSERT,
                    ChangeOperation.UPDATE,
                    ChangeOperation.DELETE,
                ),
                context_value=None,
                parameters={},
            ),
        ),
        "fk_provider": (
            AttributeValidation(
                id="equals_context_value",
                level=Severity.ERROR,
                operations=(ChangeOperation.INSERT,),
                context_value="provider_oid",
                parameters={},
            ),
        ),
        "fk_dataowner": (
            AttributeValidation(
                id="equals_context_value",
                level=Severity.ERROR,
                operations=(ChangeOperation.INSERT,),
                context_value="dataowner_oid",
                parameters={},
            ),
        ),
    }

    default_object_validations = {
        "unique_identifier_combo": (
            ObjectValidation(
                id="is_unique",
                level=Severity.ERROR,
                operations=(
                    ChangeOperation.INSERT,
                    ChangeOperation.UPDATE,
                ),
                parameters={
                    "attributes": (
                        "identifier",
                        "fk_dataowner",
                    ),
                },
            ),
        ),
    }

    assert validation_definition.mandatory_attributes == default_mandatory_attributes
    assert validation_definition.mandatory_excluded_classes == AGXX_EXTENSION_CLASSES

    assert validation_definition.attribute_validations == default_attribute_validations
    assert (
        validation_definition.attribute_validation_excluded_classes
        == AGXX_EXTENSION_CLASSES
    )

    assert validation_definition.object_validations == default_object_validations
    assert (
        validation_definition.object_validation_excluded_classes
        == AGXX_EXTENSION_CLASSES
        | {
            "file",
        }
    )

    maintenance_event = validation_definition.classes["maintenance_event"]

    assert maintenance_event.class_id == "maintenance_event"
    assert maintenance_event.mandatory_attributes == frozenset()
    assert maintenance_event.attribute_validations == {}

    maintenance_event_object_validations = {
        "unique_identifier_combo": (
            ObjectValidation(
                id="is_unique",
                level=Severity.ERROR,
                operations=(
                    ChangeOperation.INSERT,
                    ChangeOperation.UPDATE,
                ),
                parameters={
                    "attributes": (
                        "identifier",
                        "fk_dataowner",
                        "time_point",
                    ),
                },
            ),
        ),
    }

    assert maintenance_event.object_validations == maintenance_event_object_validations

    assert (
        validation_definition.mandatory_for_class("maintenance_event")
        == default_mandatory_attributes
    )
    assert (
        validation_definition.attribute_validations_for_class("maintenance_event")
        == default_attribute_validations
    )
    assert (
        validation_definition.object_validations_for_class("maintenance_event")
        == maintenance_event_object_validations
    )

    file_definition = validation_definition.classes["file"]

    assert file_definition.class_id == "file"

    assert (
        validation_definition.mandatory_for_class("file")
        == default_mandatory_attributes
    )
    assert (
        validation_definition.attribute_validations_for_class("file")
        == default_attribute_validations
    )
    assert validation_definition.object_validations_for_class("file") == {
        "unique_identifier_combo": (
            ObjectValidation(
                id="is_unique",
                level=Severity.ERROR,
                operations=(
                    ChangeOperation.INSERT,
                    ChangeOperation.UPDATE,
                ),
                parameters={
                    "attributes": ("obj_id",),
                },
            ),
        ),
    }

    expected_agxx_mandatory_attributes = {
        "agxx_wastewater_networkelement": frozenset(
            {
                "fk_wastewater_networkelement",
            }
        ),
        "agxx_last_modification": frozenset(
            {
                "fk_element",
            }
        ),
        "agxx_wastewater_node": frozenset(
            {
                "fk_wastewater_node",
            }
        ),
        "agxx_wastewater_structure": frozenset(
            {
                "fk_wastewater_structure",
            }
        ),
        "agxx_reach": frozenset(
            {
                "fk_reach",
            }
        ),
        "agxx_reach_point": frozenset(
            {
                "fk_reach_point",
            }
        ),
        "agxx_overflow": frozenset(
            {
                "fk_overflow",
            }
        ),
        "agxx_building_group": frozenset(
            {
                "fk_building_group",
            }
        ),
        "agxx_catchment_area_totals": frozenset(
            {
                "fk_catchment_area_totals",
            }
        ),
        "agxx_infiltration_zone": frozenset(
            {
                "fk_infiltration_zone",
            }
        ),
    }

    for (
        class_id,
        expected_mandatory_attributes,
    ) in expected_agxx_mandatory_attributes.items():
        class_definition = validation_definition.classes[class_id]

        assert class_definition.class_id == class_id
        assert class_definition.mandatory_attributes == expected_mandatory_attributes

        assert (
            validation_definition.mandatory_for_class(class_id)
            == expected_mandatory_attributes
        )

        assert (
            validation_definition.object_validations_for_class(class_id)
            == class_definition.object_validations
        )

    agxx_last_modification_validations = {
        "ag64_last_modification": (
            AttributeValidation(
                id="newer_than_existing",
                level=Severity.INFO,
                operations=(
                    ChangeOperation.INSERT,
                    ChangeOperation.UPDATE,
                    ChangeOperation.DELETE,
                ),
                context_value=None,
                parameters={},
            ),
        ),
        "ag96_last_modification": (
            AttributeValidation(
                id="newer_than_existing",
                level=Severity.INFO,
                operations=(
                    ChangeOperation.INSERT,
                    ChangeOperation.UPDATE,
                    ChangeOperation.DELETE,
                ),
                context_value=None,
                parameters={},
            ),
        ),
    }

    for class_id in AGXX_EXTENSION_CLASSES:
        class_definition = validation_definition.classes[class_id]

        if class_id == "agxx_last_modification":
            assert (
                class_definition.attribute_validations
                == agxx_last_modification_validations
            )
            assert (
                validation_definition.attribute_validations_for_class(class_id)
                == agxx_last_modification_validations
            )
        else:
            assert class_definition.attribute_validations == {}
            assert validation_definition.attribute_validations_for_class(class_id) == {}

        assert class_definition.object_validations == {}
        assert validation_definition.object_validations_for_class(class_id) == {}
