import requests
import base64
import urllib
from urllib.parse import urlencode, unquote
import webbrowser
import json

class SchwabAuth:
    def __init__(self, clientId, clientSecret, redirectUri):
        self.clientId = clientId
        self.clientSecret = clientSecret
        self.redirectUri = redirectUri
        self.tokenUrl = "https://api.schwabapi.com/v1/oauth/token"
        self.authUrl = "https://api.schwabapi.com/v1/oauth/authorize"
        self.accessToken = None
        self.refreshToken = None
        self.id_token = None
        self.tokenFilename = 'schwab_token.json'

    def getAuthUrl(self):
        params = {
            'client_id': self.clientId,
            'redirect_uri': self.redirectUri,
            'response_type': 'code'
        }
        return f"{self.authUrl}?{urlencode(params)}"

    def getTokens(self, authorizationCode):
        authorizationCode = unquote(authorizationCode)  # Ensure the authorization code is URL decoded
        
        authHeader = base64.b64encode(f"{self.clientId}:{self.clientSecret}".encode()).decode()

        headers = {
            'Authorization': f"Basic {authHeader}",
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        data = {
            'grant_type': 'authorization_code',
            'code': authorizationCode,
            'redirect_uri': self.redirectUri
        }
        response = requests.post(self.tokenUrl, headers=headers, data=data)
        if response.status_code == 200:
            tokens = response.json()
            self.accessToken = tokens['access_token']
            self.refreshToken = tokens['refresh_token']
            self.id_token = tokens['id_token']
        else:
            raise Exception(f"Failed to obtain tokens: {response.text}")

    def refreshAccessToken(self):
        authHeader = base64.b64encode(f"{self.clientId}:{self.clientSecret}".encode()).decode()
        headers = {
            'Authorization': f"Basic {authHeader}",
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        data = {
            'grant_type': 'refresh_token',
            'refresh_token': self.refreshToken
        }
        response = requests.post(self.tokenUrl, headers=headers, data=data)
        if response.status_code == 200:
            tokens = response.json()
            self.accessToken = tokens['access_token']

        else:
            raise Exception(f"Failed to refresh access token: {response.text}")
        
    def authenticate(self):
        authorize_url = self.getAuthUrl()
        webbrowser.open(authorize_url)
        
        # After authorizing, you will be redirected to the redirect URI with a long URL
        # Example: https://your_redirect_uri/?code=AUTHORIZATION_CODE&other_param=value

        # Simulate user copying the redirect URL from browser
        redirect_url = input("Paste the full redirect URL you were redirected to: ")

        # Extract the authorization code from the redirect URL
        parsed_url = urllib.parse.urlparse(redirect_url)
        auth_code = urllib.parse.parse_qs(parsed_url.query).get('code')

        if not auth_code:
            raise Exception("No authorization code found in the URL.")
        else:
            # Since parse_qs returns a list for each key, we take the first element
            auth_code = auth_code[0]

        # Use the authorization code to get tokens
        self.getTokens(auth_code)

        self.saveTokenFile()
        
    def saveTokenFile(self):
        infoToSerialize = {
            'refresh_token': self.refreshToken,
        }
        
        serializedData = json.dumps(infoToSerialize)
        
        with open(self.tokenFilename, 'w', encoding='utf-8') as f:
            json.dump(serializedData, f, ensure_ascii=False, indent=4)
        
    def loadTokenFile(self):
        with open(self.tokenFilename, 'r') as f:
            serializedData = json.load(f)
            
        deserializedInfo = json.loads(serializedData)
        
        self.refreshToken = deserializedInfo['refresh_token']
        
    def getAccessToken(self):
        if self.accessToken == None:
            self.loadTokenFile()
            self.refreshAccessToken()
            
        return self.accessToken