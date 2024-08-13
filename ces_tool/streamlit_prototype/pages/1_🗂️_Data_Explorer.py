import cesdb
import utils


con = cesdb.get_db_connection()

"""
# 🗂️ Data Explorer
Explore all tables in the local database.
"""

stg_pp_tables = []
stg_vp_tables = []
int_tables = []
no_prefix_tables = []

for table in utils.all_tables():
    if table.startswith("stg_pp"):
        stg_pp_tables.append(table)
    elif table.startswith("stg_vp"):
        stg_vp_tables.append(table)
    elif table.startswith("int_"):
        int_tables.append(table)
    else:
        no_prefix_tables.append(table)

def display_tables(con, table_names):
    for table in table_names:
        table_data = con.sql(f"SELECT * FROM {table}").df()
        "### " + table
        table_data
    
"## Proposal Portal - Staging Tables"
display_tables(con, stg_pp_tables)

"## Voting Portal - Staging Tables"
display_tables(con, stg_vp_tables)

"## Intermediate Tables"
display_tables(con, int_tables)

"## CES - Marts (aggregation) Tables"
display_tables(con, no_prefix_tables)