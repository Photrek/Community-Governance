import cesdb
import utils

import gravis as gv
import networkx as nx

import streamlit.components.v1 as components

from pyvis.network import Network
import streamlit as st
import streamlit.components.v1 as components


"""
# 🕸️ Network Analysis

"""
con = cesdb.get_db_connection()

tab1, tab2, tab3 = st.tabs(["Specific Proposal", "All", "Gravis based visualization"])

with tab1:
    selected_proposal = utils.proposal_selector()

    f"Selected: {selected_proposal}"

    if selected_proposal[0]:
        proposal_id = selected_proposal[0]
        f"Selected Proposal: {selected_proposal[1]}"

        edges_query = f"""
        SELECT
            r.collection_id,
            r.question_id,
            e.entropy,
        FROM
            stg_vp_answers as r
        JOIN entropy as e ON
            r.collection_id = e.collection_id
        WHERE
            r.question_id = {proposal_id}
        """
        data = con.sql(edges_query).df()

        sources = data['collection_id']
        targets = data['question_id']
        weights = data['entropy']

        edge_data = zip(sources, targets, weights)

        net = Network(
            height="899px",
            width="899px",
            notebook=True,
            heading='',
            # filter_menu=True,
            # select_menu=True,
        )
        net.toggle_physics(True)

        for e in edge_data:
            src = e[0]
            dst = e[1]
            w = e[2] * 5

            net.add_node(src, src, title=f"user_{src}", color='blue')
            net.add_node(dst, dst, title=f"proposal_{dst}", color='red')
            net.add_edge(src, dst, value=w, color='green')

        net.show('network_html_files/proposal_network.html')

        HtmlFile = open('network_html_files/proposal_network.html', 'r', encoding='utf-8')
        source_code = HtmlFile.read() 
        components.html(source_code, height = 900,width=900)

with tab2:
    x_widh = 500

    net = Network(
        height="899px",
        width="899px",
        notebook=True,
        heading='',
        # filter_menu=True,
        # select_menu=True,
    )

    net.toggle_physics(False)

    users = con.sql("SELECT collection_id FROM stg_vp_collections").fetchall()
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

    proposals = con.sql("SELECT question_id FROM stg_vp_questions").fetchall()
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
        stg_vp_answers as r
    JOIN entropy as e ON
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

    proposals = con.sql("SELECT question_id FROM stg_vp_questions").fetchall()
    n_half_proposals = len(proposals) // 2

    net.show('network_html_files/network.html')

    HtmlFile = open('network_html_files/network.html', 'r', encoding='utf-8')
    source_code = HtmlFile.read() 
    components.html(source_code, height = 900,width=900)

with tab3:
    g = nx.DiGraph()

    "## Relation between proposal creator and proposals"

    users = con.sql("SELECT collection_id FROM stg_vp_collections").fetchall()
    n_half = len(users) // 2
    for i, row in enumerate(users):
        id = f"user_{row[0]}"
        x = (i - n_half) * 40
        y = 100

        g.add_node(id, x=x, y=y, color='blue')

    proposals = con.sql("SELECT question_id FROM stg_vp_questions").fetchall()
    n_half = len(proposals) // 2
    for i, row in enumerate(proposals):
        id = f"proposal_{row[0]}"
        x = (i - n_half) * 40
        y = -100

        g.add_node(id, x=x, y=y, color='red')

    edges_query = """
    SELECT
        r.collection_id,
        r.question_id,
        e.entropy,
    FROM
        stg_vp_answers as r
    JOIN entropy as e ON
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
                    FROM stg_pp_users
                    WHERE user_id IN (
                        SELECT user_id
                        FROM stg_pp_proposals
                        WHERE round_id = {round_id}
                    )
                    """).fetchall()
    n_half = len(users) // 2
    for i, row in enumerate(users):
        id = f"user_{row[0]}"
        x = (i - n_half) * 40
        y = 100

        g.add_node(id, x=x, y=y, color='blue')

    proposals = con.sql(f"SELECT id FROM stg_pp_proposals where round_id = {round_id}").fetchall()
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
    #     stg_vp_rating as r
    # JOIN entropy as e ON
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