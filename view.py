import requests
import urllib
import os


def latex2png(code):
    print(code)
    print(urllib.parse.quote(code))
    url = 'https://latex.codecogs.com/png.latex'
    url = url + '?' + urllib.parse.quote(code)
    print(url)
    r = requests.get(url, stream=True)
    with open('out.png', 'wb') as f:
        f.write(r.raw.read())
    os.system('out.png')
