"""
Test TIDAL API v2 search endpoint.
The TIDAL web app (listen.tidal.com) uses api.tidal.com/v2/ for searching,
which may include user playlists.
"""
import json, requests

CLIENT_ID = "fX2JxdmntZWK0ixT"
CLIENT_SECRET = "1Nn9AfDAjxrgJFJbKNWLeAyKGVGmINuXPPLHVXAvxAg="

with open("backend/orpheusdl/config/soundhaven_session.json") as f:
    d = json.load(f)

# Refresh token
desktop_refresh = d.get("desktop_refresh_token")
country = d.get("country_code", "CA")

r = requests.post("https://auth.tidal.com/v1/oauth2/token", data={
    "refresh_token": desktop_refresh,
    "client_id": CLIENT_ID,
    "client_secret": CLIENT_SECRET,
    "grant_type": "refresh_token"
})
if r.status_code != 200:
    print(f"Refresh failed: {r.status_code}")
    exit(1)

token = r.json()["access_token"]
headers = {"Authorization": f"Bearer {token}"}

# Test 1: v2 search endpoint
print("=== api.tidal.com/v2/search ===")
params = {"query": "riria", "limit": 50, "countryCode": country, "types": "PLAYLISTS"}
r = requests.get("https://api.tidal.com/v2/search", params=params, headers=headers)
print(f"Status: {r.status_code}")
if r.status_code == 200:
    data = r.json()
    print(json.dumps(data, indent=2)[:1000])
else:
    print(r.text[:300])

# Test 2: openapi search endpoint
print("\n=== openapi.tidal.com/v2/searchresults ===")
params2 = {"query": "riria", "limit": 50, "countryCode": country, "type": "PLAYLISTS"}
r = requests.get("https://openapi.tidal.com/v2/searchresults", params=params2, headers=headers)
print(f"Status: {r.status_code}")
if r.status_code == 200:
    data = r.json()
    print(json.dumps(data, indent=2)[:1000])
else:
    print(r.text[:300])

# Test 3: search with USERS type (TIDAL web app includes this)
print("\n=== v1 search with USERS type ===")
params3 = {"query": "riria", "limit": 50, "countryCode": country, "types": "TRACKS,ALBUMS,ARTISTS,PLAYLISTS,USERS"}
r = requests.get("https://api.tidal.com/v1/search", params=params3, headers=headers)
print(f"Status: {r.status_code}")
if r.status_code == 200:
    data = r.json()
    # Check for users in results
    for key in data.keys():
        items = data[key].get("items", []) if isinstance(data[key], dict) else []
        print(f"  {key}: {len(items)} items")
else:
    print(r.text[:300])

# Test 4: search with type=USERPROFILES  
print("\n=== v1 search with USERPROFILES type ===")
params4 = {"query": "riria", "limit": 50, "countryCode": country, "types": "USERPROFILES"}
r = requests.get("https://api.tidal.com/v1/search", params=params4, headers=headers)
print(f"Status: {r.status_code}")
if r.status_code == 200:
    data = r.json()
    print(json.dumps(data, indent=2)[:1000])
else:
    print(r.text[:300])

# Test 5: v1 search for 'yuika' - since user mentioned this as the main search term
print("\n=== v1 search for 'yuika' ALL types ===")
params5 = {"query": "yuika", "limit": 50, "countryCode": country, "types": "TRACKS,ALBUMS,ARTISTS,PLAYLISTS"}
r = requests.get("https://api.tidal.com/v1/search", params=params5, headers=headers)
print(f"Status: {r.status_code}")
if r.status_code == 200:
    data = r.json()
    for key in data.keys():
        items = data[key].get("items", []) if isinstance(data[key], dict) else []
        if key == "playlists":
            print(f"  {key}: {len(items)} items")
            for p in items[:5]:
                creator = p.get("creator") or {}
                cname = creator.get("name", "?") if isinstance(creator, dict) else str(creator)
                ptype = p.get("type", "?")
                print(f"    - [{ptype}] {p.get('title', '?')} by {cname}")
        else:
            print(f"  {key}: {len(items)} items")
