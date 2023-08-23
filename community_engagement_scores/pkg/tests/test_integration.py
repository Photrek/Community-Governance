import os

import pandas as pd

from ces import swae_analysis as swa


ZIP_FILEPATH = os.path.join("input", "raw.zip")


def test_all_database_calculations_and_corresponding_file_exports(tmpdir):
    # ETL
    json_data = swa.extract_swae_data(ZIP_FILEPATH)
    tabular_data = swa.transform_swae_data(json_data)
    assert len(tabular_data) > 0
    con = swa.load_sqlite(tabular_data)

    # Export 1
    dirpath1 = os.path.join(tmpdir, "test1_csv")
    swa.sqlite_to_csv(con, dirpath1)
    assert os.path.isdir(dirpath1)
    assert len(os.listdir(dirpath1)) > 0

    filepath1 = os.path.join(tmpdir, "test1.xlsx")
    swa.sqlite_to_excel(con, filepath1)
    assert os.path.isfile(filepath1)

    # Score calculation
    all_missions = swa.get_missions(con)
    selected_missions = [m for m in all_missions if m[1].startswith("Round 1")]
    selected_mission_ids = [m[0] for m in selected_missions]
    filter_id = 1
    variables_id = 1
    swa.create_filter_views(con, filter_id, selected_mission_ids)
    swa.create_counts_table(con, filter_id)
    swa.create_engagement_score_table(con, filter_id, variables_id)

    filter_id2 = 42
    swa.create_filter_views(con, filter_id2, selected_mission_ids[:-1])
    swa.create_counts_table(con, filter_id2)

    # Export 2 - includes scores
    dirpath2 = os.path.join(tmpdir, "test2_csv")
    swa.sqlite_to_csv(con, dirpath2)
    assert os.path.isdir(dirpath2)
    assert len(os.listdir(dirpath2)) > 0

    filepath2 = os.path.join(tmpdir, "test2.xlsx")
    swa.sqlite_to_excel(con, filepath2)
    assert os.path.isfile(filepath2)

    # Reward calculation
    distribution_id = 1
    swa.create_rewards_table(con, filter_id, variables_id, distribution_id)

    distribution_id = 2
    filtered_user_ids = ["jan.horlings@singularitynet.io"]
    swa.create_rewards_table(
        con, filter_id, variables_id, distribution_id, filtered_user_ids
    )

    # Export 3 - includes rewards
    dirpath3 = os.path.join(tmpdir, "test3_csv")
    swa.sqlite_to_csv(con, dirpath3)
    assert os.path.isdir(dirpath3)
    assert len(os.listdir(dirpath3)) > 0

    filepath3 = os.path.join(tmpdir, "test3.xlsx")
    swa.sqlite_to_excel(con, filepath3)
    assert os.path.isfile(filepath3)

    # Expected differences in size of the exports
    s1 = len(os.listdir(dirpath1))
    s2 = len(os.listdir(dirpath2))
    s3 = len(os.listdir(dirpath3))
    assert s1 < s2 < s3

    s1 = os.path.getsize(filepath1)
    s2 = os.path.getsize(filepath2)
    s3 = os.path.getsize(filepath3)
    assert s1 < s2 < s3

    # Fetch user info
    users1 = swa.get_users(con)
    users2 = swa.get_users(con, filter_id=filter_id)
    users3 = swa.get_users(con, filter_id=filter_id2)
    assert len(users1) > len(users2) > len(users3)

    # Create plots
    figures = swa.plot_rewards(con, filter_id, variables_id, distribution_id)
    assert figures is not None

    # Create network
    mission_id = selected_mission_ids[0]
    graph = swa.sqlite_to_graph(con, mission_id)
    assert graph is not None

    con.close()


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
    conn = swa.zip_to_sqlite(zip_filepath, ":memory:", filters_on=False)
    mission_info = swa.get_missions(conn)
    mission_ids = [x[0] for x in mission_info if x[1].startswith("Round 2")]
    filter_id = 100
    variables_id = 1
    swa.create_filter_views(conn, filter_id, mission_ids, extra_time_in_days=filter_id)
    swa.create_counts_table(conn, filter_id)
    swa.create_engagement_score_table(conn, filter_id, variables_id=variables_id)
    data = swa.get_engagement_scores(conn, filter_id, variables_id)
    df2 = pd.DataFrame(data, columns=["user_id", "engagement_score"])

    # Compare the results
    assert (df1.values == df2.values).all()

    # Calculate points with this package and filtering of deleted objects
    conn = swa.zip_to_sqlite(zip_filepath, ":memory:")
    mission_info = swa.get_missions(conn)
    mission_ids = [x[0] for x in mission_info if x[1].startswith("Round 2")]
    filter_id = 100
    variables_id = 1
    swa.create_filter_views(conn, filter_id, mission_ids, extra_time_in_days=filter_id)
    swa.create_counts_table(conn, filter_id)
    swa.create_engagement_score_table(conn, filter_id, variables_id=variables_id)
    data = swa.get_engagement_scores(conn, filter_id, variables_id)
    df2 = pd.DataFrame(data, columns=["user_id", "engagement_score"])

    # Compare the results
    assert df1.shape != df2.shape
