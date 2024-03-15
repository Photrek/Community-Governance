--
-- Various example queries
--


-- get all wallets for user_id = 9
SELECT u.collection_id as user_id, w.address as wallet_id FROM user as u
    JOIN wallet_link as w ON u.collection_id = w.collection_id
    WHERE user_id = 9;

-- get sum of wallet balance for user_id = 9
SELECT u.collection_id as user_id, sum(w.balance) as wallet_balance FROM user as u
    LEFT JOIN wallet_link as w ON u.collection_id = w.collection_id
    GROUP BY w.collection_id, u.collection_id
    HAVING user_id = 9;


-- How many AGIX did one user use to vote for a question
SELECT u.collection_id, u.balance FROM user as u


-- # of people voted for proposal
SELECT question_id, count(collection_id) as votes FROM answer as a
    GROUP BY question_id
    where collection_id = 9;

SELECT tmp.votes, count(tmp.votes) FROM (
    SELECT question_id, count(question_id) as votes FROM answer as a
    GROUP BY question_id
) as tmp
GROUP BY tmp.votes

-- % of people voted for proposal
SELECT 
    question_id,
    (COUNT(CASE WHEN answer <> 'skip' THEN 1 END) * 100.0) / COUNT(*) AS participation_percentage
FROM 
    answer
GROUP BY
    question_id;


-- all valid votes (not skipped)
SELECT * FROM answer WHERE answer != 'skip';

-- all votes of user = 9 
SELECT * FROM answer WHERE answer != 'skip' AND collection_id = 9;

-- average grade using square root voting
SELECT 
    question_id,
    SUM(sqrt(total_balance) * CAST(answer AS INTEGER)) / SUM(sqrt(total_balance)) AS "average grade"
FROM 
    answer
WHERE 
    answer != 'skip'
GROUP BY 
    question_id
HAVING 
    question_id = 118;

