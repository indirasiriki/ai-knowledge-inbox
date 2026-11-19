import sqlite3
import threading
from contextlib import contextmanager
from pathlib import Path

SCHEMA = Path(__file__).with_name("schema.sql").read_text(encoding="utf-8")


class Database:
    """One SQLite connection guarded by a lock.

    Writes are short. The lock keeps a read from landing in the middle of
    the item-plus-chunks transaction.
    """

    def __init__(self, connection: sqlite3.Connection):
        self._conn = connection
        self._lock = threading.Lock()

    def read(self, sql: str, params=()):
        with self._lock:
            return self._conn.execute(sql, params).fetchall()

    def read_one(self, sql: str, params=()):
        with self._lock:
            return self._conn.execute(sql, params).fetchone()

    def write(self, sql: str, params=()):
        with self._lock:
            cursor = self._conn.execute(sql, params)
            self._conn.commit()
            return cursor

    @contextmanager
    def transaction(self):
        # isolation_level=None means we own BEGIN/COMMIT. Hold the lock for the whole unit.
        with self._lock:
            self._conn.execute("BEGIN IMMEDIATE")
            try:
                yield self._conn
                self._conn.commit()
            except Exception:
                self._conn.rollback()
                raise

    def close(self):
        self._conn.close()


def open_database(file_path) -> Database:
    """Open the inbox file, or ':memory:' for tests, and apply the schema."""
    location = str(file_path)
    if location != ":memory:":
        Path(location).parent.mkdir(parents=True, exist_ok=True)

    connection = sqlite3.connect(location, check_same_thread=False, isolation_level=None)
    connection.row_factory = sqlite3.Row
    # Required for ON DELETE CASCADE. SQLite leaves this off unless set per connection.
    connection.execute("PRAGMA foreign_keys = ON")
    if location != ":memory:":
        connection.execute("PRAGMA journal_mode = WAL")
    connection.executescript(SCHEMA)
    return Database(connection)
