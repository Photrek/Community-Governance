import sqlite3

from . import utils


def visualize_rewards(
    con: sqlite3.Connection, filter_id: int, variables_id: int, distribution_id: int
):
    table_name_rewards = (
        f"filter{filter_id}_var{variables_id}_dist{distribution_id}_rewards"
    )

    query = f"SELECT rank, contribution_score, agix_reward, voting_weight FROM {table_name_rewards} WHERE contribution_score > 0.0 ORDER BY rank;"
    result = utils.execute_query(con, query)

    ranks, contribution_scores, agix_rewards, voting_weights = list(zip(*result))
    fig1 = _create_bar_plot(
        ranks, contribution_scores, "User rank", "Contribution score", "black"
    )
    fig2 = _create_bar_plot(ranks, agix_rewards, "User rank", "AGIX reward", "blue")
    fig3 = _create_bar_plot(
        ranks, voting_weights, "User rank", "Voting weight", "green"
    )
    return fig1, fig2, fig3


def _create_bar_plot(x, y, x_label=None, y_label=None, color="black", inline=False):
    import matplotlib

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
