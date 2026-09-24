import requests, json
r = requests.get("http://localhost:8000/api/search?q=riria&limit=50")
d = r.json()
print(f"Tracks: {len(d['tracks'])}")
print(f"Albums: {len(d['albums'])}")
print(f"Playlists: {len(d['playlists'])}")
for p in d['playlists'][:5]:
    print(f"  - {p['title']} by {p['creator']}")
