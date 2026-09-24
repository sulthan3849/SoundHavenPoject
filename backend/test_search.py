
import requests, json

token = ''
with open('orpheusdl/config/soundhaven_session.json', 'r') as f:
    token = json.load(f).get('desktop_access_token')
headers = {'Authorization': f'Bearer {token}'}

# Try graphql endpoint?
# Try /v1/search endpoint with include parameters
for params in [
    {'query': 'harutya', 'limit': 50, 'countryCode': 'US', 'types': 'TRACKS,ALBUMS,ARTISTS,PLAYLISTS', 'includeUserPlaylists': 'true'},
    {'query': 'harutya', 'limit': 50, 'countryCode': 'US', 'types': 'TRACKS,ALBUMS,ARTISTS,PLAYLISTS', 'userPlaylists': 'true'},
    {'query': 'harutya', 'limit': 50, 'countryCode': 'US', 'types': 'TRACKS,ALBUMS,ARTISTS,PLAYLISTS,USER_PLAYLISTS'},
]:
    r = requests.get('https://api.tidal.com/v1/search', params=params, headers=headers)
    if r.status_code == 200:
        data = r.json()
        print('Params:', params)
        if 'playlists' in data:
            print('  Playlists:', len(data['playlists'].get('items', [])))
            for p in data['playlists'].get('items', []):
                print('    -', p.get('title').encode('ascii', 'ignore'))

