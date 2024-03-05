"""Module for loading preprocessed Swae data into useful formats."""

import csv
import os
import sqlite3
from typing import Dict, Tuple

from . import utils


def load_sqlite(
    tabular_data: Dict[str, Tuple],
    filepath: str = ":memory:",
    use_foreign_keys: bool = False,
) -> sqlite3.Connection:
    """Load preprocessed tabular data into an SQLite database.

    Parameters
    ----------
    tabular_data : Dict[str, Tuple]
        A dictionary containing the tabular data to be loaded into the database.
    filepath : str, optional, default=":memory:"
        The path of the SQLite database file to create.
        Default is an in-memory database (":memory:").
        Caution: If the file exists it will be overwritten.
    use_foreign_keys : bool, optional, default=False
        A flag that determines whether foreign key support is be enabled in SQLite.

    Returns
    -------
    con : sqlite3.Connection
        The SQLite database connection object.

    Raises
    ------
    sqlite3.IntegrityError
        If a primary key or foreign key constraint is violated.

    """
    # Argument processing
    if filepath != ":memory:":
        if os.path.isfile(filepath):
            os.remove(filepath)
        else:
            directory = os.path.dirname(filepath)
            os.makedirs(directory, exist_ok=True)
    con = sqlite3.connect(filepath)

    # https://www.sqlite.org/foreignkeys.html
    if use_foreign_keys:
        sql = "PRAGMA foreign_keys = ON"
        utils.execute_query(con, sql)

        foreign_key_map = {
            "missions": [
                # Skipped because in the example data a mission was created by a user
                # not mentioned in users
                "FOREIGN KEY(user_id) REFERENCES users(user_id)",
            ],
            "proposals": [
                "FOREIGN KEY(mission_id) REFERENCES missions(mission_id)",
                "FOREIGN KEY(user_id) REFERENCES users(user_id)",
            ],
            "comments": [
                "FOREIGN KEY(proposal_id) REFERENCES proposals(proposal_id)",
                "FOREIGN KEY(user_id) REFERENCES users(user_id)",
                # Skipped because a conditional foreign key that may be NULL
                # is not supported in SQLite
                # 'FOREIGN KEY(parent_comment_id) REFERENCES comments(comment_id)',
            ],
            "ratings": [
                "FOREIGN KEY(proposal_id) REFERENCES proposals(proposal_id)",
                "FOREIGN KEY(user_id) REFERENCES users(user_id)",
            ],
            "reactions": [
                "FOREIGN KEY(comment_id) REFERENCES comments(comment_id)",
                "FOREIGN KEY(user_id) REFERENCES users(user_id)",
            ],
            "views": [
                "FOREIGN KEY(proposal_id) REFERENCES proposals(proposal_id)",
                "FOREIGN KEY(user_id) REFERENCES users(user_id)",
            ],
        }

    # https://www.sqlite.org/datatype3.html
    datatype_map = {
        "bool": "BOOLEAN",
        "int": "INTEGER",
        "float": "REAL",
        "str": "TEXT",
    }

    with con:
        for table_name, (rows, columns, datatypes) in tabular_data.items():
            # Create table
            column_definition = []
            for i, col in enumerate(columns):
                dt = datatype_map[datatypes[i]]
                column_definition.append(f"{col} {dt}")
            if use_foreign_keys:
                if table_name in foreign_key_map:
                    # Define foreign keys
                    foreign_key_statements = foreign_key_map[table_name]
                    column_definition.extend(foreign_key_statements)
            column_definition = "\n  " + ",\n  ".join(column_definition) + "\n"
            query = f"CREATE TABLE {table_name} ({column_definition})"
            con.execute(query)

            # Define primary key
            primary_key = columns[0]
            query = (
                f"CREATE UNIQUE INDEX idx_{table_name}_{primary_key} "
                f"ON {table_name} ({primary_key})"
            )
            con.execute(query)

            # Insert data
            value_placeholders = ",".join(["?"] * len(columns))
            query = f"INSERT INTO {table_name} VALUES ({value_placeholders})"
            con.executemany(query, rows)
    return con


def sqlite_to_csv(
    con: sqlite3.Connection, dirpath: str, delimiter: str = ",", quoting: bool = True
) -> None:
    """Export all tables from an SQLite database to CSV files.

    Each table in the database will be saved as a separate CSV file in the specified directory.

    Parameters
    ----------
    con : sqlite3.Connection
        The SQLite database connection object.
    dirpath : str
        The directory path where the CSV files will be stored.
    delimiter : str, optional, default=","
        The delimiter to use for CSV files.
    quoting : bool, optional, default=True
        Whether to enable quoting for CSV files.

    Raises
    ------
    sqlite3.Error
        If there is an error executing an SQL query.
    FileNotFoundError
        If the specified directory path does not exist and can not be created.

    """
    cursor = con.cursor()

    # Precondition: Target directory exists or is created
    os.makedirs(dirpath, exist_ok=True)

    # Prepare kwargs for csv writer
    kwargs = dict(delimiter=delimiter, lineterminator="\n")
    if quoting:
        kwargs["quoting"] = csv.QUOTE_ALL

    # Get table names
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [record[0] for record in cursor.fetchall()]

    for table in tables:
        # Get column names
        cursor.execute(f"PRAGMA table_info({table})")
        columns = [row[1] for row in cursor.fetchall()]

        # Get data
        if "creation_timestamp" in columns:
            cursor.execute(f"SELECT * FROM {table} ORDER BY creation_timestamp;")
        else:
            cursor.execute(f"SELECT * FROM {table};")
        data = cursor.fetchall()
        data.insert(0, columns)

        # Write data to CSV file
        csv_filepath = os.path.join(dirpath, f"{table}.csv")
        with open(csv_filepath, "w") as f:
            writer = csv.writer(f, **kwargs)
            writer.writerows(data)


def sqlite_to_excel(con: sqlite3.Connection, filepath: str) -> None:
    """Export all tables from an SQLite database to an Excel file.

    Each table in the database will be saved as a separate sheet in the Excel file.

    Parameters
    ----------
    con : sqlite3.Connection
        The SQLite database connection object.
    filepath : str
        The path of the Excel file to be created.

    Raises
    ------
    sqlite3.Error
        If there is an error executing an SQL query.

    pyexcelerate.exceptions.InvalidParametersError
        If there is an error saving the Excel file.

    """
    import pyexcelerate

    cursor = con.cursor()
    workbook = pyexcelerate.Workbook()

    # Define header format
    header_format = pyexcelerate.Style(
        font=pyexcelerate.Font(bold=True),
        alignment=pyexcelerate.Alignment(horizontal="center", vertical="top"),
    )

    # Get table names
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [record[0] for record in cursor.fetchall()]

    for table in tables:
        # Get column names
        cursor.execute(f"PRAGMA table_info({table})")
        columns = [row[1] for row in cursor.fetchall()]

        # Get data
        if "engagement_score" in columns and "user_id" in columns:
            cursor.execute(
                f"SELECT * FROM {table} ORDER BY engagement_score DESC, user_id DESC;"
            )
        elif "creation_timestamp" in columns:
            cursor.execute(f"SELECT * FROM {table} ORDER BY creation_timestamp;")
        else:
            cursor.execute(f"SELECT * FROM {table};")
        data = cursor.fetchall()
        data.insert(0, columns)

        # Write data to spreadsheet
        sheet = workbook.new_sheet(table, data=data)

        # Apply header format
        for i, header in enumerate(columns, 1):
            sheet.set_cell_value(1, i, header)
            sheet.set_cell_style(1, i, header_format)
    workbook.save(filepath)
