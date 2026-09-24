import requests, re, json
r = requests.get('https://tidal.com/search/playlists?q=riria')
print(r.status_code)
# Search for JSON state
match = re.search(r'__PRELOADED_STATE__\s*=\s*(.*?);', r.text)
if match:
    print('Found preloaded state!')
else:
    print('No preloaded state. Looking for next data...')
    match2 = re.search(r'id="__NEXT_DATA__" type="application/json">({.*?})</script>', r.text)
    if match2:
        print('Found NEXT_DATA')
        try:
            d = json.loads(match2.group(1))
            print(d.keys())
        except Exception as e:
            print(e)
    else:
        print('Not found')
