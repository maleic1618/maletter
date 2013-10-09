import sys
from twython import Twython
from secretkey import *
import webbrowser

api = Twython(CONSUMER_KEY, CONSUMER_SECRET)
url = api.get_authentication_tokens()
webbrowser.open(url['auth_url'])

verifier = input("PIN code")
print url
api = Twython(CONSUMER_KEY, CONSUMER_SECRET, url['oauth_token'], url['oauth_token_secret'])
callback = api.get_authorized_tokens(int(verifier))

str = """CONSUMER_KEY = 'UTjGwUyLUStPp1B956snTQ'
CONSUMER_SECRET = 'VjpEYudF11XSN9vsMeQyycelvQmptHgqqmCmt1eI'
ACCESS_KEY = '""" + callback['oauth_token'] +"'\nACCESS_SECRET = '" + callback['oauth_token_secret'] + "'"

with open('secretkey.py', 'w') as f:
    f.write(str)