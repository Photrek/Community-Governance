"""Module for visualizing scores and rewards."""

import sqlite3
from typing import List

import matplotlib.figure

from . import utils


def plot_rewards(
    con: sqlite3.Connection,
    filter_id: int,
    variables_id: int,
    distribution_id: int,
    inline=False,
):
    """Create bar plots of users' engagement scores, AGIX rewards, and voting weights.

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
    inline : bool, optional, default=True
        If True, display plots inline in a Jupyter notebook.

    Returns
    -------
    figures : Tuple
        A tuple containing three Matplotlib figure objects:

        - fig1: Figure of user rank vs. engagement scores.
        - fig2: Figure of user rank vs. AGIX rewards.
        - fig3: Figure of user rank vs. voting weights.

    """
    table_name_rewards = (
        f"filter{filter_id}_var{variables_id}_dist{distribution_id}_rewards"
    )

    query = (
        "SELECT rank, engagement_score, agix_reward, voting_weight "
        f"FROM {table_name_rewards} WHERE engagement_score > 0.0 ORDER BY rank;"
    )
    result = utils.execute_query(con, query)

    ranks, engagement_scores, agix_rewards, voting_weights = list(zip(*result))
    fig1 = _create_bar_plot(
        ranks, engagement_scores, "User rank", "Engagement score", "black", inline
    )
    fig2 = _create_bar_plot(
        ranks, agix_rewards, "User rank", "AGIX reward", "blue", inline
    )
    fig3 = _create_bar_plot(
        ranks, voting_weights, "User rank", "Voting weight", "green", inline
    )
    return fig1, fig2, fig3


def _create_bar_plot(
    x: List[float],
    y: List[float],
    x_label: str = None,
    y_label: str = None,
    color: str = "black",
    inline: bool = False,
) -> matplotlib.figure.Figure:
    """Create a bar plot with optional axis labels using Matplotlib.

    Parameters
    ----------
    x : List[float]
        x axis data.
    y : List[float]
        y axis data.
    x_label : str, optional, default=None
        Label for the x axis.
    y_label : str, optional, default=None
        Label for the y axis.
    color : str, optional, default="black"
        Color of the bars and labels.
    inline : bool, optional, default=False
        If True, display the plot inline in a Jupyter notebook.

    Returns
    -------
    fig : matplotlib.figure.Figure
        The created Matplotlib figure containing the bar plot.

    """
    if not inline:
        matplotlib.use("agg")

    import matplotlib.pyplot as plt

    matplotlib.rcParams["figure.dpi"] = 400

    fig, ax = plt.subplots(figsize=(12, 5))
    ax.bar(x, y, color=color, width=0.5)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    interval = 10
    ticks = [i * interval for i in range(len(x) // interval + 1)]
    ticks[0] = 1
    ax.set_xticks(ticks)
    ax.set_xticklabels(ticks)
    if x_label:
        ax.set_xlabel(x_label, color=color)
    if y_label:
        ax.set_ylabel(y_label, color=color)
    return fig
