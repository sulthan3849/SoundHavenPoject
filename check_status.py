import urllib.request
import json
req = urllib.request.Request('http://localhost:8000/api/download/collection/status/8ab5a66c-edfe-4f94-bd39-c38a631004fd')
with urllib.request.urlopen(req) as response:
    print(json.loads(response.read()))
