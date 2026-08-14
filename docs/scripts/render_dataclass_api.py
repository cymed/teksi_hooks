from __future__ import annotations

import dataclasses
from typing import Any


def render_dataclass_api(
    cls: type[Any],
    *,
    language: str = "en",
) -> str:
    """
    Render a dataclass as RST using field metadata.

    Supported metadata:

        metadata={
            "doc": "Description"
        }

    or

        metadata={
            "doc": {
                "en": "...",
                "de": "...",
            }
        }
    """

    def render_type(
        annotation: Any,
    ) -> str:
        if isinstance(
            annotation,
            str,
        ):
            return annotation

        return getattr(
            annotation,
            "__name__",
            str(annotation),
        )

    def render_doc(
        value: Any,
    ) -> str:
        if isinstance(
            value,
            dict,
        ):
            return str(
                value.get(
                    language,
                    value.get(
                        "en",
                        "",
                    ),
                )
                or ""
            )

        return str(
            value or "",
        )

    title = cls.__name__

    lines: list[str] = [
        title,
        "-" * len(title),
        "",
        f".. autoclass:: {cls.__module__}.{cls.__name__}",
        "   :members:",
        "",
    ]

    fields = dataclasses.fields(
        cls,
    )

    if not fields:
        return "\n".join(
            lines,
        )

    lines.extend(
        [
            "Fields",
            "~~~~~~",
            "",
        ]
    )

    for field in fields:
        field_doc = render_doc(
            field.metadata.get(
                "doc",
                "",
            )
        )

        lines.extend(
            [
                f"``{field.name}``",
                f"   Type: ``{render_type(field.type)}``",
                "",
            ]
        )

        if field_doc:
            lines.extend(
                [
                    f"   {field_doc}",
                    "",
                ]
            )

    return "\n".join(
        lines,
    )
