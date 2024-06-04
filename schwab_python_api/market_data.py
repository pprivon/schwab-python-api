import requests

class MarketData:
    def __init__(self, authInstance):
        self.authInstance = authInstance
        self.baseUrl = "https://api.schwabapi.com/v1/marketdata"

    def getHeaders(self):
        return {
            'Authorization': f"Bearer {self.authInstance.accessToken}"
        }

    def getPrices(self, symbols):
        url = f"{self.baseUrl}/quotes"
        params = {'symbols': ','.join(symbols)}
        response = requests.get(url, headers=self.getHeaders(), params=params)
        return response.json()

    def getOptionExpirations(self, symbol):
        url = f"{self.baseUrl}/options/expirations"
        params = {'symbol': symbol}
        response = requests.get(url, headers=self.getHeaders(), params=params)
        return response.json()

    def getOptionChains(self, symbol, expirationDate):
        url = f"{self.baseUrl}/options/chains"
        params = {
            'symbol': symbol,
            'expiration_date': expirationDate
        }
        response = requests.get(url, headers=self.getHeaders(), params=params)
        return response.json()
