"""
Download voting portal data to the local database
"""

import os
import json
import requests

url = os.getenv('VOTING_PORTAL_HOST')

def download_proposals(round_id):
    response = requests.get(f"{url}/rounds/{round_id}/proposals")
    raw_data = response.json()
    return raw_data['proposals']

def download_reviews(proposal_id):
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

def download_comment_votes(comment_id):
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

def download_milestones(proposal_id):
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

def download_rounds():
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
    
    with open('data/rounds.json', 'w') as f:
        json.dump(rounds, f)
    with open('data/rounds_pools.json', 'w') as f:
        json.dump(rounds_pools, f)
    
    

def download_pools():
    # download the voting portal data
    response = requests.get(f"{url}/pools")
    raw_data = response.json()  # Convert response to JSON format
    
    with open('data/pools.json', 'w') as f:
        json.dump(raw_data, f)

def download_users():
    return fetch_pages('users', 'users')

def download_comments():
    return fetch_pages('comments', 'comments')

def fetch_pages(endpoint: str, selector: str):
    page = 1

    while True:
        response = requests.get(f"{url}/{endpoint}", params={'page': page, 'limit': 500})
        data = response.json()

        total_pages = data['pagination']['total_pages']

        yield (data[selector], total_pages)

        if data['pagination']['next_page'] is None:
            break

        page = data['pagination']['next_page']