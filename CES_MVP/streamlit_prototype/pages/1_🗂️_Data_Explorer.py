import cesdb
import utils


con = cesdb.get_db_connection()

"""
# 🗂️ Data Explorer
Explore all tables in the local database.
"""

proposal_similarity_query = """
SELECT
    t1.question_id AS id1,
    t1.question AS title1,
    t2.id AS id2,
    t2.title AS title2,
    levenshtein(t1.question, t2.title) AS distance
FROM
    stg_vp_questions t1
CROSS JOIN
    stg_pp_proposals t2
WHERE
    levenshtein(t1.question, t2.title) < 5
"""
"# Proposal Similarity"
proposal_similarity = con.sql(proposal_similarity_query).df()
proposal_similarity

# all_tables returns a list of all tables. There are three types of tables (starting with stg_pp, stg_vp, and no prefix) put them in separate lists.

stg_pp_tables = []
stg_vp_tables = []
no_prefix_tables = []

for table in utils.all_tables():
    if table.startswith("stg_pp"):
        stg_pp_tables.append(table)
    elif table.startswith("stg_vp"):
        stg_vp_tables.append(table)
    else:
        no_prefix_tables.append(table)

"## Proposal Portal - Staging Tables"
for table in stg_pp_tables:
    table_data = con.sql(f"SELECT * FROM {table}").df()
    "### " + table
    table_data

"## Voting Portal - Staging Tables"
for table in stg_vp_tables:
    table_data = con.sql(f"SELECT * FROM {table}").df()
    "### " + table
    table_data

"## CES - Marts (aggregation) Tables"
for table in stg_vp_tables:
    table_data = con.sql(f"SELECT * FROM {table}").df()
    "### " + table
    table_data