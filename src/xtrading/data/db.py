import contextlib
from typing import Iterator, Optional

import pymysql


MYSQL_HOST = "127.0.0.1"
MYSQL_PORT = 3306
MYSQL_USER = "root"
MYSQL_PASSWORD = "112358"
DATABASE_NAME = "x_trading"


def get_connection(database: Optional[str] = None) -> pymysql.connections.Connection:
    return pymysql.connect(
        host=MYSQL_HOST,
        port=MYSQL_PORT,
        user=MYSQL_USER,
        password=MYSQL_PASSWORD,
        database=database,
        charset="utf8mb4",
        autocommit=False,
        cursorclass=pymysql.cursors.DictCursor,
    )


@contextlib.contextmanager
def mysql_cursor(database: Optional[str] = None) -> Iterator[pymysql.cursors.Cursor]:
    conn = get_connection(database)
    try:
        cursor = conn.cursor()
        try:
            yield cursor
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            cursor.close()
    finally:
        conn.close()


def ensure_database_exists() -> None:
    with mysql_cursor(None) as cur:
        cur.execute(f"CREATE DATABASE IF NOT EXISTS `{DATABASE_NAME}` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;")


