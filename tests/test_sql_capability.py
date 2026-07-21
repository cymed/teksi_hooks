from teksi_hooks.capabilities.sql import SqlCapability


class FakeCursor:
    def __init__(self) -> None:
        self.executed = []
        self.fetchone_result = None
        self.fetchall_result = []

    def __enter__(self):
        return self

    def __exit__(
        self,
        exc_type,
        exc,
        traceback,
    ) -> None:
        return None

    def execute(
        self,
        sql,
        parameters=None,
    ) -> None:
        self.executed.append(
            (
                sql,
                parameters,
            )
        )

    def executemany(
        self,
        sql,
        parameters,
    ) -> None:
        self.executed.append(
            (
                sql,
                parameters,
            )
        )

    def fetchone(self):
        return self.fetchone_result

    def fetchall(self):
        return self.fetchall_result


class FakeConnection:
    def __init__(self) -> None:
        self.cursor_instance = FakeCursor()
        self.committed = False
        self.rolled_back = False

    def cursor(self):
        return self.cursor_instance

    def commit(self) -> None:
        self.committed = True

    def rollback(self) -> None:
        self.rolled_back = True

    def transaction(self):
        return "transaction-context"


def test_sql_capability_executes_statement() -> None:
    connection = FakeConnection()
    capability = SqlCapability(
        connection=connection,
    )

    capability.execute(
        "SELECT 1 WHERE id = %s",
        (
            1,
        ),
    )

    assert connection.cursor_instance.executed == [
        (
            "SELECT 1 WHERE id = %s",
            (
                1,
            ),
        )
    ]


def test_sql_capability_returns_fetchone() -> None:
    connection = FakeConnection()
    connection.cursor_instance.fetchone_result = (
        "value",
    )

    capability = SqlCapability(
        connection=connection,
    )

    assert capability.fetchone(
        "SELECT value",
    ) == (
        "value",
    )


def test_sql_capability_returns_fetchall() -> None:
    connection = FakeConnection()
    connection.cursor_instance.fetchall_result = [
        (
            "a",
        ),
        (
            "b",
        ),
    ]

    capability = SqlCapability(
        connection=connection,
    )

    assert capability.fetchall(
        "SELECT value",
    ) == [
        (
            "a",
        ),
        (
            "b",
        ),
    ]


def test_sql_capability_returns_scalar() -> None:
    connection = FakeConnection()
    connection.cursor_instance.fetchone_result = (
        "value",
        "ignored",
    )

    capability = SqlCapability(
        connection=connection,
    )

    assert capability.scalar(
        "SELECT value",
    ) == "value"


def test_sql_capability_returns_none_for_missing_scalar() -> None:
    connection = FakeConnection()
    connection.cursor_instance.fetchone_result = None

    capability = SqlCapability(
        connection=connection,
    )

    assert capability.scalar(
        "SELECT value",
    ) is None


def test_sql_capability_commits_and_rolls_back() -> None:
    connection = FakeConnection()
    capability = SqlCapability(
        connection=connection,
    )

    capability.commit()
    capability.rollback()

    assert connection.committed is True
    assert connection.rolled_back is True


def test_sql_capability_returns_transaction_context() -> None:
    connection = FakeConnection()
    capability = SqlCapability(
        connection=connection,
    )

    assert capability.transaction() == "transaction-context"