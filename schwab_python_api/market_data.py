import requests

class MarketData:
    def __init__(self, authInstance):
        """
        Initialize the MarketData class with an authentication instance.
        
        Args:
            authInstance (SchwabAuth): An instance of the SchwabAuth class.
        """
        self.authInstance = authInstance
        self.baseUrl = "https://api.schwabapi.com/v1/marketdata"

    def getHeaders(self):
        """
        Get the authorization headers for API requests.
        
        Returns:
            dict: A dictionary containing the authorization header.
        """
        return {
            'Authorization': f"Bearer {self.authInstance.accessToken}"
        }

    def getPrices(self, symbols):
        """
        Get current prices for the specified symbols.
        
        Args:
            symbols (list): A list of symbols to get prices for.
        
        Returns:
            dict: The JSON response containing the prices.
        """
        url = f"{self.baseUrl}/quotes"
        params = {'symbols': ','.join(symbols)}
        response = requests.get(url, headers=self.getHeaders(), params=params)
        return response.json()

    def getOptionExpirations(self, symbol):
        """
        Get option expirations for the specified symbol.
        
        Args:
            symbol (str): The symbol to get option expirations for.
        
        Returns:
            dict: The JSON response containing the option expirations.
        """
        url = f"{self.baseUrl}/options/expirations"
        params = {'symbol': symbol}
        response = requests.get(url, headers=self.getHeaders(), params=params)
        return response.json()

    def getOptionChains(self, symbol, expirationDate=None):
        """
        Get option chains for the specified symbol and expiration date.
        
        Args:
            symbol (str): The symbol to get option chains for.
            expirationDate (str, optional): The expiration date for the options.
        
        Returns:
            dict: The JSON response containing the option chains.
        """
        url = f"{self.baseUrl}/options/chains"
        params = {'symbol': symbol}
        if expirationDate:
            params['expiration_date'] = expirationDate
        
        response = requests.get(url, headers=self.getHeaders(), params=params)
        return response.json()

    def getPriceHistory(self, symbol, startDate=None, endDate=None, frequencyType=None, frequency=None, periodType=None, period=None):
        """
        Get price history for the specified symbol with optional parameters.
        
        Args:
            symbol (str): The symbol to get price history for.
            startDate (str, optional): The start date for the price history (YYYY-MM-DD).
            endDate (str, optional): The end date for the price history (YYYY-MM-DD).
            frequencyType (str, optional): The frequency type (minute, daily, weekly, monthly).
            frequency (int, optional): The frequency of data points.
            periodType (str, optional): The period type (day, month, year, ytd).
            period (int, optional): The period of data points.
        
        Returns:
            dict: The JSON response containing the price history.
        """
        url = f"{self.baseUrl}/pricehistory"
        params = {'symbol': symbol}
        
        if startDate:
            params['start_date'] = startDate
        if endDate:
            params['end_date'] = endDate
        if frequencyType:
            params['frequency_type'] = frequencyType
        if frequency:
            params['frequency'] = frequency
        if periodType:
            params['period_type'] = periodType
        if period:
            params['period'] = period
        
        response = requests.get(url, headers=self.getHeaders(), params=params)
        return response.json()
