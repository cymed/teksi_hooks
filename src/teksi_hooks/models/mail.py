from dataclasses import dataclass, field


@dataclass(slots=True, frozen=True)
class Mail:
    """
    Email message definition.
    """

    recipients: tuple[str, ...] = field(
        metadata={"doc": ("Recipient email addresses.")},
    )

    subject: str = field(
        metadata={"doc": ("Email subject line.")},
    )

    body: str = field(
        metadata={"doc": ("Plain text email body.")},
    )

    cc: tuple[str, ...] = field(
        default_factory=tuple,
        metadata={"doc": ("Optional carbon-copy recipient email addresses.")},
    )

    bcc: tuple[str, ...] = field(
        default_factory=tuple,
        metadata={"doc": ("Optional blind carbon-copy recipient email addresses.")},
    )


@dataclass(slots=True, frozen=True)
class SmtpConfiguration:
    host: str = field(
        metadata={"doc": ("SMTP server hostname.")},
    )

    port: int = field(
        metadata={"doc": ("SMTP server port.")},
    )

    username: str | None = field(
        metadata={"doc": ("Optional SMTP username.")},
    )

    password: str | None = field(
        metadata={"doc": ("Optional SMTP password.")},
    )

    sender: str = field(
        metadata={"doc": ("Sender email address.")},
    )

    use_tls: bool = field(
        default=True,
        metadata={"doc": ("Whether to establish a TLS-secured SMTP connection.")},
    )
