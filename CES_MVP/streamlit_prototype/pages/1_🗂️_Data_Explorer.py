import cesdb
import utils


con = cesdb.get_db_connection()

"""
# Data Explorer
Explore all tables in the local database.
"""

for table in utils.all_tables():
    table_data = con.sql(f"SELECT * FROM {table}").df()
    "## " + table
    table_data