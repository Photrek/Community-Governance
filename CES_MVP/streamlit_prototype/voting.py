"""
Download voting portal data to the local database
"""

import os
import json
import requests
import models
import duckdb

from typing import Callable

url = os.getenv('VOTING_PORTAL_HOST')


def load_proposals(con: duckdb.DuckDBPyConnection,
                   progress_updater: Callable[[int, int], None]) -> None:
    rounds = con.sql("SELECT id FROM silver_rounds").fetchall()
    round_ids = [row[0] for row in rounds]

    proposals = []
    for idx, round in enumerate(round_ids, start=1):
        response = __download_proposals(round_id=round)
        proposals.extend(response)
        progress_updater(idx, len(round_ids))

    __save_to_json(proposals, 'data/proposals.json')

    models.load(con, 'models/silver_proposals.sql')

def __download_proposals(round_id):
    response = requests.get(f"{url}/rounds/{round_id}/proposals")
    raw_data = response.json()
    # return raw_data['proposals']

    proposals = []
    for vote in raw_data['proposals']:
        proposals.append({
            'id': vote['id'],
            'round_id': round_id,
            'pool_id': vote['pool_id'],
            'proposer_id': vote['proposer_id'],
            'title': vote['title'],
            'content': vote['content'],
            'link': vote['link'],
            'feature_image': vote['feature_image'],
            'requested_amount': vote['requested_amount'],
            'awarded_amount': vote['awarded_amount'],
            'is_awarded': vote['is_awarded'],
            'created_at': vote['created_at'],
        })
    return proposals


def load_reviews(con: duckdb.DuckDBPyConnection,
                 progress_updater: Callable[[int, int], None]) -> None:
    proposals = con.sql("SELECT id FROM silver_proposals").fetchall()
    proposal_ids = [row[0] for row in proposals]

    reviews = []
    for idx, proposal in enumerate(proposal_ids, start=1):
        response = __download_reviews(proposal_id=proposal)
        reviews.extend(response)
        progress_updater(idx, len(proposal_ids))

    __save_to_json(reviews, 'data/reviews.json')

    models.load(con, 'models/silver_reviews.sql')

def __download_reviews(proposal_id):
    response = requests.get(f"{url}/proposals/{proposal_id}/reviews")
    raw_data = response.json()

    # check if reviews where found
    if not isinstance(raw_data['reviews'], list):
        print(f"no reviews found for proposal: {proposal_id}")
        return []
    ''''''
    print(raw_data)

    reviews = []
    for review in raw_data['reviews']:
        reviews.append({
            'proposal_id': proposal_id,
            'review_id': review['review_id'],
            'reviewer_id': review['reviewer_id'],
            'review_type': review['review_type'],
            'overall_rating': review['overall_rating'],
            'feasibility_rating': review['feasibility_rating'],
            'viability_rating': review['viability_rating'],
            'desirability_rating': review['desirability_rating'],
            'usefulness_rating': review['usefulness_rating'],
            'created_at': review['created_at'],
        })
    return reviews

def load_comment_votes(con: duckdb.DuckDBPyConnection,
                       progress_updater: Callable[[int, int], None]) -> None:
    comments = con.sql("SELECT * FROM silver_comments WHERE comment_votes > 0").fetchall()
    comments_ids = [row[0] for row in comments]

    comment_votes = []
    for idx, comment in enumerate(comments_ids, start=1):
        response = __download_comment_votes(comment_id=comment)
        comment_votes.extend(response)
        progress_updater(idx, len(comments_ids))

    __save_to_json(comment_votes, 'data/comment_votes.json')

    models.load(con, 'models/silver_comment_votes.sql')

def __download_comment_votes(comment_id):
    response = requests.get(f"{url}/comments/{comment_id}/votes")
    raw_data = response.json()

    votes = []
    for vote in raw_data['votes']:
        votes.append({
            'comment_id': comment_id,
            'voter_id': vote['voter_id'],
            'vote_type': vote['vote_type'],
        })
    return votes

def load_milestones(con: duckdb.DuckDBPyConnection,
                    progress_updater: Callable[[int, int], None]) -> None:
    proposals = con.sql("SELECT id FROM silver_proposals").fetchall()
    proposal_ids = [row[0] for row in proposals]

    milestones = []
    for idx, proposal in enumerate(proposal_ids, start=1):
        response = __download_milestones(proposal_id=proposal)
        milestones.extend(response)
        progress_updater(idx, len(proposal_ids))

    __save_to_json(milestones, 'data/milestones.json')

    models.load(con, 'models/silver_milestones.sql')

def __download_milestones(proposal_id):
    response = requests.get(f"{url}/proposals/{proposal_id}/milestones")
    raw_data = response.json()
    
    milestones = []
    for milestone in raw_data['milestones']:
        milestones.append({
            'proposal_id': proposal_id,
            'title': milestone['title'],
            'status': milestone['status'],
            'description': milestone['description'],
            'development_description': milestone['development_description'],
            'budget': milestone['budget'],
        })
    return milestones

def load_rounds_and_pools_connection(con: duckdb.DuckDBPyConnection) -> None:
    rounds, rounds_pools = __fetch_rounds_pools()
    
    __save_to_json(rounds, 'data/rounds.json')
    __save_to_json(rounds_pools, 'data/rounds_pools.json')

    models.load(con, 'models/silver_rounds.sql')
    models.load(con, 'models/silver_rounds_pools.sql')

def __fetch_rounds_pools():
    response = requests.get(f"{url}/rounds")
    raw_data = response.json()
    
    rounds = []
    rounds_pools = []

    # Extract round pool mapping
    for round in raw_data:
        rounds.append({
            'id': round['id'],
            'name': round['name'],
            'slug': round['slug'],
            'description': round['description'],
        })
        for pool in round['pool_id']:
            rounds_pools.append({
                'round_id': round['id'],
                'pool_id': pool['id']
            })
            
    return rounds,rounds_pools

def load_pools(con: duckdb.DuckDBPyConnection) -> None:
    # download the voting portal data
    response = requests.get(f"{url}/pools")
    raw_data = response.json()  # Convert response to JSON format

    __save_to_json(raw_data, 'data/pools.json')

    models.load(con, 'models/silver_pools.sql')

def fetch_pages(endpoint_path: str, selector: str):
    page = 1

    while True:
        response = requests.get(f"{url}/{endpoint_path}", params={'page': page, 'limit': 500})
        data = response.json()

        total_pages = data['pagination']['total_pages']

        yield (data[selector], total_pages)

        if data['pagination']['next_page'] is None:
            break

        page = data['pagination']['next_page']


def load_users(con: duckdb.DuckDBPyConnection, progress_updater: Callable[[int, int], None]) -> None:
    __batch_load(con, 'users', 'users', progress_updater)

def load_comments(con: duckdb.DuckDBPyConnection, progress_updater: Callable[[int, int], None]) -> None:
    __batch_load(con, 'comments', 'comments', progress_updater)

def __batch_load(con: duckdb.DuckDBPyConnection,
              endpoint_path: str, 
              selector: str,
              progress_updater: Callable[[int, int], None]) -> None:
    all_data = []
    for page_number, (page_data, total_pages) in enumerate(fetch_pages(endpoint_path, selector), start=1):
        all_data.extend(page_data)
        progress_updater(page_number, total_pages)

    __save_to_json(all_data, f'data/{selector}.json')

    models.load(con, f'models/silver_{selector}.sql')


def __save_to_json(data, path):
    with open(path, 'w') as f:
        json.dump(data, f)