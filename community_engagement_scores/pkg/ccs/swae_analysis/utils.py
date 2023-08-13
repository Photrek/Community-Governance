import sqlite3
from typing import List, Tuple


def execute_query(con: sqlite3.Connection, query: str) -> List[Tuple]:
    """Execute a single query on the database and return the result as a list of tuples.

    Parameters
    ----------
    con : sqlite3.Connection
        The connection object to the SQLite database.
    query : str
        The SQL query to execute.

    Returns
    -------
    List[Tuple]
        A list of tuples representing the result of the query.

    """
    # https://docs.python.org/3/library/sqlite3.html#sqlite3-connection-context-manager
    with con:
        result = con.execute(query).fetchall()
    return result


def execute_script(con: sqlite3.Connection, script: str) -> None:
    """Execute multiple SQL statements as a script on the database.

    Parameters
    ----------
    conn : sqlite3.Connection
        The connection object to the SQLite database.
    script : str
        The SQL script to execute.

    """
    with con:
        con.executescript(script)
