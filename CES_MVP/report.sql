--
-- Statements to generate a report of the data provided in the data folder
--

-- enable excel export
INSTALL spatial;
LOAD spatial;

-- ranked results
COPY (
    WITH vote_results AS (
        SELECT
            p.question_id,
            p.proposal,
            COUNT(CASE WHEN a.answer <> 'skip' THEN 1 END) AS num_votes,
            -- need the skip answers to calculate % of people that voted
            (COUNT(CASE WHEN a.answer <> 'skip' THEN 1 END) * 100.0) / COUNT(a.*) AS percent_voted,

            -- average grade
            NULLIF(
                -- remove skipped votes
                SUM(CASE WHEN a.answer <> 'skip' THEN sqrt(a.total_balance) * CAST(a.answer AS INTEGER) END) / 
                NULLIF(SUM(CASE WHEN a.answer <> 'skip' THEN sqrt(a.total_balance) END), 0), 
            0) AS avg_grade
        FROM 
            question AS p
        LEFT JOIN 
            answer AS a ON p.question_id = a.question_id
        GROUP BY 
            p.question_id, 
            p.proposal
    )
    SELECT
        RANK() OVER (ORDER BY avg_grade DESC) AS rank,
        question_id,
        proposal,
        num_votes AS "number of votes",
        percent_voted AS "% people that voted",
        avg_grade AS "average grade"
    FROM 
        vote_results
) TO 'report.xlsx' WITH (FORMAT GDAL, DRIVER 'xlsx');