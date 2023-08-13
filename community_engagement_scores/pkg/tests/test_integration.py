import os

import pandas as pd

from ccs import swae_analysis as swa


def test_equality_between_manual_and_automatic_score_calculation_on_deep_funding_round_2():
    zip_filepath = os.path.join(os.path.dirname(__file__), "input", "raw.zip")
    df_filepath = os.path.join(
        os.path.dirname(__file__), "input", "dfr2_results_extracted.csv"
    )

    # Load points from manual calculation in spreadsheet
    df1 = pd.read_csv(df_filepath)
    df1 = df1[["user_id", "contribution_score"]]
    df1 = df1[df1["contribution_score"] > 0]
    df1 = df1.sort_values(
        by=[list(df1.columns)[1], list(df1.columns)[0]], ascending=[False, False]
    )

    # Calculate points with this package
    con = swa.zip_to_sqlite(zip_filepath, ":memory:")
    mission_info = swa.get_mission_information(con)
    mission_ids = [x[0] for x in mission_info if x[1].startswith("Round 2")]
    filter_id = 100
    variables_id = 1
    swa.create_filter_views(con, filter_id, mission_ids, extra_time_in_days=filter_id)
    swa.create_counts_table(con, filter_id)
    swa.create_contribution_score_table(con, filter_id, variables_id=variables_id)
    data = swa.get_contribution_scores(con, filter_id, variables_id)
    df2 = pd.DataFrame(data, columns=["user_id", "contribution_score"])

    # Compare the results
    assert (df1.values == df2.values).all()
