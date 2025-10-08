import requests
import urllib.parse
from flask import Flask, redirect, request, jsonify, session
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler

app = Flask(__name__)
app.secret_key = "53d355f8-571a-4590-a310-1f9579440851"

# these are will be in your dashboard in the details of the app
CLIENT_ID = ""
CLIENT_SECRET = ""
# this will just run it on your machine, if we all want to be on the same site we might be able to change to public IP
REDIRECT_URI = 'http://127.0.0.1:8080/callback'

AUTH_URL = "https://accounts.spotify.com/authorize"
TOKEN_URL = "https://accounts.spotify.com/api/token"
API_BASE_URL = 'https://api.spotify.com/v1/'


# whenever someone visits this ending of the website (sends a GET request), run this function
@app.route('/')
def index():
    return "Welcome to our spotify app <a href='/login'>Login with Spotify</a>"


@app.route('/login')
def login():
    scope = 'user-read-private user-read-email'

    params = {
        'client_id': CLIENT_ID,
        'response_type': 'code',
        'scope': scope,
        'redirect_uri': REDIRECT_URI,
        # forcing user to log in every time **for testing**
        'show_dialog': True
    }

    auth_url = f"{AUTH_URL}?{urllib.parse.urlencode(params) }"

    return redirect(auth_url)


@app.route('/callback')
def callback():
    if 'error' in request.args:
         return jsonify({'error': request.args['error']})
     
    if 'code' in request.args:
         req_body = {
             'code' : request.args['code'],
             'grant_type' :'authorization_code',
             'redirect_uri' : REDIRECT_URI,
             'client_id' : CLIENT_ID,
             'client_secret': CLIENT_SECRET
         }
    
    response = requests.post(TOKEN_URL, data=req_body)
    token_info = response.json()

    session['access_token'] = token_info['access_token']
    session['refresh_token'] = token_info['refresh_token']
    session['expires_at'] = datetime.now().timestamp() + token_info['expires_in'] 

    return redirect('/playlists')


@app.route('/playlists')
def get_playlists():
    if 'access_token' not in session:
        return redirect('/login')
    
    # if token is expired
    if datetime.now().timestamp() > session['expires_at']:
        return redirect('/refresh-token')

    # prepares HTTP headers
    headers= {
        'Authorization': f"Bearer {session['access_token']}"
    }


    response = requests.get(API_BASE_URL + 'me/playlists', headers=headers)


    #### imported methods for parsing the data goes here #######
    playlists = response.json()
    print(playlists)

    return jsonify(playlists)


@app.route('/refresh-token')
def refresh_token():
    if 'refresh_token' not in session:
        return redirect('/login')
    
    # check if the access token has expired
    if datetime.now().timestamp() > session['expires_at']:
        # request fresh token
        req_body = {
            'grant_type': 'refresh_token',
            'refresh_token': session['refresh_token'],
            'client_id': CLIENT_ID,
            'client_secret': CLIENT_SECRET
        }

        response = requests.post(TOKEN_URL, data=req_body)
        new_token_info = response.json()
        session['access_token'] = new_token_info['access_token']
        session['expires_at'] = datetime.now().timestamp() + new_token_info['expires_in']

        return redirect('/playlists')
    



if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)



         







