"""Module for retrieving information from the SQLite database."""

import sqlite3
from typing import List, Tuple, Union

from . import utils


def get_missions(
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


def get_users(
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
    """Retrieve information about users with engagement scores.

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
    """Retrieve information about users with rewards (AGIX, voting weight).

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
