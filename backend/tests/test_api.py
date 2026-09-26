import urllib.request
import json

req = urllib.request.Request('http://localhost:8000/api/download/collection/start/album/189843871')
with urllib.request.urlopen(req) as response:
    start_data = json.loads(response.read())
    task_id = start_data['task_id']
    print('Started task:', task_id)

import time
for i in range(10):
    time.sleep(2)
    req = urllib.request.Request(f'http://localhost:8000/api/download/collection/status/{task_id}')
    with urllib.request.urlopen(req) as response:
        status_data = json.loads(response.read())
        print(status_data)
        if status_data.get('status') != 'processing':
            break
