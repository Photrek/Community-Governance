"""
Download voting portal data to the local database
"""

import os
import json
import requests
import models
import cesdb

from typing import Callable

url = os.getenv('VOTING_PORTAL_HOST')

con = cesdb.get_db_connection()

def load_proposals(progress_updater: Callable[[int, int], None]) -> None:
    rounds = con.sql("SELECT id FROM stg_pp_rounds").fetchall()
    round_ids = [row[0] for row in rounds]

    proposals = []
    for idx, round in enumerate(round_ids, start=1):
        response = __download_proposals(round_id=round)
        proposals.extend(response)
        progress_updater(idx, len(round_ids))

    __save_to_json(proposals, 'data/proposals.json')

    models.load(con, 'models/staging/proposal_portal/stg_pp_proposals.sql')

def __download_proposals(round_id):
    response = requests.get(f"{url}/rounds/{round_id}/proposals")
    raw_data = response.json()

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

def load_reviews(progress_updater: Callable[[int, int], None]) -> None:
    __batch_load('reviews', 'reviews', progress_updater)

def load_comment_votes(progress_updater: Callable[[int, int], None]) -> None:
    __batch_load('comment_votes', 'votes', progress_updater, model_name='comment_votes')

def load_milestones(progress_updater: Callable[[int, int], None]) -> None:
    __batch_load('milestones', 'milestones', progress_updater)

def load_rounds_and_pools_connection() -> None:
    rounds, rounds_pools = __fetch_rounds_pools()
    
    __save_to_json(rounds, 'data/rounds.json')
    __save_to_json(rounds_pools, 'data/rounds_pools.json')

    models.load(con, 'models/staging/proposal_portal/stg_pp_rounds.sql')
    models.load(con, 'models/staging/proposal_portal/stg_pp_rounds_pools.sql')

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

def load_pools() -> None:
    # download the voting portal data
    response = requests.get(f"{url}/pools")
    raw_data = response.json()  # Convert response to JSON format

    __save_to_json(raw_data, 'data/pools.json')

    models.load(con, 'models/staging/proposal_portal/stg_pp_pools.sql')

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


def load_users(progress_updater: Callable[[int, int], None]) -> None:
    __batch_load('users', 'users', progress_updater)

def load_comments(progress_updater: Callable[[int, int], None]) -> None:
    __batch_load('comments', 'comments', progress_updater)

def __batch_load(endpoint_path: str, 
                 selector: str,
                 progress_updater: Callable[[int, int], None],
                 model_name: str = None) -> None:
    if model_name is None:
        model_name = selector

    all_data = []
    for page_number, (page_data, total_pages) in enumerate(fetch_pages(endpoint_path, selector), start=1):
        all_data.extend(page_data)
        progress_updater(page_number, total_pages)

    __save_to_json(all_data, f'data/{model_name}.json')

    print(f"Loading model: {model_name}")
    models.load(con, f'models/staging/proposal_portal/stg_pp_{model_name}.sql')

def __save_to_json(data, path):
    print(f"Saving data to {path}")
    with open(path, 'w') as f:
        json.dump(data, f)