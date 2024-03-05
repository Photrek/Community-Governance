"""Module for creating a graph that represents a part of Swae data."""

import sqlite3
from typing import List

import networkx as nx

from . import utils


def sqlite_to_graph(con: sqlite3.Connection, mission_ids: List[str]) -> nx.DiGraph:
    """Convert selected items from an SQLite database with Swae data into a NetworkX graph.

    Parameters
    ----------
    con : sqlite3.Connection
        The SQLite database connection object.
    mission_ids : List[str]
        A list of mission IDs to consider for the data conversion.

    Returns
    -------
    graph : networkx.DiGraph
        The NetworkX graph that contains the selected data from the database.

    """
    if isinstance(mission_ids, str):
        mission_ids = [mission_ids]

    def to_sql_str1(items):
        return ", ".join(f"'{x}'" for x in items)

    def to_sql_str2(rows, idx):
        return ", ".join(f"'{row[idx]}'" for row in rows)

    mission_ids_str = to_sql_str1(mission_ids)
    query = (
        f"SELECT * FROM missions WHERE mission_id IN ({mission_ids_str}) "
        "ORDER BY creation_timestamp;"
    )
    missions = utils.execute_query(con, query)
    query = (
        f"SELECT * FROM proposals WHERE mission_id IN ({mission_ids_str}) "
        "ORDER BY creation_timestamp;"
    )
    proposals = utils.execute_query(con, query)

    proposal_ids_str = to_sql_str2(proposals, 0)
    query = (
        f"SELECT * FROM ratings WHERE proposal_id IN ({proposal_ids_str}) "
        "ORDER BY creation_timestamp;"
    )
    ratings = utils.execute_query(con, query)
    query = (
        f"SELECT * FROM comments WHERE proposal_id IN ({proposal_ids_str}) "
        "ORDER BY creation_timestamp;"
    )
    comments = utils.execute_query(con, query)

    comment_ids_str = to_sql_str2(comments, 0)
    query = f"SELECT * FROM reactions WHERE comment_id IN ({comment_ids_str});"
    reactions = utils.execute_query(con, query)

    user_ids0 = set(row[1] for row in missions)
    user_ids1 = set(row[2] for row in proposals)
    user_ids2 = set(row[2] for row in ratings)
    user_ids3 = set(row[2] for row in comments)
    user_ids4 = set(row[2] for row in reactions)
    user_ids = set().union(user_ids0, user_ids1, user_ids2, user_ids3, user_ids4)
    user_ids_str = to_sql_str1(user_ids)
    query = f"SELECT * FROM users WHERE user_id IN ({user_ids_str});"
    users = utils.execute_query(con, query)

    m_color = "blue"
    u_color = "green"
    p_color = "red"
    c_color = "violet"
    re_color = "limegreen"

    g = nx.DiGraph()

    # Missions
    mission_to_data = dict()
    n_half = len(missions) // 2
    for i, row in enumerate(missions):
        m_id = row[0]
        u_id = row[1]
        m_title = row[2]
        m_descr = row[3]
        x = (i - n_half) * 40
        y = 400
        hover = (
            f"<b>Mission</b>\n\n<b>Title</b>\n{m_title}\n\n<b>Summary</b>\n{m_descr}"
        )

        # Remember data about included missions
        md = mission_to_data[m_id] = dict()
        md["id"] = m_id
        md["x"] = x
        md["y"] = y
        md["proposal_counter"] = 0
        # Add mission node
        g.add_node(m_id, color=m_color, hover=hover, x=x, y=y)

    # Proposals
    p_ids = []
    proposal_to_data = dict()
    n_half = len(proposals) // 2
    for i, row in enumerate(proposals):
        p_id = row[0]
        m_id = row[1]
        u_id = row[2]
        p_title = row[3]
        p_summary = row[4]
        p_ids.append(p_id)
        md = mission_to_data[m_id]
        x = (i - n_half) * 40
        y = md["y"] - 50
        hover = (
            f"<b>Proposal</b>\n\n<b>Title</b>\n{p_title}\n\n<b>Summary</b>\n{p_summary}"
        )
        md["proposal_counter"] += 1

        # Remember data about included proposals
        pd = proposal_to_data[p_id] = dict()
        pd["id"] = p_id
        pd["x"] = x
        pd["y"] = y
        # Add proposal node
        g.add_node(p_id, color=p_color, hover=hover, x=x, y=y)
        # Add proposal-mission link
        g.add_edge(m_id, p_id, color=p_color)

    # Users
    user_to_data = dict()
    user_counter = 0
    for i, row in enumerate(users):
        u_id = row[0]
        u_name = row[1]
        u_email = row[2]
        u_eth = row[3]
        u_ada = row[4]
        u_dt = row[20]
        ud = user_to_data[u_id] = dict()
        ud["i"] = i
        ud["name"] = u_name
        ud["creation_datetime"] = u_dt
        ud["email_address"] = u_email
        ud["ethereum_address"] = u_eth
        ud["cardano_address"] = u_ada
        ud["user_counter"] = user_counter
        user_counter += 1

    # Comments
    comment_to_data = dict()
    for row in comments:
        c_id = row[0]
        p_id = row[1]
        u_id = row[2]
        pc_id = row[3]
        c_text = row[4]
        cd = comment_to_data[c_id] = dict()
        cd["text"] = c_text
        if pc_id:
            a, b = pc_id, c_id
        else:
            a, b = p_id, c_id
        hover = f"<b>Comment</b>\n\n<b>Text</b>\n{c_text}"

        # Add comment node
        g.add_node(c_id, color=c_color, hover=hover)
        # Add comment->proposal or comment->parent_comment link
        g.add_edge(a, b, color=c_color)

        if u_id not in user_to_data:
            continue
        user = user_to_data[u_id]
        user_name = user["name"]
        hover = f"<b>User</b>\n\n<b>Name</b>\n{user_name}"
        # Add user node
        g.add_node(u_id, color=u_color, hover=hover)
        # Add user->comment link
        g.add_edge(c_id, u_id, color=u_color)

    # Reactions
    for row in reactions:
        re_id = row[0]
        c_id = row[1]
        u_id = row[2]
        re_type = row[3]
        hover = f"<b>Reaction</b>\n\n<b>Type</b>\n{re_type}"
        # Add reaction node
        g.add_node(re_id, color=re_color, hover=hover)
        # Add reaction->comment link
        g.add_edge(re_id, c_id, color=re_color)

        if u_id not in user_to_data:
            continue
        user = user_to_data[u_id]
        user_name = user["name"]
        hover = f"<b>User</b>\n\n<b>Name</b>\n{user_name}"
        # Add user node
        g.add_node(u_id, color=u_color, hover=hover)
        # Add user->reaction link
        g.add_edge(u_id, re_id, color=u_color)
    return g
