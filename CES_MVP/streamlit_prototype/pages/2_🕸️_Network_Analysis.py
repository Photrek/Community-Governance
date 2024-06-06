import cesdb
import utils

import gravis as gv
import networkx as nx

import streamlit.components.v1 as components


"""
# Network Analysis

> TODO:
>
> try out pyvis if it's faster: https://pyvis.readthedocs.io/en/latest/tutorial.html#getting-started
"""
con = cesdb.get_db_connection()

option = utils.round_selector()
round_id = option[0]

g = nx.DiGraph()

"## Relation between proposal creator and proposals"

users = con.sql(f"""
                SELECT user_id
                FROM silver_users
                WHERE user_id IN (
                    SELECT user_id
                    FROM silver_proposals
                    WHERE round_id = {round_id}
                )
                """).fetchall()
n_half = len(users) // 2
for i, row in enumerate(users):
    id = f"user_{row[0]}"
    x = (i - n_half) * 40
    y = 100

    g.add_node(id, x=x, y=y, color='blue')

proposals = con.sql(f"SELECT id FROM silver_proposals where round_id = {round_id}").fetchall()
n_half = len(proposals) // 2
for i, row in enumerate(proposals):
    id = f"proposal_{row[0]}"
    x = (i - n_half) * 40
    y = -100

    g.add_node(id, x=x, y=y, color='red')

# edges_query = """
# SELECT
#     r.user_id,
#     r.proposal_id,
#     e.entropy,
# FROM
#     silver_rating as r
# JOIN gold_entropy as e ON
#     r.user_id = e.user_id,
# """

# ratings = con.sql(edges_query).fetchall()
# n_half = len(ratings) // 2
# for i, row in enumerate(ratings):
#     user_id = f"user_{row[0]}"
#     proposal_id = f"proposal_{row[1]}"
#     entropy = row[2] * 5

#     g.add_edge(user_id, proposal_id, color='green', size=entropy)


fig = gv.d3(g, show_node_label=True, node_drag_fix=True, node_hover_neighborhood=True)
components.html(fig.to_html(), height=600)