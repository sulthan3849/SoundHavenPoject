
import urllib.request
import re

req = urllib.request.Request('https://listen.tidal.com/', headers={'User-Agent': 'Mozilla/5.0'})
try:
    html = urllib.request.urlopen(req).read().decode('utf-8')
    scripts = re.findall(r'<script[^>]+src=[\'\"]([^\'\"]+\.js)', html)
    print(scripts)
except Exception as e:
    print(e)

