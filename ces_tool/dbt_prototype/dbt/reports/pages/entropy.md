---
title: Entropy
---

_Demonstration of using entropy in calculating the community engagement score_


```sql entropy
select 
  collection_id,
  entropy
from entropy
```

<BarChart
    data={entropy} 
    x=collection_id
    y=entropy 
/>

<DataTable search=true rowShading=true rows=50 data={entropy}/>
