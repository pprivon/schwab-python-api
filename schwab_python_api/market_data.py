import requests
from urllib import parse 

class MarketData:
    def __init__(self, authInstance):
        """
        Initialize the MarketData class with an authentication instance.
        
        Args:
            authInstance (SchwabAuth): An instance of the SchwabAuth class.
        """
        self.authInstance = authInstance
        self.baseUrl = "https://api.schwabapi.com/marketdata/v1"

    def getHeaders(self):
        """
        Get the authorization headers for API requests.
        
        Returns:
            dict: A dictionary containing the authorization header.
        """
        return {
            'Authorization': f"Bearer {self.authInstance.accessToken}"
        }

    def getQuotes(self, symbols):
        """
        Get current quote for the specified symbols.
        
        Args:
            symbols (list): A list of symbols to get quote for.
        
        Returns:
            dict: The JSON response containing the quote.
        """
        # Convert List to Comma Separated String
        symbol_str = ','.join(symbols)

        # Construct the URL and parameters
        url = f"{self.baseUrl}/quotes"
        params = {'symbols': symbol_str}

        # Make the GET request
        response = requests.get(url, headers=self.getHeaders(), params=params)
        
        return response.json()
    
    def getQuote(self, symbol):
        """
        Get current quote for a single specified symbol.
        
        Args:
            symbols (str): A single symbol to get quote for.
        
        Returns:
            dict: The JSON response containing the quote.
        """
        # Convert the symbol string to URL-encoded format, encoding all characters
        html_symbol = parse.quote(symbol, safe='')
        
        url = f"{self.baseUrl}/{html_symbol}/quotes"
        params = {}
        response = requests.get(url, headers=self.getHeaders(), params=params)
        if response.status_code == 200:
            return response.json()
        
        else:
            print(f"Schwab API getQuote Failure: Ticker: {symbol}: Response Status Code {response.status_code}: {response.reason}")
            return None

    def getOptionExpirations(self, symbol):
        """
        Get option expirations for the specified symbol.
        
        Args:
            symbol (str): The symbol to get option expirations for.
        
        Returns:
            dict: The JSON response containing the option expirations.
        """
        url = f"{self.baseUrl}/expirationchain"
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
        url = f"{self.baseUrl}/chains"
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
