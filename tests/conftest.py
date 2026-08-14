from pathlib import Path
from collections.abc import Mapping
import pytest


from teksi_hooks.models.oid import Standardoid
from teksi_hooks.models.rights import (
    RightsDefinition,
    ResolvedClassDefinition,
)
from teksi_hooks.parser.provider_rights_parser import ProviderRightsParser
from teksi_hooks.parser.rights_parser import RightsParser
from teksi_hooks.parser.model_mapping_parser import ModelMappingParser

from teksi_hooks.models.provider import Provider, ResolvedProvider
from teksi_hooks.models.mapping import ModelMapping

from teksi_hooks.capabilities.conditions import ConditionsCapability
from teksi_hooks.capabilities.rights import (
    RightsCapability,
    DerivedRightsCapability,
    SubclassRightsCapability,
)
from teksi_hooks.capabilities.privilege import ResolvedProviderCapability
from teksi_hooks.capabilities.validation import (
    ValidationRegistry,
)

from teksi_hooks.resolver.rights_resolver import RightsResolver
from teksi_hooks.resolver.provider_resolver import ProviderResolver


from teksi_hooks.evaluators.rights import RightsEvaluator

DATA_DIR = Path(__file__).parent / "parser/data"



@pytest.fixture
def rights_definition() -> RightsDefinition:
    return RightsParser().parse_file(
        DATA_DIR / "rights_parser_minimal.yaml",
    )


@pytest.fixture
def rights_definition_non_transitive() -> RightsDefinition:
    return RightsParser().parse_file(
        DATA_DIR / "rights_parser_minimal_non_transitive.yaml",
    )


@pytest.fixture
def providers() -> tuple[Provider, ...]:
    return ProviderRightsParser(oid_type=Standardoid).parse_file(
        DATA_DIR / "provider_rights_minimal.yaml",
    )


@pytest.fixture
def resolved_providers(
    providers: tuple[Provider, ...],
) -> dict[Standardoid, ResolvedProvider]:
    return ProviderResolver().resolve_all(
        providers,
    )


@pytest.fixture
def resolved_rights(
    rights_definition: RightsDefinition,
) -> Mapping[str, ResolvedClassDefinition]:
    return RightsResolver().resolve(
        rights_definition,
    )


@pytest.fixture
def agxx_mapping() -> ModelMapping:
    return ModelMappingParser().parse_file(
        DATA_DIR / "agxx_mapping_minimal.yaml",
    )


@pytest.fixture
def derived_rights(
    rights_definition,
):
    return RightsResolver().resolve_derived_rights_config(
        rights_definition,
    )


@pytest.fixture
def evaluator(
    resolved_rights,
    resolved_providers,
    relation_lookup,
):
    return RightsEvaluator(
        rights=RightsCapability(
            rights=resolved_rights,
        ),
        provider=ResolvedProviderCapability(
            provider=resolved_providers[Standardoid("ch000000geping01")],
        ),
        conditions=ConditionsCapability(),
        relation_lookup=relation_lookup,
        derived_rights=DerivedRightsCapability(
            rights=resolved_rights,
        ),
        subclass_rights=SubclassRightsCapability(
            rights=resolved_rights,
        ),
    )


@pytest.fixture
def registry() -> ValidationRegistry:
    return ValidationRegistry()
