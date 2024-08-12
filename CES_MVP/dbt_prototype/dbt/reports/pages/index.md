---
title: CES MVP
---

<script>
	import Katex from 'svelte-katex'
</script>

<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.15.2/dist/katex.min.css" integrity="sha384-MlJdn/WNKDGXveldHDdyRP1R4CTHr3FeuDNfhsLPYrq2t0UBkUdK2jyTnXPEK1NQ" crossorigin="anonymous">

_Demonstration of tooling used to extract, load and transform the DeepFunding data_

## Deep Funding Round 4

```sql dfr4_voting_results
select
  *,
  case 
    when eligible then '<b>Bold</b> text'
    else '<input type="checkbox" />'
  end as eligible_html
from dfr4_voting_results
```

<Katex>
{`
eligable = \\begin{cases}
   true &\\text{if } \\text{average\\_grade} > 6.5 \\text{ and } \\text{percent\\_of\\_people\\_voted} > 1.0 \\\\
   false &\\text{otherwise}
\\end{cases}
`}
</Katex>

<DataTable 
  data={dfr4_voting_results}
  rowShading=true
  search=true
  rows=50
  groupBy=pool_name
  groupType=section >
    <Column id=pool_id />
    <Column id=pool_name />
    <Column id=proposal_id />
    <Column id=title wrap=true />
    <Column id=proposal_url contentType=link wrap=true />
    <Column id=pool_funding_amount />
    <Column id=requested_amount />
    <Column id=votes_per_proposal />
    <Column id=total_voters />
    <Column id=perc_people_that_voted contentType=colorscale scaleColor=#e3af05 />
    <Column id=weighted_sum />
    <Column id=average_grade />
    <Column id=eligible />
    <Column id=eligible_html contentType=html class=markdown />
</DataTable>
