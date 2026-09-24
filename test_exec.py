import urllib.request
req = urllib.request.Request('http://localhost:8000/api/search?q=test')
with urllib.request.urlopen(req) as response:
    pass
