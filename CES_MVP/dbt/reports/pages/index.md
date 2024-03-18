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

### Ranked voting results using square root voting

```sql sqrt_voting
SELECT
  RANK() OVER (ORDER BY avg_grade DESC) AS rank,
  proposal_id,
  title,
  num_votes,
  percent_voted,
  avg_grade,
  'https://proposals.deepfunding.ai/graduated/accepted/69b71ede-ae53-43c8-ab78-93eb213a378f' as proposal_url
FROM 
  vote_results
```

<DataTable data={sqrt_voting} rowShading=true search=true rows=25  link=proposal_url >
    <Column id=rank />
    <Column id=proposal_id />
    <Column id=title wrap=true />
    <Column id=num_votes contentType=colorscale scaleColor=#e3af05 />
    <Column id=percent_voted contentType=colorscale scaleColor=blue />
    <Column id=avg_grade contentType=colorscale />
</DataTable>

### Overview votes

<BarChart 
    data={sqrt_voting} 
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