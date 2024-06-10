import cesdb
import utils

import gravis as gv
import networkx as nx

import streamlit.components.v1 as components

from pyvis.network import Network
import streamlit as st
import streamlit.components.v1 as components


"""
# Network Analysis

> TODO:
>
> try out pyvis if it's faster: https://pyvis.readthedocs.io/en/latest/tutorial.html#getting-started
"""
con = cesdb.get_db_connection()

x_widh = 500

net = Network(
    height="899px",
    width="899px",
    notebook=True,
    heading='',
    filter_menu=True,
    # select_menu=True,
)

net.toggle_physics(False)

users = con.sql("SELECT collection_id FROM bronze_collections").fetchall()
n_half = len(users) // 2
for i, row in enumerate(users):
    id = f"user_{row[0]}"
    x = (i - n_half) * x_widh
    y = 1000

    net.add_node(
        id,
        label=id,
        x=x,
        y=y,
        color='blue'
    )

proposals = con.sql("SELECT question_id FROM bronze_questions").fetchall()
n_half = len(proposals) // 2
for i, row in enumerate(proposals):
    id = f"proposal_{row[0]}"
    x = (i - n_half) * x_widh
    y = -1000

    net.add_node(
        id,
        label=id,
        x=x,
        y=y,
        color='red'
    )

edges_query = """
SELECT
    r.collection_id,
    r.question_id,
    e.entropy,
FROM
    silver_ratings as r
JOIN gold_entropy as e ON
    r.collection_id = e.collection_id,
"""

ratings = con.sql(edges_query).fetchall()
n_half = len(ratings) // 2
for i, row in enumerate(ratings):
    user_id = f"user_{row[0]}"
    proposal_id = f"proposal_{row[1]}"
    entropy = row[2] * 100

    net.add_edge(
        user_id,
        proposal_id,
        color='green',
        width=entropy
    )

proposals = con.sql("SELECT question_id FROM bronze_questions").fetchall()
n_half_proposals = len(proposals) // 2

# edges_query = """
# SELECT
#     r.collection_id,
#     r.question_id,
#     e.entropy,
# FROM
#     silver_ratings as r
# JOIN gold_entropy as e ON
#     r.collection_id = e.collection_id,
# """
# data = con.sql(edges_query).df()

# sources = data['collection_id']
# targets = data['question_id']
# weights = data['entropy']

# edge_data = zip(sources, targets, weights)

# for e in edge_data:
#     src = e[0]
#     dst = e[1]
#     w = e[2] * 5
#     print(f"src: {src}, dst: {dst}, w: {w}")

#     net.add_node(src, src, title=f"user_{src}", color='blue')
#     net.add_node(dst, dst, title=f"proposal_{dst}", color='red')
#     net.add_edge(src, dst, value=w, color='green')

net.show('network_html_files/network.html')

HtmlFile = open('network_html_files/network.html', 'r', encoding='utf-8')
source_code = HtmlFile.read() 
components.html(source_code, height = 900,width=900)



# nx_graph = nx.cycle_graph(10)
# nx_graph.nodes[1]['title'] = 'Number 1'
# nx_graph.nodes[1]['group'] = 1
# nx_graph.nodes[3]['title'] = 'I belong to a different group!'
# nx_graph.nodes[3]['group'] = 10
# nx_graph.add_node(20, size=20, title='couple', group=2)
# nx_graph.add_node(21, size=15, title='couple', group=2)
# nx_graph.add_edge(20, 21, weight=5)
# nx_graph.add_node(25, size=25, label='lonely', title='lonely node', group=3)


# nt = Network("899px", "899px", notebook=True, heading='')
# nt.from_nx(nx_graph)
# # nt.show_buttons(filter_=['physics'])
# nt.show('network_html_files/test.html')

# HtmlFile = open('network_html_files/test.html', 'r', encoding='utf-8')
# source_code = HtmlFile.read() 
# components.html(source_code, height = 900,width=900)


g = nx.DiGraph()

"## Relation between proposal creator and proposals"

users = con.sql("SELECT collection_id FROM bronze_collections").fetchall()
n_half = len(users) // 2
for i, row in enumerate(users):
    id = f"user_{row[0]}"
    x = (i - n_half) * 40
    y = 100

    g.add_node(id, x=x, y=y, color='blue')

proposals = con.sql("SELECT question_id FROM bronze_questions").fetchall()
n_half = len(proposals) // 2
for i, row in enumerate(proposals):
    id = f"proposal_{row[0]}"
    x = (i - n_half) * 40
    y = -100

    g.add_node(id, x=x, y=y, color='red')

proposals

edges_query = """
SELECT
    r.collection_id,
    r.question_id,
    e.entropy,
FROM
    silver_ratings as r
JOIN gold_entropy as e ON
    r.collection_id = e.collection_id,
"""

ratings = con.sql(edges_query).fetchall()
n_half = len(ratings) // 2
for i, row in enumerate(ratings):
    user_id = f"user_{row[0]}"
    proposal_id = f"proposal_{row[1]}"
    entropy = row[2] * 5

    g.add_edge(user_id, proposal_id, color='green', size=entropy)


fig = gv.d3(g, show_node_label=True, node_drag_fix=True, node_hover_neighborhood=True)
components.html(fig.to_html(), height=600)


"""
# TODO apply to API data once mapping question_id => proposal_id is done
"""

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