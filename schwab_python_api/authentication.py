import requests
import base64
from urllib.parse import urlencode

class SchwabAuth:
    def __init__(self, clientId, clientSecret, redirectUri):
        self.clientId = clientId
        self.clientSecret = clientSecret
        self.redirectUri = redirectUri
        self.tokenUrl = "https://api.schwabapi.com/v1/oauth/token"
        self.authUrl = "https://api.schwabapi.com/v1/oauth/authorize"
        self.accessToken = None
        self.refreshToken = None

    def getAuthUrl(self):
        params = {
            'client_id': self.clientId,
            'redirect_uri': self.redirectUri,
            'response_type': 'code'
        }
        return f"{self.authUrl}?{urlencode(params)}"

    def getTokens(self, authorizationCode):
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
            self.refreshToken = tokens['refresh_token']
        else:
            raise Exception(f"Failed to refresh access token: {response.text}")
