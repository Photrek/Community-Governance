"""Module for deriving counts, scores and rewards from preprocessed Swae data."""

import sqlite3
from typing import Any, Dict, List, Tuple, Union

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
    con : sqlite3.Connection
        The SQLite database connection object.
    filter_id : int
        The ID of the filter to create. It will be used in a prefix for each created view.
    mission_ids : List[str]
        A list of mission identifiers.
    extra_time_in_days : int, optional, default=30
        Extra time in days to add to the time ranges after the end.

    """
    # Argument processing
    mission_ids_str = ", ".join("'{}'".format(x) for x in mission_ids)
    extra_time_in_ms = (
        extra_time_in_days * 24 * 60 * 60 * 1000
    )  # 1d=24h 1h=60m 1m=60s 1s=1000ms

    # Get time ranges of all included missions and keep unique ones
    query = (
        "SELECT start_timestamp, end_timestamp FROM missions "
        f"WHERE mission_id IN ({mission_ids_str}) ORDER BY creation_timestamp;"
    )
    timestamp_pairs = utils.execute_query(con, query)
    timestamp_pairs = set(timestamp_pairs)

    # Create timerange conditions: Only consider entities created between start and end
    # (+chosen extra time) of some mission
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
        timerange_conditions=sql_timerange_conditions,
    )
    utils.execute_script(con, script)


def create_counts_table(con: sqlite3.Connection, filter_id: int) -> None:
    """Create a database table with counts of each user activity.

    The counts are based on the views that correspond to the given filter ID.

    Parameters
    ----------
    con : sqlite3.Connection
        The SQLite database connection object.
    filter_id : int
        The ID of the filter to create counts for.

    """
    script_template = pkg_resources.resource_string(
        __name__, "create_counts_table.sql"
    ).decode()
    script = script_template.format(
        filter_id=filter_id,
        positive_reactions=(
            "'celebrate', 'clap', 'curious', 'genius', "
            "'happy', 'hot', 'laugh', 'love'"
        ),
        negative_reactions="'anger', 'sad'",
    )
    utils.execute_script(con, script)


def create_engagement_score_table(
    con: sqlite3.Connection,
    filter_id: int,
    variables_id: int,
    variables: Dict[str, Any] = None,
) -> None:
    """Create a database table with engagement scores for each user activity and their sum.

    The engagement scores are calculated from

    1) counts based on the views that correspond to the given filter ID
    2) user-provided variables that define how to weight each count

    Parameters
    ----------
    con : sqlite3.Connection
        The SQLite database connection object.
    filter_id : int
        The ID of the filter to create engagement scores for.
    variables_id : int
        The ID of the variables to use for calculating the engagement scores.
    variables : Dict[str, Any], optional
        Custom variables and their corresponding values to be used in the
        calculation.

    """
    # Argument processing
    table_name_counts = f"filter{filter_id}_counts"
    table_name_engagement_scores = f"filter{filter_id}_var{variables_id}_scores"

    if variables is None:
        positive_reaction_received = 2
        negative_reaction_received = -2
        variables = {
            "proposals_created": 0,
            "fraction_of_engagement_scores_for_highly_rated_proposals": 0.0,
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

    # Create table with engagement scores
    script_template = pkg_resources.resource_string(
        __name__, "create_engagement_score_table.sql"
    ).decode()
    script = script_template.format(
        table_name_counts=table_name_counts,
        table_name_engagement_scores=table_name_engagement_scores,
        **variables,
    )
    utils.execute_script(con, script)


def create_rewards_table(
    con: sqlite3.Connection,
    filter_id: int,
    variables_id: int,
    distribution_id: int,
    filtered_user_ids: Union[str, None] = None,
    function_agix_reward: str = "x",
    function_voting_weight: str = "x",
    threshold_percentile: float = 20.0,
    total_agix_reward: float = 100_000.0,
    min_voting_weight: float = 1.0,
    max_voting_weight: float = 5.0,
) -> None:
    """Create a table with rewards based on engagement scores and provided functions.

    Parameters
    ----------
    con : sqlite3.Connection
        The SQLite database connection object.
    filter_id : int
        The ID of the filter.
    variables_id : int
        The ID of the variables.
    distribution_id : int
        The ID of the distribution.
    filtered_user_ids : Union[str, None], optional, default=None
        Comma-separated list of filtered user IDs.
    function_agix_reward : str, optional, default="x"
        Function expression for calculating AGIX reward.
    function_voting_weight : str, optional, default="x"
        Function expression for calculating voting weight.
    threshold_percentile : float, optional, default=20.0
        Percentile threshold for engagement scores.
    total_agix_reward : float, optional, default=100_000.0
        Total AGIX reward to distribute among users who have high enough engagement scores.
    min_voting_weight : float, optional, default=1.0
        Minimum voting weight.
    max_voting_weight : float, optional, default=5.0
        Maximum voting weight.

    """
    # Argument processing
    table_name_engagement_scores = f"filter{filter_id}_var{variables_id}_scores"
    table_name_rewards = (
        f"filter{filter_id}_var{variables_id}_dist{distribution_id}_rewards"
    )

    # Filtered users
    if filtered_user_ids is not None:
        filtered_user_ids = ",".join(f'"{uid}"' for uid in filtered_user_ids)
    else:
        filtered_user_ids = ""

    # Threshold calculation by percentile
    query = (
        f"SELECT engagement_score FROM {table_name_engagement_scores} "
        "WHERE engagement_score > 0.0;"
    )
    engagement_scores = [row[0] for row in utils.execute_query(con, query)]
    threshold_value = np.percentile(engagement_scores, threshold_percentile)

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
        table_name_engagement_scores=table_name_engagement_scores,
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
) -> List[Tuple]:
    """Retrieve information about all missions contained in the database.

    Parameters
    ----------
    con : Connection
        The connection object to the SQLite database.

    Returns
    -------
    mission_info : List[Tuple]
        A list of tuples containing mission information.

        Each tuple has following items:

        - mission_id: str
        - title: str
        - start_timestamp: int
        - start_datetime: str
        - end_timestamp: int
        - end_datetime: str

    """
    query = (
        "SELECT mission_id, title, start_timestamp, start_datetime, "
        "end_timestamp, end_datetime "
        "FROM missions ORDER BY creation_timestamp;"
    )
    result = utils.execute_query(con, query)
    return result


def get_user_information(
    con: sqlite3.Connection, filter_id: Union[int, None] = None
) -> List[Tuple]:
    """Retrieve information about users contained in the database or a subset of it.

    Parameters
    ----------
    con : Connection
        The connection object to the SQLite database.
    filter_id : Union[int, None], optional
        The ID of the filter. If it is provided, only information about users
        contained in the corresponding subset of the database is delivered.

    Returns
    -------
    user_info : List[Tuple]
        A list of tuples containing user information.

        Each tuple has following items:

        - user_id: str
        - name: str

    """
    if filter_id is None:
        query = "SELECT user_id, name FROM users ORDER BY user_id;"
    else:
        # Note: There is no view for filtered users, because it requires walking over
        # all other views, therefore the counts table is used, where this has already been done
        table_name = f"filter{filter_id}_counts"
        query = (
            f"SELECT {table_name}.user_id, users.name FROM {table_name} "
            "LEFT JOIN users USING (user_id) ORDER BY user_id;"
        )
    result = utils.execute_query(con, query)
    return result


def get_engagement_scores(
    con: sqlite3.Connection, filter_id: int, variables_id: int
) -> List[Tuple]:
    """Retrieve information about all users contained in the database.

    Parameters
    ----------
    con : Connection
        The connection object to the SQLite database.
    filter_id : int
        The ID of the filter.
    variables_id : int
        The ID of the variables.

    Returns
    -------
    engagement_score_info : List[Tuple]
        A list of tuples containing engagement score information.

        Each tuple has following items:

        - user_id: str
        - engagement_score: float

    """
    table_name_engagement_scores = f"filter{filter_id}_var{variables_id}_scores"
    query = (
        f"SELECT user_id, engagement_score FROM {table_name_engagement_scores} "
        "WHERE engagement_score > 0.0 ORDER BY engagement_score DESC, user_id DESC;"
    )
    result = utils.execute_query(con, query)
    return result


def get_rewards(
    con: sqlite3.Connection, filter_id: int, variables_id: int, distribution_id: int
) -> List[Tuple]:
    """Retrieve information about all users contained in the database.

    Parameters
    ----------
    con : Connection
        The connection object to the SQLite database.
    filter_id : int
        The ID of the filter.
    variables_id : int
        The ID of the variables.
    distribution_id : int
        The ID of the reward distribution scheme.

    Returns
    -------
    rewards_info : List[Tuple]
        A list of tuples containing reward information.

        Each tuple has following items:

        - user_id: str
        - agix_reward: float
        - voting_weight: float

    """
    table_name_rewards = (
        f"filter{filter_id}_var{variables_id}_dist{distribution_id}_rewards"
    )
    query = (
        f"SELECT user_id, agix_reward, voting_weight FROM {table_name_rewards} "
        "WHERE agix_reward > 0.0 ORDER BY agix_reward DESC, voting_weight DESC, user_id DESC;"
    )
    result = utils.execute_query(con, query)
    return result
