"""Module for combining different functionality in higher-level functions."""

import sqlite3
from typing import Dict, List, Tuple

from .derive import (
    create_counts_table,
    create_engagement_score_table,
    create_filter_views,
    create_rewards_table,
)
from .extract import extract_swae_data
from .load import load_sqlite
from .retrieve import get_engagement_scores, get_missions, get_rewards
from .transform import transform_swae_data
from .visualize import plot_rewards


FILTER_ID = 0
VARIABLES_ID = 0
DISTRIBUTION_ID = 0


def zip_to_sqlite(
    source_filepath: str, target_filepath: str = ":memory:", filters_on: bool = True
) -> sqlite3.Connection:
    """Extract, transform and load semi-structured data from a ZIP file into an SQLite database.

    Parameters
    ----------
    source_filepath : str
        The path of the ZIP file, which contains a data export of Swae
        in form of multiple JSON files.
    target_filepath : str, optional, default=":memory:"
        The path of the SQLite database file to create.
        Default is an in-memory database (":memory:").
        Caution: If the file exists it will be overwritten.
    filters_on : bool, optional, default=True
        A flag that determines whether filters are enabled for the transformation.
        If True, individual rows can be skipped if they carry an attribute that indicates that
        they are inactive, e.g. a proposal being in draft status or a comment being deleted.

    Returns
    -------
    con : sqlite3.Connection
        The SQLite database connection object.

    """
    # Extract
    json_data = extract_swae_data(source_filepath)

    # Transform
    tabular_data = transform_swae_data(json_data, filters_on)

    # Load
    con = load_sqlite(tabular_data, target_filepath)
    return con


def sqlite_to_scores_and_rewards(
    con: sqlite3.Connection,
    mission_ids: List[str] = None,
    variables: Dict = None,
    filtered_user_ids: List[str] = None,
    function_agix_reward: callable = "x",
    function_voting_weight: callable = "x",
    inline: bool = False,
) -> List[Tuple]:
    """Calculate community engagement scores based on provided SQLite data.

    Parameters
    ----------
    con : sqlite3.Connection
        The SQLite database connection object.
    mission_ids : List[str], optional
        A list of mission IDs to generate scores for.
        If None, scores will be generated for all missions.
    variables : Dict, optional
        A list of variables used for scoring.
        If None, default values will be used.
    filtered_user_ids : List[str], optional
        A list of user IDs to filter for reward calculation.
        If None, no filtering will be applied.
    function_agix_reward : callable, optional, default="x"
        A custom function to calculate AGIX rewards for users.
    function_voting_weight : callable, optional, default="x"
        A custom function to calculate voting weight for users.
    inline : bool, optional, default=False
        Flag to specify whether to display generated plots inline.

    Returns
    -------
    results : List[Tuple]
        A list of engagement scores calculated for the specified missions.

    """
    # Argument processing
    if mission_ids is None:
        all_missions = get_missions(con)
        mission_ids = [m[0] for m in all_missions]
    if variables is None:
        variables = {
            "proposals_created": 0,
            "ratings_created": 0,
            "ratings_received": 0,
            "comments_created": 3,
            "comments_received": 0,
            "upvote_reactions_created": 0,
            "downvote_reactions_created": 0,
            "celebrate_reactions_created": 0,
            "clap_reactions_created": 0,
            "curious_reactions_created": 0,
            "genius_reactions_created": 0,
            "happy_reactions_created": 0,
            "hot_reactions_created": 0,
            "laugh_reactions_created": 0,
            "love_reactions_created": 0,
            "anger_reactions_created": 0,
            "sad_reactions_created": 0,
            "upvote_reactions_received": 2,
            "downvote_reactions_received": -3,
            "celebrate_reactions_received": 2,
            "clap_reactions_received": 2,
            "curious_reactions_received": 2,
            "genius_reactions_received": 2,
            "happy_reactions_received": 2,
            "hot_reactions_received": 2,
            "laugh_reactions_received": 2,
            "love_reactions_received": 2,
            "anger_reactions_received": -2,
            "sad_reactions_received": -2,
            "fraction_of_engagement_scores_for_highly_rated_proposals": 0.0,
        }
    if filtered_user_ids is None:
        filtered_user_ids = []

    global FILTER_ID
    global VARIABLES_ID
    global DISTRIBUTION_ID
    FILTER_ID += 1
    VARIABLES_ID += 1
    DISTRIBUTION_ID += 1

    # Data selection
    create_filter_views(con, FILTER_ID, mission_ids)

    # Activity counts
    create_counts_table(con, FILTER_ID)

    # Engagement scores
    create_engagement_score_table(con, FILTER_ID, VARIABLES_ID, variables)

    # Rewards
    create_rewards_table(
        con,
        FILTER_ID,
        VARIABLES_ID,
        DISTRIBUTION_ID,
        threshold_percentile=10,
        filtered_user_ids=filtered_user_ids,
        function_agix_reward=function_agix_reward,
        function_voting_weight=function_voting_weight,
    )

    # Retrieve data to return
    engagement_scores = get_engagement_scores(con, FILTER_ID, VARIABLES_ID)
    rewards = get_rewards(con, FILTER_ID, VARIABLES_ID, DISTRIBUTION_ID)
    figures = plot_rewards(con, FILTER_ID, VARIABLES_ID, DISTRIBUTION_ID, inline)
    return engagement_scores, rewards, figures
