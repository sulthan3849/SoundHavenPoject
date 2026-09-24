import json, requests

with open("backend/orpheusdl/config/soundhaven_session.json") as f:
    d = json.load(f)

desktop_token = d.get("desktop_access_token")
tv_token = d.get("access_token")
country = d.get("country_code", "CA")

print("=== Desktop Token Search for 'riria' ===")
if desktop_token:
    headers = {"Authorization": f"Bearer {desktop_token}"}
    params = {"query": "riria", "limit": 50, "countryCode": country, "types": "PLAYLISTS"}
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
    else:
        print(f"Error: {r.text[:300]}")
else:
    print("No desktop token found")

# Refresh TV token
print("\n=== TV Token Search for 'riria' ===")
tv_secret = "1nqpgx8uvBdZigrx4hUPDV2hOwgYAAAG5DYXOr6uNf8="
tv_client_id = "cgiF7TQuB97BUIu3"
r = requests.post("https://auth.tidal.com/v1/oauth2/token", data={
    "refresh_token": d["refresh_token"],
    "client_id": tv_client_id,
    "client_secret": tv_secret,
    "grant_type": "refresh_token"
})
if r.status_code == 200:
    fresh_tv = r.json()["access_token"]
    headers = {"Authorization": f"Bearer {fresh_tv}"}
    params = {"query": "riria", "limit": 50, "countryCode": country, "types": "PLAYLISTS"}
    r2 = requests.get("https://api.tidal.com/v1/search", params=params, headers=headers)
    print(f"Status: {r2.status_code}")
    if r2.status_code == 200:
        items = r2.json().get("playlists", {}).get("items", [])
        print(f"Total playlists: {len(items)}")
        for p in items[:10]:
            creator = p.get("creator") or {}
            cname = creator.get("name", "?") if isinstance(creator, dict) else str(creator)
            ptype = p.get("type", "?")
            print(f"  - [{ptype}] {p.get('title', '?')} by {cname}")
    else:
        print(f"Error: {r2.text[:300]}")
else:
    print(f"TV refresh failed: {r.status_code} {r.text[:300]}")

# Now test with desktop token for 'yuika'
print("\n=== Desktop Token Search for 'yuika' ===")
if desktop_token:
    headers = {"Authorization": f"Bearer {desktop_token}"}
    params = {"query": "yuika", "limit": 50, "countryCode": country, "types": "PLAYLISTS"}
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
    else:
        print(f"Error: {r.text[:300]}")

# Test with NO countryCode (maybe the country restriction is the issue)
print("\n=== Desktop Token Search for 'riria' WITHOUT countryCode ===")
if desktop_token:
    headers = {"Authorization": f"Bearer {desktop_token}"}
    params = {"query": "riria", "limit": 50, "types": "PLAYLISTS"}
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
    else:
        print(f"Error: {r.text[:300]}")

# Test with countryCode=US
print("\n=== Desktop Token Search for 'riria' with countryCode=US ===")
if desktop_token:
    headers = {"Authorization": f"Bearer {desktop_token}"}
    params = {"query": "riria", "limit": 50, "countryCode": "US", "types": "PLAYLISTS"}
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
    else:
        print(f"Error: {r.text[:300]}")

# Test with includeUserPlaylists
print("\n=== Desktop Token with includeUserPlaylists ===")
if desktop_token:
    headers = {"Authorization": f"Bearer {desktop_token}"}
    params = {"query": "riria", "limit": 50, "countryCode": country, "types": "PLAYLISTS", "includeUserPlaylists": "true"}
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
    else:
        print(f"Error: {r.text[:300]}")
