from . import utils


def sqlite_to_graph(con, mission_ids):
    import networkx as nx

    def to_sql_str1(items):
        return ", ".join("'{}'".format(x) for x in items)

    def to_sql_str2(rows, idx):
        return ", ".join("'{}'".format(row[idx]) for row in rows)

    mission_ids_str = to_sql_str1(mission_ids)
    query = f"SELECT * FROM missions WHERE mission_id IN ({mission_ids_str}) ORDER BY creation_timestamp;"
    missions = utils.execute_query(con, query)
    query = f"SELECT * FROM proposals WHERE mission_id IN ({mission_ids_str}) ORDER BY creation_timestamp;"
    proposals = utils.execute_query(con, query)

    proposal_ids_str = to_sql_str2(proposals, 0)
    query = f"SELECT * FROM ratings WHERE proposal_id IN ({proposal_ids_str}) ORDER BY creation_timestamp;"
    ratings = utils.execute_query(con, query)
    query = f"SELECT * FROM comments WHERE proposal_id IN ({proposal_ids_str}) ORDER BY creation_timestamp;"
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
    ra_color = "orange"
    re_color = "limegreen"

    g = nx.DiGraph()

    # Missions
    mission_to_data = dict()
    for i, row in enumerate(missions):
        m_id = row[0]
        u_id = row[1]
        m_title = row[2]
        m_descr = row[3]

        x = 0
        y = i * 100
        hover = "<b>Mission</b>\n\n<b>Title</b>\n{}\n\n<b>Summary</b>\n{}".format(
            m_title, m_descr
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
    for i, row in enumerate(proposals):
        p_id = row[0]
        m_id = row[1]
        u_id = row[2]
        p_title = row[3]
        p_summary = row[4]

        p_ids.append(p_id)
        md = mission_to_data[m_id]
        x = i * 40  # md['x'] - 350 + md['proposal_counter'] * 40
        y = md["y"] - 50
        hover = "<b>Proposal</b>\n\n<b>Title</b>\n{}\n\n<b>Summary</b>\n{}".format(
            p_title, p_summary
        )
        md["proposal_counter"] += 1

        # Remember data about included proposals
        pd = proposal_to_data[p_id] = dict()
        pd["id"] = p_id
        pd["x"] = x
        pd["y"] = y

        # Add proposal node
        g.add_node(p_id, color=p_color, hover=hover, x=x, y=y)
        # g.add_node(u_id, color=u_color)

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
    for i, row in enumerate(comments):
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
        hover = "<b>Comment</b>\n\n<b>Text</b>\n{}".format(c_text)

        # Add comment node
        x = i * 15
        y = -100
        g.add_node(c_id, color=c_color, hover=hover, x=x, y=y)
        # Add comment->proposal or comment->parent_comment link
        g.add_edge(a, b, color=c_color)

        user = user_to_data[u_id]
        # hover = '<b>User</b>\n\n<b>Name</b>\n{}\n\n<b>e-Mail</b>\n{}'.format(
        #    user['name'], user['email_address'])
        hover = "<b>User</b>\n\n<b>Name</b>\n{}".format(user["name"])

        # Add user node
        x = user["i"] * 15
        y = -300
        g.add_node(
            u_id, color=u_color, hover=hover, x=x, y=y
        )  # , x=-300, y=user_to_data[uid]['user_counter']*10)
        # Add user->comment link
        g.add_edge(c_id, u_id, color=u_color)

    # Reactions
    reaction_to_data = dict()
    for i, row in enumerate(reactions):
        re_id = row[0]
        c_id = row[1]
        u_id = row[2]
        re_type = row[3]

        hover = "<b>Reaction</b>\n\n<b>Type</b>\n{}".format(re_type)

        # Add reaction node
        x = i * 15
        y = -150
        g.add_node(re_id, color=re_color, hover=hover, x=x, y=y)
        # Add reaction->comment link
        g.add_edge(re_id, c_id, color=re_color)

        user = user_to_data[u_id]
        # hover = '<b>User</b>\n\n<b>Name</b>\n{}\n\n<b>e-Mail</b>\n{}'.format(
        #    user['name'], user['email_address'])
        hover = "<b>User</b>\n\n<b>Name</b>\n{}".format(user["name"])

        # Add user node
        x = user["i"] * 15
        y = -310
        g.add_node(
            u_id, color=u_color, hover=hover, x=x, y=y
        )  # , x=-300, y=user_to_data[uid]['user_counter']*10)
        # Add user->reaction link
        g.add_edge(u_id, re_id, color=u_color)
    return g


def dataframes_to_graph(
    dfs, mission_title_prefix="Round 1 - Pool  B", mission_ids=None
):
    import networkx as nx

    df_missions = dfs["missions"]
    df_proposals = dfs["proposals"]
    df_users = dfs["users"]
    df_comments = dfs["comments"]
    df_reactions = dfs["reactions"]

    if mission_ids is None:
        mission_ids = [
            row["mission_id"]
            for i, row in df_missions.iterrows()
            if row["title"].startswith(mission_title_prefix)
        ]

    mcolor = "blue"
    ucolor = "green"
    pcolor = "red"
    ccolor = "violet"
    racolor = "orange"
    recolor = "limegreen"

    g = nx.DiGraph()

    mission_to_data = dict()
    for i, row in df_missions.iterrows():
        mid = row["mission_id"]
        mtitle = row["title"]
        mdesc = row["description"]
        uid = row["user_id"]

        if mid not in mission_ids:
            continue

        x = 0
        y = i * 100
        hover = "<b>Mission</b>\n\n<b>Title</b>\n{}\n\n<b>Summary</b>\n{}".format(
            mtitle, mdesc
        )

        # Remember data about included missions
        md = mission_to_data[mid] = dict()
        md["id"] = md
        md["x"] = x
        md["y"] = y
        md["proposal_counter"] = 0

        # Add mission node
        g.add_node(mid, color=mcolor, hover=hover, x=x, y=y)

        # Add relationship to user who created the mission
        # g.add_node(uid, color=pcolor)
        # g.add_edge(mid, uid)

    proposals = []
    proposal_to_data = dict()
    for i, row in df_proposals.iterrows():
        pid = row["proposal_id"]
        ptitle = row["title"]
        psummary = row["summary"]
        mid = row["mission_id"]
        uid = row["user_id"]

        if mid not in mission_ids:
            continue
        proposals.append(pid)

        md = mission_to_data[mid]
        x = md["x"] - 350 + md["proposal_counter"] * 40
        y = md["y"] - 50
        hover = "<b>Proposal</b>\n\n<b>Title</b>\n{}\n\n<b>Summary</b>\n{}".format(
            ptitle, psummary
        )
        md["proposal_counter"] += 1

        # Remember data about included proposals
        ptd = proposal_to_data[pid] = dict()
        ptd["id"] = pid
        ptd["x"] = x
        ptd["y"] = y

        # Add proposal node
        g.add_node(pid, color=pcolor, hover=hover, x=x, y=y)
        # g.add_node(uid, color=ucolor)

        # Add proposal-mission link
        g.add_edge(mid, pid, color=pcolor)

    user_to_data = dict()
    user_counter = 0
    for i, row in df_users.iterrows():
        uid = row["user_id"]

        ud = user_to_data[uid] = dict()
        ud["name"] = row["name"]
        ud["creation_datetime"] = row["creation_datetime"]
        ud["email_address"] = row["email_address"]
        ud["ethereum_address"] = row["ethereum_address"]
        ud["cardano_address"] = row["cardano_address"]
        ud["user_counter"] = user_counter
        user_counter += 1

    comment_to_data = dict()
    for i, row in df_comments.iterrows():
        cid = row["comment_id"]
        pid = row["proposal_id"]
        uid = row["user_id"]
        pcid = row["parent_comment_id"]
        ctext = row["text"]

        if pid not in proposal_to_data:
            continue

        if uid not in user_to_data:
            continue

        cd = comment_to_data[cid] = dict()
        cd["text"] = ctext

        if pcid:
            a, b = pcid, cid
        else:
            a, b = pid, cid

        hover = "<b>Comment</b>\n\n<b>Text</b>\n{}".format(ctext)

        # Add comment node
        g.add_node(cid, color=ccolor, hover=hover)
        # Add comment->proposal or comment->parent_comment link
        g.add_edge(a, b, color=ccolor)

        user = user_to_data[uid]
        # hover = '<b>User</b>\n\n<b>Name</b>\n{}\n\n<b>e-Mail</b>\n{}'.format(
        #    user['name'], user['email_address'])
        hover = "<b>User</b>\n\n<b>Name</b>\n{}".format(user["name"])

        # Add user node
        g.add_node(
            uid, color=ucolor, hover=hover
        )  # , x=-300, y=user_to_data[uid]['user_counter']*10)
        # Add user->comment link
        g.add_edge(cid, uid, color=ucolor)

    for i, row in df_reactions.iterrows():
        rid = row["reaction_id"]
        cid = row["comment_id"]
        uid = row["user_id"]
        rtype = row["reaction_type"]

        if cid not in comment_to_data:
            continue

        hover = "<b>Reaction</b>\n\n<b>Type</b>\n{}".format(rtype)

        # Add reaction node
        g.add_node(rid, color=recolor, hover=hover)
        # Add reaction->comment link
        g.add_edge(rid, cid, color=ccolor)

    return g
