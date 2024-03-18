---
title: CES MVP
---

_Demonstration of tooling used to extract, load and transform the DeepFunding data_

## Investment Round X Results

```sql votes_summary
select 
  sum(num_votes) as total_votes,
  count(proposal_id) as total_proposals
from vote_results
```

<BigValue data={votes_summary} value=total_votes />
<BigValue data={votes_summary} value=total_proposals />

### Voting Algorihtms

```sql algorihtms
-- static names of voting algorithms
SELECT *
FROM (
    VALUES 
        ('one_user_one_vote'),
        ('one_user_one_vote_weighted_sqrt'),
) AS StaticRows (name)
```

<Dropdown
    data={algorihtms} 
    name=algorithm
    title="Select voting algorithm"
    value=name
    defaultValue=one_user_one_vote
/>

```sql voting_result
SELECT
    p.proposal_id,
    p.title,
    COUNT(CASE WHEN r.grade <> 'skip' THEN 1 END) AS num_votes,

    -- need the skipped answers to calculate % of people that voted
    (COUNT(CASE WHEN r.grade <> 'skip' THEN 1 END) * 100.0) / COUNT(r.*) AS percent_voted,

    IF('${inputs.algorithm.value}' = 'one_user_one_vote_weighted_sqrt', 
      
      -- one_user_one_vote_weighted_sqrt
      NULLIF(
        -- remove skipped votes
        SUM(CASE WHEN r.grade <> 'skip' THEN sqrt(r.total_balance) * CAST(r.grade AS INTEGER) END) / 
        NULLIF(SUM(CASE WHEN r.grade <> 'skip' THEN sqrt(r.total_balance) END), 0), 
      0)

    , 
    
      -- one_user_one_vote
      NULLIF(
        -- remove skipped votes
        SUM(CASE WHEN r.grade <> 'skip' THEN CAST(r.grade AS INTEGER) END) / 
        NULLIF(COUNT(CASE WHEN r.grade <> 'skip' THEN 1 END), 0), 
      0) 

    ) AS avg_grade
FROM 
    proposals AS p
LEFT JOIN 
    ratings AS r
ON p.proposal_id = r.proposal_id
GROUP BY 
    p.proposal_id, 
    p.title
```

```sql voting_sqrt_ranked
SELECT
  RANK() OVER (ORDER BY avg_grade DESC) AS rank,
  proposal_id,
  title,
  num_votes,
  percent_voted,
  avg_grade,
  'https://proposals.deepfunding.ai/graduated/accepted/69b71ede-ae53-43c8-ab78-93eb213a378f' as proposal_url
FROM 
  ${voting_result}
```

<DataTable data={voting_sqrt_ranked} rowShading=true search=true rows=25  link=proposal_url >
    <Column id=rank />
    <Column id=proposal_id />
    <Column id=title wrap=true />
    <Column id=num_votes contentType=colorscale scaleColor=#e3af05 />
    <Column id=percent_voted contentType=colorscale scaleColor=blue />
    <Column id=avg_grade contentType=colorscale />
</DataTable>

### Overview votes

<BarChart 
    data={voting_sqrt_ranked} 
    x=proposal_id
    y=num_votes
    xAxisTitle=Proposal
    yAxisTitle=Votes
/>

### Votes relation
```sql stacked_voting
SELECT
  proposal_id,
  num_votes AS value,
  'number of votes' AS type
FROM 
  vote_results

UNION ALL

SELECT
  proposal_id,
  percent_voted AS value,
  'percentage voted' AS type
FROM 
  vote_results
```
<BarChart 
    data={stacked_voting} 
    x=proposal_id
    y=value
    series=type 
    xAxisTitle=Proposal
    yAxisTitle=Votes
/>