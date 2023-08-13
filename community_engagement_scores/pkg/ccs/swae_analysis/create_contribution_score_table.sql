-- Calculate points for user activities, depending on given variables
CREATE TABLE {table_name_contribution_scores} AS
SELECT
    user_id,

    num_created_proposals * {proposals_created} AS pts_proposals_created,

    num_created_ratings * {ratings_created} AS pts_ratings_created,
    num_received_ratings * {ratings_received} AS pts_ratings_received,

    num_created_comments * {comments_created} AS pts_comments_created,
    num_received_comments * {comments_received} AS pts_comments_received,

    num_created_upvote_reactions * {upvote_reactions_created} AS pts_upvote_reactions_created,
    num_created_downvote_reactions * {downvote_reactions_created} AS pts_downvote_reactions_created,
    num_created_anger_reactions * {anger_reactions_created} AS pts_anger_reactions_created,
    num_created_celebrate_reactions * {celebrate_reactions_created} AS pts_celebrate_reactions_created,
    num_created_clap_reactions * {clap_reactions_created} AS pts_clap_reactions_created,
    num_created_curious_reactions * {curious_reactions_created} AS pts_curious_reactions_created,
    num_created_genius_reactions * {genius_reactions_created} AS pts_genius_reactions_created,
    num_created_happy_reactions * {happy_reactions_created} AS pts_happy_reactions_created,
    num_created_hot_reactions * {hot_reactions_created} AS pts_hot_reactions_created,
    num_created_laugh_reactions * {laugh_reactions_created} AS pts_laugh_reactions_created,
    num_created_love_reactions * {love_reactions_created} AS pts_love_reactions_created,
    num_created_sad_reactions * {sad_reactions_created} AS pts_sad_reactions_created,

    num_received_upvote_reactions * {upvote_reactions_received} AS pts_upvote_reactions_received,
    num_received_downvote_reactions * {downvote_reactions_received} AS pts_downvote_reactions_received,
    num_received_anger_reactions * {anger_reactions_received} AS pts_anger_reactions_received,
    num_received_celebrate_reactions * {celebrate_reactions_received} AS pts_celebrate_reactions_received,
    num_received_clap_reactions * {clap_reactions_received} AS pts_clap_reactions_received,
    num_received_curious_reactions * {curious_reactions_received} AS pts_curious_reactions_received,
    num_received_genius_reactions * {genius_reactions_received} AS pts_genius_reactions_received,
    num_received_happy_reactions * {happy_reactions_received} AS pts_happy_reactions_received,
    num_received_hot_reactions * {hot_reactions_received} AS pts_hot_reactions_received,
    num_received_laugh_reactions * {laugh_reactions_received} AS pts_laugh_reactions_received,
    num_received_love_reactions * {love_reactions_received} AS pts_love_reactions_received,
    num_received_sad_reactions * {sad_reactions_received} AS pts_sad_reactions_received,

    NULL AS pts_total_reactions_created,
    NULL AS pts_total_reactions_received,
    NULL AS pts_for_activities,
    NULL AS pts_for_ratings_received,
    NULL AS contribution_score
FROM {table_name_counts}
LEFT JOIN users USING (user_id);


UPDATE {table_name_contribution_scores}
SET pts_total_reactions_created = pts_upvote_reactions_created
    + pts_downvote_reactions_created
    + pts_anger_reactions_created
    + pts_celebrate_reactions_created
    + pts_clap_reactions_created
    + pts_curious_reactions_created
    + pts_genius_reactions_created
    + pts_happy_reactions_created
    + pts_hot_reactions_created
    + pts_laugh_reactions_created
    + pts_love_reactions_created
    + pts_sad_reactions_created,

    pts_total_reactions_received = pts_upvote_reactions_received
    + pts_downvote_reactions_received
    + pts_anger_reactions_received
    + pts_celebrate_reactions_received
    + pts_clap_reactions_received
    + pts_curious_reactions_received
    + pts_genius_reactions_received
    + pts_happy_reactions_received
    + pts_hot_reactions_received
    + pts_laugh_reactions_received
    + pts_love_reactions_received
    + pts_sad_reactions_received;


UPDATE {table_name_contribution_scores}
SET pts_for_activities = pts_proposals_created
    + pts_ratings_created
    + pts_ratings_received
    + pts_comments_created
    + pts_comments_received
    + pts_total_reactions_created
    + pts_total_reactions_received,

    pts_for_ratings_received = (
        SELECT weight_received_ratings
        FROM {table_name_counts}
        WHERE {table_name_contribution_scores}.user_id={table_name_counts}.user_id
    );


-- Scale the points received for proposal ratings, so they become a user-specified fraction of the total points (=contribution score)
UPDATE {table_name_contribution_scores}
SET pts_for_ratings_received = pts_for_ratings_received * (
    SELECT
        {fraction_of_contribution_scores_for_highly_rated_proposals} / (1.0 - {fraction_of_contribution_scores_for_highly_rated_proposals}) *
        SUM(pts_for_activities) / SUM(pts_for_ratings_received)
    FROM {table_name_contribution_scores}
);


UPDATE {table_name_contribution_scores}
SET contribution_score = pts_for_activities + pts_for_ratings_received;