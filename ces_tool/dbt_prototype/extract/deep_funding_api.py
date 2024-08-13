"""
Download voting portal data to the local database
"""

import os
import json
import requests

from typing import Callable

url = os.getenv('VOTING_PORTAL_HOST')

# TODO: add way to download only new data

def load_proposals(rounds):
    print("Downloading proposals")
    round_ids = [row['id'] for row in rounds]

    proposals = []
    for idx, round in enumerate(round_ids, start=1):
        response = __download_proposals(round_id=round)
        proposals.extend(response)
        print(f"\tDownloaded {len(response)} proposals for round {idx}/{len(round_ids)}")

    __save_to_json(proposals, 'data/input/proposals.json')


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

def load_reviews():
    print("Downloading reviews")
    __batch_load('reviews', 'reviews')

def load_comment_votes():
    print("Downloading comment votes")
    __batch_load('comment_votes', 'votes', model_name='comment_votes')

def load_milestones():
    print("Downloading milestones")
    __batch_load('milestones', 'milestones')

def load_rounds_and_pools_connection():
    print("Downloading rounds and pools connection")
    rounds, rounds_pools = __fetch_rounds_pools()
    
    __save_to_json(rounds, 'data/input/rounds.json')
    __save_to_json(rounds_pools, 'data/input/rounds_pools.json')

    return rounds, rounds_pools


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
            
    return rounds, rounds_pools

def load_pools():
    print("Downloading pools")
    # download the voting portal data
    response = requests.get(f"{url}/pools")
    raw_data = response.json()  # Convert response to JSON format

    __save_to_json(raw_data, 'data/input/pools.json')


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


def load_users():
    print("Downloading users")
    __batch_load('users', 'users')

def load_comments():
    print("Downloading comments")
    __batch_load('comments', 'comments')

def __batch_load(endpoint_path: str, 
                 selector: str,
                 model_name: str = '') -> None:
    if '' == model_name:
        model_name = selector

    all_data = []
    for page_number, (page_data, total_pages) in enumerate(fetch_pages(endpoint_path, selector), start=1):
        all_data.extend(page_data)
        print(f"\tDownloaded {len(all_data)} {model_name} from {page_number}/{total_pages}")

    __save_to_json(all_data, f'data/input/{model_name}.json')

def __save_to_json(data, path):
    print(f"\t💾 Saving data to {path}")
    with open(path, 'w') as f:
        json.dump(data, f)


# add main that get executed when the file is run
if __name__ == '__main__':
    rounds, _ = load_rounds_and_pools_connection()
    load_proposals(rounds)
    load_reviews()
    load_comment_votes()
    load_milestones()
    load_pools()
    load_users()
    load_comments()