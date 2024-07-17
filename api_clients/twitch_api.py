import os
import requests

# Twitch credentials
TWITCH_TOKEN_URL = 'https://id.twitch.tv/oauth2/token'
TWITCH_API_URL = 'https://api.twitch.tv/helix'
STREAMERS = ['zerator', 'ponce', 'dealabs', 'shisheyu', 'ayfri_', 'jaepasdargent']

online_streamers = set()

def get_twitch_oauth_token():
    response = requests.post(TWITCH_TOKEN_URL, params={
        'client_id': os.getenv("TWITCH_CLIENT_ID"),
        'client_secret': os.getenv("TWITCH_CLIENT_TOKEN"),
        'grant_type': 'client_credentials'
    })
    response.raise_for_status()
    return response.json()['access_token']


def check_streamers_online():
    global online_streamers
    token = get_twitch_oauth_token()
    headers = {
        'Client-ID': os.getenv("TWITCH_CLIENT_ID"),
        'Authorization': f'Bearer {token}'
    }

    response = requests.get(f'{TWITCH_API_URL}/streams', headers=headers, params={
        'user_login': STREAMERS
    })
    response.raise_for_status()
    data = response.json()['data']

    current_online_streamers = {stream['user_name'] for stream in data}
    newly_online_streamers = current_online_streamers - online_streamers
    offline_streamers = online_streamers - current_online_streamers

    # for user in newly_online_streamers:
    #     print(f"[DEBUG] {user} is online")
    # for user in offline_streamers:
    #     print(f"[DEBUG] {user} is offline")

    online_streamers = current_online_streamers
    return newly_online_streamers