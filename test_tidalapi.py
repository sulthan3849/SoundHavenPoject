"""
Test TIDAL search using the tidalapi library directly with saved credentials.
This is the library the user had previously working.
"""
import json, tidalapi
from datetime import datetime

with open("backend/orpheusdl/config/soundhaven_session.json") as f:
    d = json.load(f)

# Create a session using tidalapi with the desktop token
session = tidalapi.Session()

# Manually set the session tokens from our saved data
session.access_token = d.get("desktop_access_token")
session.refresh_token = d.get("desktop_refresh_token")
session.token_type = "Bearer"
session.country_code = d.get("country_code", "CA")
session.user = None
session.session_id = None

# First, try to refresh the token properly through tidalapi
try:
    refreshed = session.token_refresh(d.get("desktop_refresh_token"))
    print(f"Token refresh via tidalapi: {refreshed}")
except Exception as e:
    print(f"Token refresh failed: {e}")

# Now search
try:
    results = session.search("riria", models=[tidalapi.playlist.Playlist], limit=50)
    playlists = results.get("playlists", [])
    print(f"\nSearch 'riria' via tidalapi: {len(playlists)} playlists")
    for p in playlists[:10]:
        creator_name = "?"
        try:
            if hasattr(p, 'creator') and p.creator:
                creator_name = p.creator.name if hasattr(p.creator, 'name') else str(p.creator)
        except:
            pass
        ptype = getattr(p, 'type', '?')
        print(f"  - [{ptype}] {p.name} by {creator_name}")
except Exception as e:
    print(f"Search failed: {e}")

# Search yuika
try:
    results = session.search("yuika", models=[tidalapi.playlist.Playlist], limit=50)
    playlists = results.get("playlists", [])
    print(f"\nSearch 'yuika' via tidalapi: {len(playlists)} playlists")
    for p in playlists[:10]:
        creator_name = "?"
        try:
            if hasattr(p, 'creator') and p.creator:
                creator_name = p.creator.name if hasattr(p.creator, 'name') else str(p.creator)
        except:
            pass
        ptype = getattr(p, 'type', '?')
        print(f"  - [{ptype}] {p.name} by {creator_name}")
except Exception as e:
    print(f"Search yuika failed: {e}")

# Search ALL types for yuika
try:
    results = session.search("yuika", limit=50)
    for key, val in results.items():
        if isinstance(val, list):
            print(f"\nyuika {key}: {len(val)} items")
            for item in val[:3]:
                print(f"  - {getattr(item, 'name', getattr(item, 'title', str(item)))}")
        elif val is not None:
            print(f"\nyuika {key}: {val}")
except Exception as e:
    print(f"Full search failed: {e}")
