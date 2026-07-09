import re

from dataclasses import dataclass

from ..utils.hooks.exceptions import TeksiHookError


_STANDARDOID_PATTERN = re.compile(r"^\w{16}$")


@dataclass(slots=True, frozen=True)
class Standardoid:
    value: str


    def __post_init__(self) -> None:
        if not _STANDARDOID_PATTERN.fullmatch(
            self.value,
        ):
            raise TeksiHookError(
                f"'{self.value}' is not a valid standardoid."
            )


    def __str__(self) -> str:
        return self.value