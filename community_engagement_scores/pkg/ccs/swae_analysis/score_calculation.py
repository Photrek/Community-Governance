import sqlite3
from typing import Dict, List, Optional, Tuple

import numpy as np
import pkg_resources

from . import utils


def create_filter_views(
    con: sqlite3.Connection,
    filter_id: int,
    mission_ids: List[str],
    extra_time_in_days: int = 21,
) -> None:
    """Create database views that restrict each table to items belonging to given missions.

    Parameters
    ----------
    con : Connection
        The connection object to the SQLite database.
    filter_id : int
        The ID of the filter to create. It will be used in a prefix for each created view.
    mission_ids : List[str]
        A list of mission identifiers.
    extra_time_in_days : int, optional
        Extra time in days to add to the time ranges after the end.

    """
    # Argument processing
    mission_ids_str = ", ".join("'{}'".format(x) for x in mission_ids)
    extra_time_in_ms = (
        extra_time_in_days * 24 * 60 * 60 * 1000
    )  # 1d=24h 1h=60m 1m=60s 1s=1000ms

    # Get time ranges of all included missions and keep unique ones
    query = f"SELECT start_timestamp, end_timestamp FROM missions WHERE mission_id IN ({mission_ids_str}) ORDER BY creation_timestamp;"
    timestamp_pairs = utils.execute_query(con, query)
    timestamp_pairs = set(timestamp_pairs)

    # Create timerange conditions: Only consider entities created between start and end (+chosen extra time) of some mission
    sql_line = "(creation_timestamp >= {} AND creation_timestamp <= {})"
    sql_timerange_conditions = [
        sql_line.format(start, end + extra_time_in_ms)
        for start, end in set(timestamp_pairs)
    ]
    sql_timerange_conditions = "\n        OR\n        ".join(sql_timerange_conditions)

    # Create views
    script_template = pkg_resources.resource_string(
        __name__, "create_filter_views.sql"
    ).decode()
    script = script_template.format(
        mission_ids=mission_ids_str,
        filter_id=filter_id,
        timerange_conditions="1=1",  # TODO: sql_timerange_conditions,
    )
    utils.execute_script(con, script)


def create_counts_table(con: sqlite3.Connection, filter_id: int) -> None:
    """Create a database table with counts of each user activity.

    The counts are based on the views that correspond to the given filter ID.

    Parameters
    ----------
    con : Connection
        The connection object to the SQLite database.
    filter_id : int
        The ID of the filter to create counts for.

    """
    script_template = pkg_resources.resource_string(
        __name__, "create_counts_table.sql"
    ).decode()
    script = script_template.format(
        filter_id=filter_id,
        positive_reactions="'celebrate', 'clap', 'curious', 'genius', 'happy', 'hot', 'laugh', 'love'",
        negative_reactions="'anger', 'sad'",
    )
    utils.execute_script(con, script)


def create_contribution_score_table(
    con: sqlite3.Connection,
    filter_id: int,
    variables_id: int,
    variables: Optional[Dict[str, int]] = None,
) -> None:
    """Create a database table with contribution scores for each user activity and their sum.

    The contribution scores are calculated from

    1) counts based on the views that correspond to the given filter ID
    2) user-provided variables that define how to weight each count

    Parameters
    ----------
    con : Connection
        The connection object to the SQLite database.
    filter_id : int
        The ID of the filter to create contribution scores for.
    variables_id : int
        The ID of the variables to use for calculating the contribution scores.
    variables : dict, optional
        Custom variables and their corresponding values to be used in the calculation. Defaults to None.

    """
    # Argument processing
    table_name_counts = f"filter{filter_id}_counts"
    table_name_contribution_scores = f"filter{filter_id}_var{variables_id}_scores"

    # TODO: provide suggestions in the app, not here
    if variables is None:
        positive_reaction_received = 2
        negative_reaction_received = -2
        variables = {
            "proposals_created": 0,
            "fraction_of_contribution_scores_for_highly_rated_proposals": 0.0,
            "ratings_created": 0,
            "ratings_received": 0,
            "comments_created": 3,
            "comments_received": 0,
            "upvote_reactions_created": 0,
            "downvote_reactions_created": 0,
            "anger_reactions_created": 0,
            "celebrate_reactions_created": 0,
            "clap_reactions_created": 0,
            "curious_reactions_created": 0,
            "genius_reactions_created": 0,
            "happy_reactions_created": 0,
            "hot_reactions_created": 0,
            "laugh_reactions_created": 0,
            "love_reactions_created": 0,
            "sad_reactions_created": 0,
            "upvote_reactions_received": 2,
            "downvote_reactions_received": -3,
            "anger_reactions_received": negative_reaction_received,
            "celebrate_reactions_received": positive_reaction_received,
            "clap_reactions_received": positive_reaction_received,
            "curious_reactions_received": positive_reaction_received,
            "genius_reactions_received": positive_reaction_received,
            "happy_reactions_received": positive_reaction_received,
            "hot_reactions_received": positive_reaction_received,
            "laugh_reactions_received": positive_reaction_received,
            "love_reactions_received": positive_reaction_received,
            "sad_reactions_received": negative_reaction_received,
        }

    # Create table with contribution scores
    script_template = pkg_resources.resource_string(
        __name__, "create_contribution_score_table.sql"
    ).decode()
    script = script_template.format(
        table_name_counts=table_name_counts,
        table_name_contribution_scores=table_name_contribution_scores,
        **variables,
    )
    utils.execute_script(con, script)


def create_rewards_table(
    con: sqlite3.Connection,
    filter_id: int,
    variables_id: int,
    distribution_id: int,
    filtered_user_ids=None,
    function_agix_reward="x",
    function_voting_weight="x",
    threshold_percentile=20.0,
    total_agix_reward=100_000.0,
    min_voting_weight=1.0,
    max_voting_weight=5.0,
):
    # Argument processing
    table_name_contribution_scores = f"filter{filter_id}_var{variables_id}_scores"
    table_name_rewards = (
        f"filter{filter_id}_var{variables_id}_dist{distribution_id}_rewards"
    )

    # Filtered users
    if filtered_user_ids is not None:
        filtered_user_ids = ",".join(f'"{uid}"' for uid in filtered_user_ids)
    else:
        filtered_user_ids = ""

    # Threshold calculation by percentile
    query = f"SELECT contribution_score FROM {table_name_contribution_scores} WHERE contribution_score > 0.0;"
    contribution_scores = [row[0] for row in utils.execute_query(con, query)]
    threshold_value = np.percentile(contribution_scores, threshold_percentile)

    # Distribution calculation by provided functions
    math_functions = dict(
        abs=np.abs,
        ceil=np.ceil,
        floor=np.floor,
        mod=np.mod,
        sqrt=np.sqrt,
        cbrt=np.cbrt,
        sin=np.sin,
        cos=np.cos,
        tan=np.tan,
        arcsin=np.arcsin,
        arccos=np.arccos,
        arctan=np.arctan,
        cosh=np.cosh,
        sinh=np.sinh,
        tanh=np.tanh,
        arcsinh=np.arcsinh,
        arccosh=np.arccosh,
        arctanh=np.arctanh,
        exp=np.exp,
        e=np.exp,
        ln=np.log,
        log=np.log,
        log2=np.log2,
        log10=np.log10,
    )

    def calc_agix_distribution(x):
        try:
            x = float(x)
            scope = math_functions.copy()
            scope["x"] = x
            y = eval(function_agix_reward, scope)
        except Exception:
            y = 0.0
        return y

    def calc_vw_distribution(x):
        try:
            x = float(x)
            scope = math_functions.copy()
            scope["x"] = x
            y = eval(function_voting_weight, scope)
        except Exception:
            y = 0.0
        return y

    con.create_function("calc_agix_distribution", 1, calc_agix_distribution)
    con.create_function("calc_vw_distribution", 1, calc_vw_distribution)

    # Create table with rewards
    script_template = pkg_resources.resource_string(
        __name__, "create_rewards_table.sql"
    ).decode()
    script = script_template.format(
        table_name_contribution_scores=table_name_contribution_scores,
        table_name_rewards=table_name_rewards,
        filtered_user_ids=filtered_user_ids,
        threshold_value=threshold_value,
        total_agix_reward=total_agix_reward,
        min_voting_weight=min_voting_weight,
        max_voting_weight=max_voting_weight,
    )
    utils.execute_script(con, script)


def get_mission_information(
    con: sqlite3.Connection,
) -> List[Tuple[str, str, int, str, int, str]]:
    """Retrieve information about all missions contained in the database.

    Parameters
    ----------
    con : Connection
        The connection object to the SQLite database.

    Returns
    -------
    List[Tuple[str, str, int, str, int, str]]
        A list of tuples containing mission information. Each tuple contains:
        - mission_id: str
        - title: str
        - start_timestamp: int
        - start_datetime: str
        - end_timestamp: int
        - end_datetime: str

    """
    query = "SELECT mission_id, title, start_timestamp, start_datetime, end_timestamp, end_datetime FROM missions ORDER BY creation_timestamp;"
    result = utils.execute_query(con, query)
    return result


def get_user_information(con: sqlite3.Connection, filter_id=None):
    # TODO: docstring
    if filter_id is None:
        query = "SELECT user_id, name FROM users ORDER BY user_id;"
    else:
        table_name = f"filter{filter_id}_counts"
        query = f"SELECT {table_name}.user_id, users.name FROM {table_name} LEFT JOIN users USING (user_id) ORDER BY user_id;"
    result = utils.execute_query(con, query)
    return result


def get_contribution_scores(con: sqlite3.Connection, filter_id: int, variables_id: int):
    # TODO: docstring
    table_name_contribution_scores = f"filter{filter_id}_var{variables_id}_scores"
    query = f"SELECT user_id, contribution_score FROM {table_name_contribution_scores} WHERE contribution_score > 0.0 ORDER BY contribution_score DESC, user_id DESC;"
    result = utils.execute_query(con, query)
    return result
