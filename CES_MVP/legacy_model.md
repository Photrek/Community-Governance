# Legacy Data Model fo [CES POC](../community_engagement_scores_poc/README.md)
Data model using [Crow's_foot_notation](https://en.wikipedia.org/wiki/Entity%E2%80%93relationship_model#Crow's_foot_notation)

```mermaid
---
title: community_engagement_scores_poc Model
---
erDiagram

    MISSION {
        varchar mission_id PK
        varchar title
        timestamp start_timestamp
        timestamp end_timestamp
    }

    USER {
        varchar user_id PK
        varchar name
        varchar email_address
        varchar ethereum_address
        varchar cardano_address
        varchar web3_nonce
        varchar handle
        varchar bio
        varchar timezone
        varchar age_range
        varchar gender
        varchar linkedin_link
        varchar medium_link
        varchar twitter_link
        varchar provider_name
        int last_seen_time
        varchar last_seen_location
        bool sign_status
        bool contribution_status
        int creation_timestamp
        varchar creation_datetime
        int num_votes
    }
    
    ENGAGEMENT_SCORE {
        int user_id FK
        decimal engagement_score
    }

    RATING {
        varchar rating_id PK
        varchar proposal_id FK
        varchar user_id FK
        int rating
        bool is_anonymous
        bool enable
        int creation_timestamp
        varchar creation_datetime
    }

    REWARDS {
        int user_id FK
        decimal agix_reward
        decimal voting_weight
    }

    PROPOSAL {
        varchar proposal_id PK
        varchar mission_id FK
        varchar user_id FK
        varchar title
        varchar summary
        varchar state
        bool is_anonymous
        bool is_rejected
        int time_spent_create
        varchar rating
        float average_rating
        int creation_timestamp
        varchar creation_datetime
        int publishing_timestamp
        varchar publishing_datetime
        int num_files
        int num_total_unique_views
        int num_total_engagements
        int num_total_contributions
        int num_unique_contributions
        int num_total_ratings
        int num_total_comments
        int num_total_neutral_comments
        int num_total_positive_comments
        int num_total_negative_comments
        int num_total_inline_comments
        int num_total_suggestions
        int num_total_inline_suggestions
        int num_volunteers
    }

    COMMENT {
        varchar comment_id PK
        varchar proposal_id FK
        varchar user_id FK
        varchar parent_comment_id FK
        varchar text
        varchar emotion
        int level
        int time_spent
        bool is_anonymous
        bool is_flagged
        int creation_timestamp
        varchar creation_datetime
        int num_total_replies
        int num_endorse_up_reactions
        int num_endorse_down_reactions
        int num_anger_reactions
        int num_celebrate_reactions
        int num_clap_reactions
        int num_curious_reactions
        int num_genius_reactions
        int num_happy_reactions
        int num_hot_reactions
        int num_laugh_reactions
        int num_love_reactions
        int num_sad_reactions
    }

    REACTION {
        varchar reaction_id PK
        varchar comment_id FK
        varchar user_id FK
        varchar reaction_type
        int creation_timestamp
        varchar creation_datetime
    }

    VIEW {
        varchar view_id PK
        varchar proposal_id FK
        varchar user_id FK
    }

    USER ||--|{ ENGAGEMENT_SCORE : has
    USER ||--|{ REWARDS : gets
    USER ||--|{ PROPOSAL : proposes
    USER ||--|{ RATING : gives
    USER ||--|{ COMMENT : makes
    USER ||--|{ REACTION : gives
    USER ||--|{ VIEW : makes
    PROPOSAL ||--|{ RATING : rates
    PROPOSAL ||--|{ COMMENT : has
    PROPOSAL ||--|{ VIEW : has
    MISSION ||--|{ PROPOSAL : has
    COMMENT ||--|{ COMMENT : has_children
    COMMENT ||--|{ REACTION : has
```