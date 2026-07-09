import logging
import os
import re
import sys
import inspect
import time
import abc
from pathlib import Path
import dataclasses
import psycopg

from typing import Any, TypeVar
from .exceptions import TeksiHookError


@dataclasses.dataclass(slots=True)
class SqlCapability:
    connection: psycopg.Connection

    def execute(
        self,
        sql: str,
        parameters: tuple[Any, ...] | dict[str, Any] | None = None,
    ) -> None:
        with self.connection.cursor() as cur:
            cur.execute(
                sql,
                parameters,
            )

    def fetchone(
        self,
        sql: str,
        parameters: tuple[Any, ...] | dict[str, Any] | None = None,
    ) -> tuple[Any, ...] | None:
        with self.connection.cursor() as cur:
            cur.execute(
                sql,
                parameters,
            )

            return cur.fetchone()

    def fetchall(
        self,
        sql: str,
        parameters: tuple[Any, ...] | dict[str, Any] | None = None,
    ) -> list[tuple[Any, ...]]:
        with self.connection.cursor() as cur:
            cur.execute(
                sql,
                parameters,
            )

            return cur.fetchall()

    def executemany(
        self,
        sql: str,
        parameters: list[tuple[Any, ...]],
    ) -> None:
        with self.connection.cursor() as cur:
            cur.executemany(
                sql,
                parameters,
            )

    def scalar(
        self,
        sql: str,
        parameters: tuple[Any, ...] | dict[str, Any] | None = None,
    ) -> Any:
        with self.connection.cursor() as cur:
            cur.execute(
                sql,
                parameters,
            )

            row = cur.fetchone()

        if row is None:
            return None

        return row[0]

    def commit(self) -> None:
        self.connection.commit()

    def rollback(self) -> None:
        self.connection.rollback()

    def transaction(self):
        return self.connection.transaction()