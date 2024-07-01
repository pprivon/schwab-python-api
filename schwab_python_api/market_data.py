import requests
from urllib import parse 
from datetime import datetime, timezone
import pandas as pd
import json


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
        endpoint = '/expirationchain'
        try:
            url = f"{self.baseUrl}{endpoint}"
            params = {'symbol': symbol}
            response = requests.get(url, headers=self.getHeaders(), params=params)

            if response is not None and response.status_code == 200:

                # Define headers for dataframe
                header = [
                    'ticker',
                    'timestamp',
                    'year',
                    'month',
                    'day',
                    'expiryType'
                ]

                # Create dataframe to store options chain information
                df_exp_date = pd.DataFrame(columns = header)

                parsed = json.loads(response.text)

                # Handle and parse response
                data = response.json()
                timestamp = datetime.now()
                if data is not None and 'expirationList' in data:
                    i = 0
                    for expirationDate in data['expirationList']:
                        date = datetime.strptime(expirationDate['expirationDate'], "%Y-%m-%d")
                        df_exp_date.loc[len(df_exp_date.index)] =[
                            symbol,
                            timestamp,
                            date.year,
                            date.month,
                            date.day,
                            expirationDate['expirationType']
                        ]
                        i = i + 1
                    return df_exp_date
                else:
                    print("No expiration dates available.")
                    df_exp_date = pd.DataFrame()  
                    return df_exp_date
            
            elif response is not None:
                print(f"Endpoint {endpoint} returned status {response.status_code}: {response.text}, {response.url}")
                df_exp_date = pd.DataFrame()  
                return df_exp_date
            
        except Exception as Error:
            print(f"Unable to obtain option chain expirations. Error: {Error}")    
            df_exp_date = pd.DataFrame()  
            return df_exp_date
            

    def getOptionChains(self, symbol, fromDate=None, toDate=None):
        """
        Get option chains for the specified symbol and expiration date.
        
        Args:
            symbol (str): The symbol to get option chains for.
            fromDate (str, optional): The starting date expiration date for the options.
            toDate (str, optional): The ending date expiration date for the options. If fromDate populated and toDate not populated, toDate defaulted to fromDate
        
        Returns:
            dict: The JSON response containing the option chains.
        """
        try:
            endpoint = '/chains'
            url = f"{self.baseUrl}{endpoint}"
            params = {'symbol': symbol}

            current_timestamp = int(datetime.now(timezone.utc).timestamp())
            if fromDate is not None:
                params['fromDate'] = fromDate
                if toDate is None:
                    params['toDate'] = fromDate
                else:
                    params['toDate'] = toDate

            response = requests.get(url, headers=self.getHeaders(), params=params)
            option_data_raw = response.json()

            if response is not None and response.status_code == 200:
                # Initialize an empty list to hold the processed option chain data
                option_data = []
                
                # Extract call and put maps
                call_map = option_data_raw.get('callExpDateMap', {})
                put_map = option_data_raw.get('putExpDateMap', {})
                
                
                # Iterate through each expiration date in the callExpDateMap
                for expiry in call_map:
                    expiry_date_str, dte = expiry.split(':')
                    expiry_date = datetime.strptime(expiry_date_str, '%Y-%m-%d')
                    
                    # Create a set of common strikes in both call and put maps for this expiry
                    call_strikes = set(call_map.get(expiry, {}).keys())
                    put_strikes = set(put_map.get(expiry, {}).keys())
                    common_strikes = sorted(call_strikes.intersection(put_strikes), key=float)
                    
                    # Iterate through each strike price within the expiration date
                    for strike_price in common_strikes:
                        call_option = call_map[expiry][strike_price][0]
                        put_option = put_map[expiry][strike_price][0]
                        # Add the parsed data to the list
                        option_data.append({
                            'timestamp': current_timestamp,
                            'call_timestamp': call_option.get('quoteTimeInLong'),
                            'call_symbol': call_option.get('symbol'),
                            'call_option_root': call_option.get('optionRoot'),
                            'call_option_type': call_option.get('putCall'),
                            'call_strike_price': call_option.get('strikePrice'),
                            'call_volume': call_option.get('totalVolume'),
                            'call_open_interest': call_option.get('openInterest'),
                            'call_last_price': call_option.get('last'),
                            'call_bid': call_option.get('bid'),
                            'call_ask': call_option.get('ask'),
                            'call_itm': max(call_option.get('intrinsicValue'),0),
                            'call_net_change': call_option.get('netChange'),
                            'call_delta': call_option.get('delta'),
                            'call_gamma': call_option.get('gamma'),
                            'call_theta': call_option.get('theta'),
                            'call_vega': call_option.get('vega'),
                            'call_rho': call_option.get('rho'),
                            'call_iv': call_option.get('volatility')/100,
                            'call_osi': call_option.get('symbol'),
                            'put_timestamp': put_option.get('quoteTimeInLong'),
                            'put_symbol': put_option.get('symbol'),
                            'put_option_root': put_option.get('optionRoot'),
                            'put_option_type': put_option.get('putCall'),
                            'put_strike_price': put_option.get('strikePrice'),
                            'put_volume': put_option.get('totalVolume'),
                            'put_open_interest': put_option.get('openInterest'),
                            'put_last_price': put_option.get('last'),
                            'put_bid': put_option.get('bid'),
                            'put_ask': put_option.get('ask'),
                            'put_itm': max(put_option.get('intrinsicValue'),0),
                            'put_net_change': put_option.get('netChange'),
                            'put_delta': put_option.get('delta'),
                            'put_gamma': put_option.get('gamma'),
                            'put_theta': put_option.get('theta'),
                            'put_vega': put_option.get('vega'),
                            'put_rho': put_option.get('rho'),
                            'put_iv': put_option.get('volatility')/100,
                            'put_osi': put_option.get('symbol'),
                            'expiration_year': expiry_date.year,
                            'expiration_month': expiry_date.month,
                            'expiration_day': expiry_date.day,
                            'expiration_date': expiry_date.strftime('%d-%b-%y'),
                        })
                # Convert the list to a DataFrame
                df_option_chain = pd.DataFrame(option_data)

            elif response is not None:
                print(f"Endpoint {endpoint} returned status {response.status_code}: {response.text}, {response.url} for symbol: {symbol} fromDate: {fromDate} toDate: {toDate}")
        except Exception as Error:
            print(f"Unable to obtain option chains. Error: {Error}")    
            df_option_chain = pd.DataFrame()   
            
        return df_option_chain

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
