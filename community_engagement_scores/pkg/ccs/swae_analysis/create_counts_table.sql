CREATE TABLE filter{filter_id}_counts AS
SELECT
    user_id,
    0 AS num_created_proposals,

    0 AS num_created_ratings,
    0 AS num_received_ratings,
    0.0 AS weight_received_ratings,

    0 AS num_created_comments,
    0 AS num_received_comments,

    0 AS num_created_reactions,
    0 AS num_created_positive_reactions,
    0 AS num_created_negative_reactions,
    0 AS num_created_upvote_reactions,
    0 AS num_created_downvote_reactions,
    0 AS num_created_anger_reactions,
    0 AS num_created_celebrate_reactions,
    0 AS num_created_clap_reactions,
    0 AS num_created_curious_reactions,
    0 AS num_created_genius_reactions,
    0 AS num_created_happy_reactions,
    0 AS num_created_hot_reactions,
    0 AS num_created_laugh_reactions,
    0 AS num_created_love_reactions,
    0 AS num_created_sad_reactions,

    0 AS num_received_reactions,
    0 AS num_received_positive_reactions,
    0 AS num_received_negative_reactions,
    0 AS num_received_upvote_reactions,
    0 AS num_received_downvote_reactions,
    0 AS num_received_anger_reactions,
    0 AS num_received_celebrate_reactions,
    0 AS num_received_clap_reactions,
    0 AS num_received_curious_reactions,
    0 AS num_received_genius_reactions,
    0 AS num_received_happy_reactions,
    0 AS num_received_hot_reactions,
    0 AS num_received_laugh_reactions,
    0 AS num_received_love_reactions,
    0 AS num_received_sad_reactions
FROM users;



-- num_created_proposals
WITH created_proposals AS (
    SELECT user_id, COUNT(user_id) AS num_created_proposals
    FROM filter{filter_id}_proposals
    GROUP BY user_id
)
UPDATE filter{filter_id}_counts
SET num_created_proposals = created_proposals.num_created_proposals
FROM created_proposals
WHERE filter{filter_id}_counts.user_id = created_proposals.user_id;



-- num_created_ratings
WITH created_ratings AS (
    SELECT user_id, COUNT(user_id) AS num_created_ratings
    FROM ratings
    GROUP BY user_id
)
UPDATE filter{filter_id}_counts
SET num_created_ratings = created_ratings.num_created_ratings
FROM created_ratings
WHERE filter{filter_id}_counts.user_id = created_ratings.user_id;



-- num_received_ratings
WITH proposals_x_ratings AS (
    SELECT filter{filter_id}_proposals.user_id AS user_id
    FROM filter{filter_id}_ratings
    LEFT JOIN filter{filter_id}_proposals
    USING (proposal_id)
    -- RIGHT JOIN would be a more natural choice here,
    -- but is only supported in SQLite 3.39.0 onwards
),
received_ratings AS (
    SELECT user_id, COUNT(user_id) AS num_received_ratings
    FROM proposals_x_ratings
    GROUP BY user_id
)
UPDATE filter{filter_id}_counts
SET num_received_ratings = received_ratings.num_received_ratings
FROM received_ratings
WHERE filter{filter_id}_counts.user_id = received_ratings.user_id;



-- weight_received_ratings
WITH received_rating_weight AS (
    SELECT user_id, MAX(SUM(average_rating * num_total_ratings), 0.0) AS weight_received_ratings
    FROM filter{filter_id}_proposals
    GROUP BY user_id
)
UPDATE filter{filter_id}_counts
SET weight_received_ratings = received_rating_weight.weight_received_ratings
FROM received_rating_weight
WHERE filter{filter_id}_counts.user_id = received_rating_weight.user_id;



-- num_created_comments
WITH created_comments AS (
    SELECT user_id, COUNT(user_id) AS num_created_comments
    FROM filter{filter_id}_comments
    GROUP BY user_id
)
UPDATE filter{filter_id}_counts
SET num_created_comments = created_comments.num_created_comments
FROM created_comments
WHERE filter{filter_id}_counts.user_id = created_comments.user_id;



-- num_received_comments
WITH filter{filter_id}_proposals_x_comments AS (
    SELECT filter{filter_id}_proposals.user_id AS user_id
    FROM filter{filter_id}_comments
    LEFT JOIN filter{filter_id}_proposals
    USING (proposal_id)
    -- RIGHT JOIN would be a more natural choice here,
    -- but is only supported in SQLite 3.39.0 onwards
),
received_comments AS (
    SELECT user_id, COUNT(user_id) AS num_received_comments
    FROM filter{filter_id}_proposals_x_comments
    GROUP BY user_id
)
UPDATE filter{filter_id}_counts
SET num_received_comments = received_comments.num_received_comments
FROM received_comments
WHERE filter{filter_id}_counts.user_id = received_comments.user_id;




CREATE TEMP TABLE reactions_grouped AS
    SELECT user_id, reaction_type, COUNT(user_id) AS cnt_by_type
    FROM filter{filter_id}_reactions
    GROUP BY user_id, reaction_type;

-- num_created_reactions
WITH created_reactions AS (
    SELECT user_id, SUM(cnt_by_type) AS num_created_reactions
    FROM reactions_grouped
    GROUP BY user_id
)
UPDATE filter{filter_id}_counts
SET num_created_reactions = created_reactions.num_created_reactions
FROM created_reactions
WHERE filter{filter_id}_counts.user_id = created_reactions.user_id;

-- num_created_positive_reactions
WITH created_positive_reactions AS (
    SELECT user_id, SUM(cnt_by_type) AS num_created_positive_reactions
    FROM reactions_grouped
    WHERE reaction_type IN ({positive_reactions})
    GROUP BY user_id
)
UPDATE filter{filter_id}_counts
SET num_created_positive_reactions = created_positive_reactions.num_created_positive_reactions
FROM created_positive_reactions
WHERE filter{filter_id}_counts.user_id = created_positive_reactions.user_id;

-- num_created_negative_reactions
WITH created_negative_reactions AS (
    SELECT user_id, SUM(cnt_by_type) AS num_created_negative_reactions
    FROM reactions_grouped
    WHERE reaction_type IN ({negative_reactions})
    GROUP BY user_id
)
UPDATE filter{filter_id}_counts
SET num_created_negative_reactions = created_negative_reactions.num_created_negative_reactions
FROM created_negative_reactions
WHERE filter{filter_id}_counts.user_id = created_negative_reactions.user_id;

-- num_created_upvote_reactions
WITH created_upvote_reactions AS (
    SELECT user_id, cnt_by_type AS num_created_upvote_reactions
    FROM reactions_grouped
    WHERE reaction_type='upvote'
    GROUP BY user_id
)
UPDATE filter{filter_id}_counts
SET num_created_upvote_reactions = created_upvote_reactions.num_created_upvote_reactions
FROM created_upvote_reactions
WHERE filter{filter_id}_counts.user_id = created_upvote_reactions.user_id;

-- num_created_downvote_reactions
WITH created_downvote_reactions AS (
    SELECT user_id, cnt_by_type AS num_created_downvote_reactions
    FROM reactions_grouped
    WHERE reaction_type='downvote'
    GROUP BY user_id
)
UPDATE filter{filter_id}_counts
SET num_created_downvote_reactions = created_downvote_reactions.num_created_downvote_reactions
FROM created_downvote_reactions
WHERE filter{filter_id}_counts.user_id = created_downvote_reactions.user_id;

-- num_created_anger_reactions
WITH created_anger_reactions AS (
    SELECT user_id, cnt_by_type AS num_created_anger_reactions
    FROM reactions_grouped
    WHERE reaction_type='anger'
    GROUP BY user_id
)
UPDATE filter{filter_id}_counts
SET num_created_anger_reactions = created_anger_reactions.num_created_anger_reactions
FROM created_anger_reactions
WHERE filter{filter_id}_counts.user_id = created_anger_reactions.user_id;

-- num_created_celebrate_reactions
WITH created_celebrate_reactions AS (
    SELECT user_id, cnt_by_type AS num_created_celebrate_reactions
    FROM reactions_grouped
    WHERE reaction_type='celebrate'
    GROUP BY user_id
)
UPDATE filter{filter_id}_counts
SET num_created_celebrate_reactions = created_celebrate_reactions.num_created_celebrate_reactions
FROM created_celebrate_reactions
WHERE filter{filter_id}_counts.user_id = created_celebrate_reactions.user_id;

-- num_created_clap_reactions
WITH created_clap_reactions AS (
    SELECT user_id, cnt_by_type AS num_created_clap_reactions
    FROM reactions_grouped
    WHERE reaction_type='clap'
    GROUP BY user_id
)
UPDATE filter{filter_id}_counts
SET num_created_clap_reactions = created_clap_reactions.num_created_clap_reactions
FROM created_clap_reactions
WHERE filter{filter_id}_counts.user_id = created_clap_reactions.user_id;

-- num_created_curious_reactions
WITH created_curious_reactions AS (
    SELECT user_id, cnt_by_type AS num_created_curious_reactions
    FROM reactions_grouped
    WHERE reaction_type='curious'
    GROUP BY user_id
)
UPDATE filter{filter_id}_counts
SET num_created_curious_reactions = created_curious_reactions.num_created_curious_reactions
FROM created_curious_reactions
WHERE filter{filter_id}_counts.user_id = created_curious_reactions.user_id;

-- num_created_genius_reactions
WITH created_genius_reactions AS (
    SELECT user_id, cnt_by_type AS num_created_genius_reactions
    FROM reactions_grouped
    WHERE reaction_type='genius'
    GROUP BY user_id
)
UPDATE filter{filter_id}_counts
SET num_created_genius_reactions = created_genius_reactions.num_created_genius_reactions
FROM created_genius_reactions
WHERE filter{filter_id}_counts.user_id = created_genius_reactions.user_id;

-- num_created_happy_reactions
WITH created_happy_reactions AS (
    SELECT user_id, cnt_by_type AS num_created_happy_reactions
    FROM reactions_grouped
    WHERE reaction_type='happy'
    GROUP BY user_id
)
UPDATE filter{filter_id}_counts
SET num_created_happy_reactions = created_happy_reactions.num_created_happy_reactions
FROM created_happy_reactions
WHERE filter{filter_id}_counts.user_id = created_happy_reactions.user_id;

-- num_created_hot_reactions
WITH created_hot_reactions AS (
    SELECT user_id, cnt_by_type AS num_created_hot_reactions
    FROM reactions_grouped
    WHERE reaction_type='hot'
    GROUP BY user_id
)
UPDATE filter{filter_id}_counts
SET num_created_hot_reactions = created_hot_reactions.num_created_hot_reactions
FROM created_hot_reactions
WHERE filter{filter_id}_counts.user_id = created_hot_reactions.user_id;

-- num_created_laugh_reactions
WITH created_laugh_reactions AS (
    SELECT user_id, cnt_by_type AS num_created_laugh_reactions
    FROM reactions_grouped
    WHERE reaction_type='laugh'
    GROUP BY user_id
)
UPDATE filter{filter_id}_counts
SET num_created_laugh_reactions = created_laugh_reactions.num_created_laugh_reactions
FROM created_laugh_reactions
WHERE filter{filter_id}_counts.user_id = created_laugh_reactions.user_id;

-- num_created_love_reactions
WITH created_love_reactions AS (
    SELECT user_id, cnt_by_type AS num_created_love_reactions
    FROM reactions_grouped
    WHERE reaction_type='love'
    GROUP BY user_id
)
UPDATE filter{filter_id}_counts
SET num_created_love_reactions = created_love_reactions.num_created_love_reactions
FROM created_love_reactions
WHERE filter{filter_id}_counts.user_id = created_love_reactions.user_id;

-- num_created_sad_reactions
WITH created_sad_reactions AS (
    SELECT user_id, cnt_by_type AS num_created_sad_reactions
    FROM reactions_grouped
    WHERE reaction_type='sad'
    GROUP BY user_id
)
UPDATE filter{filter_id}_counts
SET num_created_sad_reactions = created_sad_reactions.num_created_sad_reactions
FROM created_sad_reactions
WHERE filter{filter_id}_counts.user_id = created_sad_reactions.user_id;



CREATE TEMP TABLE selected_comments_x_reactions AS
SELECT filter{filter_id}_comments.user_id AS user_id, reaction_type
FROM filter{filter_id}_reactions
    LEFT JOIN filter{filter_id}_comments
    USING (comment_id);
    -- RIGHT JOIN would be a more natural choice here,
    -- but is only supported in SQLite 3.39.0 onwards

CREATE TEMP TABLE selected_comments_x_reactions_grouped AS
SELECT user_id, reaction_type, COUNT(user_id) as cnt_by_type
FROM selected_comments_x_reactions
GROUP BY user_id, reaction_type;

-- num_received_reactions
WITH received_reactions AS (
    SELECT user_id, SUM(cnt_by_type) AS num_received_reactions
    FROM selected_comments_x_reactions_grouped
    GROUP BY user_id
)
UPDATE filter{filter_id}_counts
SET num_received_reactions = received_reactions.num_received_reactions
FROM received_reactions
WHERE filter{filter_id}_counts.user_id = received_reactions.user_id;

-- num_received_positive_reactions
WITH received_positive_reactions AS (
    SELECT user_id, SUM(cnt_by_type) AS num_received_positive_reactions
    FROM selected_comments_x_reactions_grouped
    WHERE reaction_type IN ('celebrate', 'clap', 'curious', 'genius', 'happy', 'hot', 'laugh', 'love')
)
UPDATE filter{filter_id}_counts
SET num_received_positive_reactions = received_positive_reactions.num_received_positive_reactions
FROM received_positive_reactions
WHERE filter{filter_id}_counts.user_id = received_positive_reactions.user_id;

-- num_received_negative_reactions
WITH received_negative_reactions AS (
    SELECT user_id, SUM(cnt_by_type) AS num_received_negative_reactions
    FROM selected_comments_x_reactions_grouped
    WHERE reaction_type IN ('anger', 'sad')
)
UPDATE filter{filter_id}_counts
SET num_received_negative_reactions = received_negative_reactions.num_received_negative_reactions
FROM received_negative_reactions
WHERE filter{filter_id}_counts.user_id = received_negative_reactions.user_id;

-- num_received_upvote_reactions
WITH received_upvote_reactions AS (
    SELECT user_id, cnt_by_type AS num_received_upvote_reactions
    FROM selected_comments_x_reactions_grouped
    WHERE reaction_type='upvote'
)
UPDATE filter{filter_id}_counts
SET num_received_upvote_reactions = received_upvote_reactions.num_received_upvote_reactions
FROM received_upvote_reactions
WHERE filter{filter_id}_counts.user_id = received_upvote_reactions.user_id;

-- num_received_downvote_reactions
WITH received_downvote_reactions AS (
    SELECT user_id, cnt_by_type AS num_received_downvote_reactions
    FROM selected_comments_x_reactions_grouped
    WHERE reaction_type='downvote'
)
UPDATE filter{filter_id}_counts
SET num_received_downvote_reactions = received_downvote_reactions.num_received_downvote_reactions
FROM received_downvote_reactions
WHERE filter{filter_id}_counts.user_id = received_downvote_reactions.user_id;

-- num_received_anger_reactions
WITH received_anger_reactions AS (
    SELECT user_id, cnt_by_type AS num_received_anger_reactions
    FROM selected_comments_x_reactions_grouped
    WHERE reaction_type='anger'
)
UPDATE filter{filter_id}_counts
SET num_received_anger_reactions = received_anger_reactions.num_received_anger_reactions
FROM received_anger_reactions
WHERE filter{filter_id}_counts.user_id = received_anger_reactions.user_id;

-- num_received_celebrate_reactions
WITH received_celebrate_reactions AS (
    SELECT user_id, cnt_by_type AS num_received_celebrate_reactions
    FROM selected_comments_x_reactions_grouped
    WHERE reaction_type='celebrate'
)
UPDATE filter{filter_id}_counts
SET num_received_celebrate_reactions = received_celebrate_reactions.num_received_celebrate_reactions
FROM received_celebrate_reactions
WHERE filter{filter_id}_counts.user_id = received_celebrate_reactions.user_id;

-- num_received_clap_reactions
WITH received_clap_reactions AS (
    SELECT user_id, cnt_by_type AS num_received_clap_reactions
    FROM selected_comments_x_reactions_grouped
    WHERE reaction_type='clap'
)
UPDATE filter{filter_id}_counts
SET num_received_clap_reactions = received_clap_reactions.num_received_clap_reactions
FROM received_clap_reactions
WHERE filter{filter_id}_counts.user_id = received_clap_reactions.user_id;

-- num_received_curious_reactions
WITH received_curious_reactions AS (
    SELECT user_id, cnt_by_type AS num_received_curious_reactions
    FROM selected_comments_x_reactions_grouped
    WHERE reaction_type='curious'
)
UPDATE filter{filter_id}_counts
SET num_received_curious_reactions = received_curious_reactions.num_received_curious_reactions
FROM received_curious_reactions
WHERE filter{filter_id}_counts.user_id = received_curious_reactions.user_id;

-- num_received_genius_reactions
WITH received_genius_reactions AS (
    SELECT user_id, cnt_by_type AS num_received_genius_reactions
    FROM selected_comments_x_reactions_grouped
    WHERE reaction_type='genius'
)
UPDATE filter{filter_id}_counts
SET num_received_genius_reactions = received_genius_reactions.num_received_genius_reactions
FROM received_genius_reactions
WHERE filter{filter_id}_counts.user_id = received_genius_reactions.user_id;

-- num_received_happy_reactions
WITH received_happy_reactions AS (
    SELECT user_id, cnt_by_type AS num_received_happy_reactions
    FROM selected_comments_x_reactions_grouped
    WHERE reaction_type='happy'
)
UPDATE filter{filter_id}_counts
SET num_received_happy_reactions = received_happy_reactions.num_received_happy_reactions
FROM received_happy_reactions
WHERE filter{filter_id}_counts.user_id = received_happy_reactions.user_id;

-- num_received_hot_reactions
WITH received_hot_reactions AS (
    SELECT user_id, cnt_by_type AS num_received_hot_reactions
    FROM selected_comments_x_reactions_grouped
    WHERE reaction_type='hot'
)
UPDATE filter{filter_id}_counts
SET num_received_hot_reactions = received_hot_reactions.num_received_hot_reactions
FROM received_hot_reactions
WHERE filter{filter_id}_counts.user_id = received_hot_reactions.user_id;

-- num_received_laugh_reactions
WITH received_laugh_reactions AS (
    SELECT user_id, cnt_by_type AS num_received_laugh_reactions
    FROM selected_comments_x_reactions_grouped
    WHERE reaction_type='laugh'
)
UPDATE filter{filter_id}_counts
SET num_received_laugh_reactions = received_laugh_reactions.num_received_laugh_reactions
FROM received_laugh_reactions
WHERE filter{filter_id}_counts.user_id = received_laugh_reactions.user_id;

-- num_received_love_reactions
WITH received_love_reactions AS (
    SELECT user_id, cnt_by_type AS num_received_love_reactions
    FROM selected_comments_x_reactions_grouped
    WHERE reaction_type='love'
)
UPDATE filter{filter_id}_counts
SET num_received_love_reactions = received_love_reactions.num_received_love_reactions
FROM received_love_reactions
WHERE filter{filter_id}_counts.user_id = received_love_reactions.user_id;

-- num_received_sad_reactions
WITH received_sad_reactions AS (
    SELECT user_id, cnt_by_type AS num_received_sad_reactions
    FROM selected_comments_x_reactions_grouped
    WHERE reaction_type='sad'
)
UPDATE filter{filter_id}_counts
SET num_received_sad_reactions = received_sad_reactions.num_received_sad_reactions
FROM received_sad_reactions
WHERE filter{filter_id}_counts.user_id = received_sad_reactions.user_id;



DELETE FROM filter{filter_id}_counts
WHERE
    num_created_proposals = 0 AND
    num_created_ratings = 0 AND
    num_received_ratings = 0 AND
    weight_received_ratings = 0.0 AND
    num_created_comments = 0 AND
    num_received_comments = 0 AND
    num_created_reactions = 0 AND
    num_created_positive_reactions = 0 AND
    num_created_negative_reactions = 0 AND
    num_created_upvote_reactions = 0 AND
    num_created_downvote_reactions = 0 AND
    num_created_anger_reactions = 0 AND
    num_created_celebrate_reactions = 0 AND
    num_created_clap_reactions = 0 AND
    num_created_curious_reactions = 0 AND
    num_created_genius_reactions = 0 AND
    num_created_happy_reactions = 0 AND
    num_created_hot_reactions = 0 AND
    num_created_laugh_reactions = 0 AND
    num_created_love_reactions = 0 AND
    num_created_sad_reactions = 0 AND
    num_received_reactions = 0 AND
    num_received_positive_reactions = 0 AND
    num_received_negative_reactions = 0 AND
    num_received_upvote_reactions = 0 AND
    num_received_downvote_reactions = 0 AND
    num_received_anger_reactions = 0 AND
    num_received_celebrate_reactions = 0 AND
    num_received_clap_reactions = 0 AND
    num_received_curious_reactions = 0 AND
    num_received_genius_reactions = 0 AND
    num_received_happy_reactions = 0 AND
    num_received_hot_reactions = 0 AND
    num_received_laugh_reactions = 0 AND
    num_received_love_reactions = 0 AND
    num_received_sad_reactions = 0;