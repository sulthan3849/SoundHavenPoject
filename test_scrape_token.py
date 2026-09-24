import requests, re

def get_web_token():
    try:
        print("Fetching listen.tidal.com...")
        r = requests.get('https://listen.tidal.com')
        js_files = re.findall(r'src="(/[^"]+\.js)"', r.text)
        print("JS Files found:", js_files)
        
        for js in js_files:
            js_url = f"https://listen.tidal.com{js}"
            print("Fetching", js_url)
            r2 = requests.get(js_url)
            
            # Check for client_id or x-tidal-token
            client_id = re.search(r'clientId:\s*["\']([a-zA-Z0-9\-_]+)["\']', r2.text)
            if client_id:
                print("Found Client ID:", client_id.group(1))
            
            token = re.search(r'x-tidal-token["\']?:\s*["\']([a-zA-Z0-9\-_]+)["\']', r2.text, re.IGNORECASE)
            if token:
                print("Found Token:", token.group(1))
                return token.group(1)
        return None
    except Exception as e:
        return str(e)

print(get_web_token())
