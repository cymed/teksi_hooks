import re

from dataclasses import dataclass, field

from .exceptions import TeksiHookError


_STANDARDOID_PATTERN = re.compile(
    r"^[A-Za-z0-9]{16}$",
)


@dataclass(slots=True, frozen=True)
class Standardoid:
    """
    Validated INTERLIS standard OID value.

    A Standardoid is represented as a 16-character word string. It is used as
    a stable identifier for TEKSI / INTERLIS objects, organizations and data
    owners.
    """

    value: str = field(
        metadata={
            "doc": (
                "Raw standard OID value. Must match the standardoid pattern "
                "`^[A-Za-z0-9]{16}$`, meaning exactly 16 word ASCII characters "
                "or digits."
            )
        },
    )

    def __post_init__(
        self,
    ) -> None:
        if not _STANDARDOID_PATTERN.fullmatch(
            self.value,
        ):
            raise TeksiHookError(
                f"'{self.value}' is not a valid standardoid."
            )

    def __str__(
        self,
    ) -> str:
        return self.value