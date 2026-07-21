from __future__ import annotations

import dataclasses
from typing import Any

import psycopg


@dataclasses.dataclass(slots=True)
class SqlCapability:
    """
    Capability wrapper around a psycopg database connection.

    This class provides small convenience methods for executing SQL commands,
    fetching rows and managing transaction boundaries. It intentionally stays
    generic and does not contain TEKSI domain-specific query logic.
    """

    connection: psycopg.Connection = dataclasses.field(
        metadata={
            "doc": (
                "Open psycopg database connection used by hook capabilities "
                "and services. The connection lifecycle is owned by the caller."
            )
        },
    )

    def execute(
        self,
        sql: str,
        parameters: tuple[Any, ...] | dict[str, Any] | None = None,
    ) -> None:
        """
        Execute a SQL statement that does not need to return rows.
        """

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
        """
        Execute a SQL query and return the first row, or None if no row exists.
        """

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
        """
        Execute a SQL query and return all rows.
        """

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
        """
        Execute a SQL statement repeatedly for a list of parameter tuples.
        """

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
        """
        Execute a SQL query and return the first column of the first row.

        Returns None if the query returns no rows.
        """

        with self.connection.cursor() as cur:
            cur.execute(
                sql,
                parameters,
            )

            row = cur.fetchone()

        if row is None:
            return None

        return row[0]

    def commit(
        self,
    ) -> None:
        """
        Commit the current database transaction.
        """

        self.connection.commit()

    def rollback(
        self,
    ) -> None:
        """
        Roll back the current database transaction.
        """

        self.connection.rollback()

    def transaction(
        self,
    ):
        """
        Return a psycopg transaction context manager.

        The caller is responsible for using the returned context manager.
        """

        return self.connection.transaction()