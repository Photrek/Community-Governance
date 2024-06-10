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
    bronze_questions t1
CROSS JOIN
    silver_proposals t2
WHERE
    levenshtein(t1.question, t2.title) < 5
"""
"# Proposal Similarity"
proposal_similarity = con.sql(proposal_similarity_query).df()
proposal_similarity

for table in utils.all_tables():
    table_data = con.sql(f"SELECT * FROM {table}").df()
    "## " + table
    table_data