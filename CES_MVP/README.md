# Community Engagement Score

# System Overview

<div align="center" style="background-color:white">
    <img src="docs/images/system_overview.png" alt="System context overview">
    <p>
        System context overview - <a target="__blank" href="docs/images/system_overview.drawio">source</a>
    </p>
</div>

# Project Structure
* The model structure is inspired by dbt's [How we structure our dbt projects](https://docs.getdbt.com/best-practices/how-we-structure/1-guide-overview) article.

# Data Model
Data model using [Crow's_foot_notation](https://en.wikipedia.org/wiki/Entity%E2%80%93relationship_model#Crow's_foot_notation)
```mermaid
---
title: Community Engagement High Level Model
---
erDiagram
    USER ||--|| WALLET : owns
    USER ||--|| PROPOSAL : rates
```

* **users.csv** (collections) - user in the voting portal
* **wallet-links.csv** - [join table] between user and wallet
* **answers.csv** (voting-portal) - [join table] contains answers (ratings) of questions
* **questions.csv** - proposal names


```mermaid
---
title: Current Community Engagement Model
---
erDiagram

    USER {
        int user_id PK
        bigint balance
    }

    RATING {
        int user_id FK
        int proposal_id FK
        varchar grade
        bigint total_balance
    }

    PROPOSAL {
        int proposal_id PK
        varchar title
    }

    WALLET_LINK {
        varchar address PK
        int user_id FK
        bigint balance
    }

    WALLET ||--|{ WALLET_LINK : belongs_to
    USER ||--|{ WALLET_LINK : owns
    USER ||--|{ RATING : gives
    PROPOSAL  ||--|{ RATING : belongs_to
```

```mermaid
---
title: Future Community Engagement Model
---
erDiagram

    POOL {
        int pool_id PK
        varchar name
        varchar description
        bigint max_amount
    }

    USER {
        int user_id PK
        bigint balance
    }

    RATING {
        int user_id FK
        int proposal_id FK
        varchar grade
        bigint total_balance
    }

    PROPOSAL {
        int proposal_id PK
        int pool_id FK
        varchar title
        bigint required_amount
        varchar detail_page
        varchar main_image
    }

    WALLET_LINK {
        varchar address PK
        int user_id FK
        bigint balance
    }

    WALLET ||--|{ WALLET_LINK : belongs_to
    USER ||--|{ WALLET_LINK : owns
    USER ||--|{ RATING : gives
    PROPOSAL  ||--|{ RATING : belongs_to
    POOL ||--|{ PROPOSAL : part_of
```

# Square Root Voting Formula:
Formula used in the report task `make report` to calculate the average grade of a proposal (see `report.sql`).

$\text{Average Grade} = \frac{\sum (\sqrt{\text{tokens}_i} \times \text{grade}_i)}{\sum \sqrt{\text{tokens}_i}}$

Where:
* $tokens_i$: Number of tokens held by user $i$.
* $grade_i$: Grade assigned by user $i$
