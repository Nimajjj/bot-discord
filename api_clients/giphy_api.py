# Giphy API setup
import os
import random
import requests

GIPHY_SEARCH_URL = 'https://api.giphy.com/v1/gifs/search'


def fetch_gif(search):
    response = requests.get(GIPHY_SEARCH_URL, params={
        'api_key': os.getenv("GIPHY_TOKEN"),
        'q': search,
        'limit': 5
    })
    response.raise_for_status()
    data = response.json()

    if data['data']:
        return random.choice(data['data'])['url']
    return None