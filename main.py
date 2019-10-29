import json
from flask import Flask, request, g, redirect, render_template
import requests
from urllib.parse import quote
from os import path

app = Flask(__name__)


CLIENT_ID = 'a937516e-a6a3-46db-add3-6702851593c2'
CLIENT_SECRET = '7PmMsg2V9XOvuDhaBflAKg'

CTCT_AUTH_URL = 'https://api.cc.email/v3/idfed'
CTCT_TOKEN_URL = 'https://idfed.constantcontact.com/as/token.oauth2'
CTCT_API_URL = 'https://api.cc.email/v3'

CLIENT_SIDE_URL = 'http://127.0.0.1'
PORT = 5000
REDIRECT_URI = "https://localhost:8888/oauth/redirect"
SCOPE = 'contact_data+campaign_data'


auth_query_parameters = {
    'response_type': 'code',
    'redirect_uri': REDIRECT_URI,
    'scope': SCOPE,
    'client_id': CLIENT_ID,
}

authorization_redirect_url = CTCT_AUTH_URL + '?response_type=code&client_id=' + CLIENT_ID + '&redirect_uri=' + REDIRECT_URI + '&scope=contact_data+campaign_data'

@app.route('/', methods=['GET'])
def index():
    if path.exists('tokens.txt'):
        pass
    else:
        url_args = '&'.join(['{}={}'.format(key, quote(val)) for key, val in auth_query_parameters.items()])
        auth_url = '{}/?{}'.format(CTCT_AUTH_URL, url_args)
    return redirect(authorization_redirect_url)


@app.route('/callback/q')
def callback():
    auth_code = request.args.get('code')

    code_payload = {
        'grant_type': 'authorization_code',
        'code': auth_code,
        'redirect_uri': REDIRECT_URI
    }
    post_request = requests.post(CTCT_TOKEN_URL, data=code_payload, verify=False,
                                 allow_redirects=True, auth=(CLIENT_ID, CLIENT_SECRET))

    response_data = json.loads(post_request.headers)


    access_token = response_data['access_token']
    refresh_token = response_data['refresh_token']
    token_type = response_data['token_type']

    authorization_header = {'Authorization': 'Basic {}'.format(access_token)}

    all_campaigns_api_endpoint = '{}/emails'.format(CTCT_API_URL)
    campaigns_response = requests.get(all_campaigns_api_endpoint, headers=authorization_header)
    campaigns_data = json.loads(campaigns_response.text)
    
    display_arr = [campaigns_data]
    return render_template('index.html', sorted_array=display_arr)


if __name__ == '__main__':
    app.run(ssl_context='adhoc')
