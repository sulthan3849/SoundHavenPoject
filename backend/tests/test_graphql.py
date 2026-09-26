import requests as req
import json

headers = {'x-tidal-token': 'czdes45c55cg322b', 'Content-Type': 'application/json'}
q = {'query': 'query { search(query: "yuika") { playlists { items { title } } } }'}
r = req.post('https://listen.tidal.com/graphql', json=q, headers=headers)
print(r.status_code)
print(r.text)
