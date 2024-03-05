#!/usr/bin/env python
# coding: utf-8

# Community Engagement Scores
# This python script demonstrates how to use the package `ces` for calculating Community Engagement Scores (CES) in a minimalistic way. As input it uses a data export from Swae (`raw.zip`) and as output it generates engagement scores, rewards and plots.

import os

from ces import swae_analysis as swa

# Define input and output locations

in_dir = os.path.join('..', 'tests', 'input')
in_zip_filepath = os.path.join(in_dir, 'raw.zip')
in_csv_filepath = os.path.join(in_dir, 'dfr2_results_extracted.csv')

out_dir = 'output'
out_sqlite_filepath = os.path.join(out_dir, 'deep_funding_round_2.sqlite')
out_excel_filepath = os.path.join(out_dir, 'deep_funding_round_2.xlsx')


# Convert Swae data to SQLite
# Extract, transform and load (ETL) data from multiple semi-structured JSON files into a single structured SQLite database
con = swa.zip_to_sqlite(in_zip_filepath, out_sqlite_filepath, filters_on=False)


# Calculate engagement scores and rewards
mission_ids = [
    'ceb335c2-ba7f-4aa7-939a-4d1c97294865',
    '27842bc3-83b7-4aef-ad75-2ef7c8938755',
    '8fec6dee-3831-462a-b1fc-2ebe562db79d',
    'cccaa945-e5c3-49ae-832f-055ddd4e180f',
    'de5c7837-32c0-4337-8a73-62beb4da1f59',
]

variables_dfr2 = {
    'proposals_created': 0,
    'ratings_created': 0,
    'ratings_received': 0,
    'comments_created': 3,
    'comments_received': 0,
    'upvote_reactions_created': 0,
    'downvote_reactions_created': 0,
    'celebrate_reactions_created': 0,
    'clap_reactions_created': 0,
    'curious_reactions_created': 0,
    'genius_reactions_created': 0,
    'happy_reactions_created': 0,
    'hot_reactions_created': 0,
    'laugh_reactions_created': 0,
    'love_reactions_created': 0,
    'anger_reactions_created': 0,
    'sad_reactions_created': 0,
    'upvote_reactions_received': 2,
    'downvote_reactions_received': -3,
    'celebrate_reactions_received': 2,
    'clap_reactions_received': 2,
    'curious_reactions_received': 2,
    'genius_reactions_received': 2,
    'happy_reactions_received': 2,
    'hot_reactions_received': 2,
    'laugh_reactions_received': 2,
    'love_reactions_received': 2,
    'anger_reactions_received': -2,
    'sad_reactions_received': -2,    
    'fraction_of_engagement_scores_for_highly_rated_proposals': 0.0,
}

filtered_user_ids = [
    'jan.horlings@singularitynet.io',
    'janhorlings@gmail.com',
]

scores, rewards, figures = swa.sqlite_to_scores_and_rewards(
    con,
    mission_ids=mission_ids,
    variables=variables_dfr2,
    filtered_user_ids=filtered_user_ids,
    function_agix_reward="x**2",
    function_voting_weight="x**2",
    inline=True,
)

print("{:50}{}".format("User ID", "Engagement score"))
for uid, score in scores:
    print("{:50}{}".format(uid, score))
