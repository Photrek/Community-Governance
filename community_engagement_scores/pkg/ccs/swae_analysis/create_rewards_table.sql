CREATE TABLE {table_name_rewards} AS
SELECT
    user_id,
    name,
    email_address,
    ethereum_address,
    cardano_address,
    contribution_score,
    NULL AS rank,
    NULL AS eligibility,
    NULL AS x,
    NULL AS agix_reward_fraction,
    NULL AS voting_weight_fraction,
    NULL AS agix_reward,
    NULL AS voting_weight
FROM {table_name_contribution_scores}
JOIN users USING (user_id);


-- Rank
WITH ranked_users AS (
    SELECT
        user_id,
        ROW_NUMBER() OVER (ORDER BY contribution_score DESC) AS rank
    FROM {table_name_rewards}
)
UPDATE {table_name_rewards}
SET rank = ranked_users.rank
    FROM ranked_users
    WHERE ranked_users.user_id = {table_name_rewards}.user_id;


-- Eligibility
UPDATE {table_name_rewards}
SET eligibility = CASE
    WHEN user_id in ({filtered_user_ids}) THEN "filtered user"
    WHEN contribution_score < {threshold_value} THEN "below score threshold"
    ELSE "yes"
END;


-- Input value x for distribution functions
WITH number_assignment AS (
    SELECT
        user_id,
        ROW_NUMBER() OVER (ORDER BY rank DESC) AS x
    FROM {table_name_rewards}
    WHERE eligibility = "yes"
)
UPDATE {table_name_rewards}
SET x = number_assignment.x
    FROM number_assignment
    WHERE number_assignment.user_id = {table_name_rewards}.user_id;


-- AGIX reward distribution with Python function
UPDATE {table_name_rewards}
SET agix_reward_fraction = calc_agix_distribution(x);
-- Normalization: sum needs to be 1.0
UPDATE {table_name_rewards}
SET agix_reward_fraction = agix_reward_fraction / (SELECT SUM(agix_reward_fraction) FROM {table_name_rewards});


-- Voting power reward distribution with Python function
UPDATE {table_name_rewards}
SET voting_weight_fraction = calc_vw_distribution(x);
-- Normalization: sum needs to be 1.0
UPDATE {table_name_rewards}
SET voting_weight_fraction = voting_weight_fraction / (SELECT SUM(voting_weight_fraction) FROM {table_name_rewards});



-- AGIX reward based on distribution
UPDATE {table_name_rewards}
SET agix_reward = agix_reward_fraction * {total_agix_reward};

-- Equalize AGIX rewards of users with equal scores
-- Create a temporary table to store the updated values
CREATE TEMPORARY TABLE temp AS
SELECT contribution_score, AVG(agix_reward) AS average_agix_reward
FROM {table_name_rewards}
WHERE agix_reward > 0.0
GROUP BY contribution_score
HAVING COUNT(*) > 1;
-- Update the original rewards table with the average values
UPDATE {table_name_rewards}
SET agix_reward = (
    SELECT average_agix_reward
    FROM temp
    WHERE contribution_score = {table_name_rewards}.contribution_score
)
WHERE contribution_score IN (SELECT contribution_score FROM temp)
AND agix_reward > 0.0;
-- Drop the temporary table
DROP TABLE temp;



-- Voting power reward based on distribution
UPDATE {table_name_rewards}
SET voting_weight = (voting_weight_fraction / (SELECT MAX(voting_weight_fraction) FROM {table_name_rewards})) *
    ({max_voting_weight} - {min_voting_weight}) +
    {min_voting_weight};

-- Equalize voting power of users with equal scores
-- Create a temporary table to store the updated values
CREATE TEMPORARY TABLE temp AS
SELECT contribution_score, AVG(voting_weight) AS average_voting_weight
FROM {table_name_rewards}
WHERE voting_weight > {min_voting_weight}
GROUP BY contribution_score
HAVING COUNT(*) > 1;
-- Update the original rewards table with the average values
UPDATE {table_name_rewards}
SET voting_weight = (SELECT average_voting_weight FROM temp WHERE contribution_score = {table_name_rewards}.contribution_score)
WHERE contribution_score IN (SELECT contribution_score FROM temp)
AND voting_weight > {min_voting_weight};
-- Drop the temporary table
DROP TABLE temp;
