"""
Test: Use tidalapi's client_id + client_secret to get a token via device code,
then search for user playlists.

The key difference we discovered:
- Our code: client_id=fX2JxdmntZWK0ixT, NO client_secret
- tidalapi:  client_id=fX2JxdmntZWK0ixT, client_secret=1Nn9AfDAjxrgJFJbKNWLeAyKGVGmINuXPPLHVXAvxAg=
"""
import json, requests
from datetime import datetime, timedelta

CLIENT_ID = "fX2JxdmntZWK0ixT"
CLIENT_SECRET = "1Nn9AfDAjxrgJFJbKNWLeAyKGVGmINuXPPLHVXAvxAg="

with open("backend/orpheusdl/config/soundhaven_session.json") as f:
    d = json.load(f)

desktop_refresh = d.get("desktop_refresh_token")
country = d.get("country_code", "CA")

if not desktop_refresh:
    print("No desktop_refresh_token found!")
    exit(1)

# First: try to refresh the desktop token WITH client_secret
print("=== Refreshing desktop token WITH client_secret ===")
r = requests.post("https://auth.tidal.com/v1/oauth2/token", data={
    "refresh_token": desktop_refresh,
    "client_id": CLIENT_ID,
    "client_secret": CLIENT_SECRET,
    "grant_type": "refresh_token"
})
print(f"Refresh status: {r.status_code}")
if r.status_code != 200:
    print(f"Refresh failed: {r.text[:300]}")
    
    # Try WITHOUT client_secret
    print("\n=== Refreshing desktop token WITHOUT client_secret ===")
    r = requests.post("https://auth.tidal.com/v1/oauth2/token", data={
        "refresh_token": desktop_refresh,
        "client_id": CLIENT_ID,
        "grant_type": "refresh_token"
    })
    print(f"Refresh status: {r.status_code}")
    if r.status_code != 200:
        print(f"Both refreshes failed: {r.text[:300]}")
        exit(1)

fresh_token = r.json()["access_token"]
print(f"Got fresh token: {fresh_token[:30]}...")

# Now search with the fresh token
print("\n=== Search for 'riria' with FRESH token ===")
headers = {"Authorization": f"Bearer {fresh_token}"}
params = {"query": "riria", "limit": 50, "countryCode": country, "types": "PLAYLISTS"}
r = requests.get("https://api.tidal.com/v1/search", params=params, headers=headers)
print(f"Status: {r.status_code}")
if r.status_code == 200:
    items = r.json().get("playlists", {}).get("items", [])
    print(f"Total playlists: {len(items)}")
    user_count = 0
    for p in items:
        creator = p.get("creator") or {}
        cname = creator.get("name", "?") if isinstance(creator, dict) else str(creator)
        ptype = p.get("type", "?")
        if ptype != "EDITORIAL":
            user_count += 1
        print(f"  - [{ptype}] {p.get('title', '?')} by {cname}")
    print(f"\nUser playlists found: {user_count}")

# Also test with X-Tidal-Token header (like tidalapi does)
print("\n=== Search with X-Tidal-Token header ===")
headers2 = {
    "Authorization": f"Bearer {fresh_token}",
    "X-Tidal-Token": CLIENT_ID,
}
r = requests.get("https://api.tidal.com/v1/search", params=params, headers=headers2)
print(f"Status: {r.status_code}")
if r.status_code == 200:
    items = r.json().get("playlists", {}).get("items", [])
    print(f"Total playlists: {len(items)}")
    user_count = 0
    for p in items:
        creator = p.get("creator") or {}
        cname = creator.get("name", "?") if isinstance(creator, dict) else str(creator)
        ptype = p.get("type", "?")
        if ptype != "EDITORIAL":
            user_count += 1
        print(f"  - [{ptype}] {p.get('title', '?')} by {cname}")
    print(f"\nUser playlists found: {user_count}")

# Try searching for 'misekai' (another user playlist the user mentioned)
print("\n=== Search for 'misekai' ===")
params["query"] = "misekai"
r = requests.get("https://api.tidal.com/v1/search", params=params, headers=headers)
print(f"Status: {r.status_code}")
if r.status_code == 200:
    items = r.json().get("playlists", {}).get("items", [])
    print(f"Total playlists: {len(items)}")
    for p in items[:10]:
        creator = p.get("creator") or {}
        cname = creator.get("name", "?") if isinstance(creator, dict) else str(creator)
        ptype = p.get("type", "?")
        print(f"  - [{ptype}] {p.get('title', '?')} by {cname}")

# Test the SEARCH/TOP endpoint (used by the TIDAL web app)
print("\n=== Search for 'riria' via search/top endpoint ===")
params_top = {"query": "riria", "limit": 50, "countryCode": country}
r = requests.get("https://api.tidal.com/v1/search/top", params=params_top, headers=headers)
print(f"Status: {r.status_code}")
if r.status_code == 200:
    data = r.json()
    print(json.dumps(data, indent=2)[:500])
