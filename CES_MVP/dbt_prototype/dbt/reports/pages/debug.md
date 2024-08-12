---
title: Analysis
---

<script>
	import Katex from 'svelte-katex'
</script>

<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.15.2/dist/katex.min.css" integrity="sha384-MlJdn/WNKDGXveldHDdyRP1R4CTHr3FeuDNfhsLPYrq2t0UBkUdK2jyTnXPEK1NQ" crossorigin="anonymous">

_Showing relevant data used to calculate the final output_

## General Insights

```sql unique_voters
select count(distinct collection_uuid) as unique_voters from stg_vp__voting_answers
```
```sql proposals_with_votes
select count(distinct question_id) as proposals_with_votes from stg_vp__voting_answers
```
```sql users_with_coll_id_or_address
select count(*) as users_with_coll_id_or_address from stg_pp__users where collection_uuid is not null or wallet_address is not null
```
```sql voters_with_agix
select count(distinct collection_uuid) as voters_with_agix from int__ratings where balance > 0
```

<BigValue 
  data={unique_voters} 
  value=unique_voters
/>
<BigValue 
  data={proposals_with_votes} 
  value=proposals_with_votes
/>

<BigValue 
  data={users_with_coll_id_or_address} 
  value=users_with_coll_id_or_address
/>
<BigValue 
  data={voters_with_agix} 
  value=voters_with_agix
/>

## Engagement Score

The engagement score per user is calculated as follows:

| Event                             | Weight |
|-----------------------------------|--------|
| comment count                     |      3 |
| upvote count                      |      2 |
| downvote count                    |     -3 |
| reviews created                   |      2 |



```sql comments_count
select count(*) as comments from stg_pp__comments
```

```sql distinct_comment_voters
select count(distinct voter_id) as users_voting_on_comments from stg_pp__comment_votes
```

<BigValue 
  data={comments_count} 
  value=comments
/>

<BigValue  
  data={distinct_comment_voters} 
  value=users_voting_on_comments
/>

```sql int__engagement_score
select * from int__engagement_score
```

### Engagement Score Table
<DataTable search=true data={int__engagement_score}/>

## Reputation Weights
The reputation weight is a logarithmic scale that distributes the user engagement score in range [1,5].

<Katex>
{"\\text{Engagement Score} = 3 \\times \\text{comment count} + 2 \\times \\text{upvote count} - 3 \\times \\text{downvote count}"}
</Katex>

```sql int__reputation_weight
select * from int__reputation_weight
```

<DataTable search=true data={int__reputation_weight}/>

<Details title="More Details">

## Min/Max engagement score per user

```sql min_max_engagement_score
select * from int__min_max_engagement_score_per_proposal
```
<DataTable search=true data={min_max_engagement_score}/>

</Details>

## Voting Weights

<Katex>
{"\\text{total voting weight} = \\sqrt{\\text{balance} / 100000000} \\times \\text{reputation weight}"}
</Katex>

```sql voting_weights
select * from voting_weights
```
<DataTable search=true data={voting_weights}/>

## Voting Results Details

### Votes per grade

```sql votes_per_grade
select 
  proposal_id,
  title,
  votes_per_proposal,
  total_voters,
  perc_people_that_voted,
  weighted_sum,
  average_grade,
  average_grade_wo_reputation,
    
  grade_sum,
  grade_1,
  grade_2,
  grade_3,
  grade_4,
  grade_5,
  grade_6,
  grade_7,
  grade_8,
  grade_9,
  grade_10,
  average_grade_2,
  simple_average_grade,

from dfr4_voting_results
```

<DataTable search=true data={votes_per_grade}/>

### Votes per proposal

```sql votes_per_proposal
select * from int__votes_per_proposal
```

<DataTable search=true data={votes_per_proposal}/>

