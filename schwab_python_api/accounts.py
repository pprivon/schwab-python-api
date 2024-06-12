import requests
from schwab_python_api.utilities import Utilities
import pandas as pd

class Accounts:
    def __init__(self, authInstance):
        """
        Initialize the Accounts class with an authentication instance.
        
        Args:
            authInstance (SchwabAuth): An instance of the SchwabAuth class.
        """
        self.authInstance = authInstance
        self.baseUrl = "https://api.schwabapi.com/trader/v1"
        
    def getHeaders(self):
        """
        Get the authorization headers for API requests.
        
        Returns:
            dict: A dictionary containing the authorization header.
        """
        return {
            'Authorization': f"Bearer {self.authInstance.accessToken}"
        }
        
    def getAccountNumbers(self):
        """
        Get list of account numbers and their encrypted values. 
        
        
        Returns:
            dict: The JSON response containing the account numbers and encrypted values.
        """
        url = f"{self.baseUrl}/accounts/accountNumbers"
        response = requests.get(url, headers=self.getHeaders())
        return response.json()
    
    def getAccounts(self, fields=None):
        """
        All the linked account information for the user logged in. The balances on these accounts are displayed by default however the positions on these accounts will be displayed based on the "positions" flag. 
        
        Args:
            fields (str, options): Allows one to determine which fields they want returned. Possible value in this String can be: positions
        
        Returns:
            dict: The JSON response containing the Account information.
        """
        url = f"{self.baseUrl}/accounts"
        if fields != None:
            params = {'fields': fields}
            response = requests.get(url, headers=self.getHeaders(), params=params)
        else:
            response = requests.get(url, headers=self.getHeaders())
        return response.json()
    
    def getSpecificAccounts(self, accountID, fields=None):
        """
        All the linked account information for the user logged in. The balances on these accounts are displayed by default however the positions on these accounts will be displayed based on the "positions" flag. 
        
        Args:
            accountID (str): Encrypted ID of the account
            fields (str, options): Allows one to determine which fields they want returned. Possible value in this String can be: positions
        
        Returns:
            dict: The JSON response containing the Account information.
        """
        url = f"{self.baseUrl}/accounts/{accountID}"
        if fields != None:
            params = {'fields': fields}
            response = requests.get(url, headers=self.getHeaders(), params=params)
        else:
            response = requests.get(url, headers=self.getHeaders())
        return response.json()
    
    def getFormattedPositions(self, accountID):
        # Get Unformatted Options Positions
        data = self.getSpecificAccounts(accountID=accountID,fields='positions')
        
        # Extract Options Contract Data and Add to Dataframe
        flattened_products = []
        if data is not None and 'securitiesAccount' in data and 'positions' in data['securitiesAccount']:
            for position in data['securitiesAccount']['positions']:
                product_dict = position['instrument']
                flattened_products.append({**product_dict, **position})

            df_products = pd.DataFrame(flattened_products)
        
        # Extract Expiration Date and Strike from Contract Data
        util = Utilities()
        df_positions_raw = util.extractOptionsContractSpecifications(df_products)
        
        # Format Positions Dataframe with Common Headings
        df_positions = self.formatPositionsDataFrame(df_positions_raw)
        return df_positions
    
    def formatPositionsDataFrame(self, df_positions_raw):
        
        df_positions_raw.rename(columns={
            'symbol': 'contractSpec', 
            'underlyingSymbol': 'symbol', 
            'putCall': 'callPut', 
            }, inplace=True)
        
        # Convert 'expiry' column to datetime format
        df_positions_raw['expiry'] = pd.to_datetime(df_positions_raw['expiry'], format='%d-%b-%y')

        # Extract year, month, and day components
        df_positions_raw['expiryYear'] = df_positions_raw['expiry'].dt.year
        df_positions_raw['expiryMonth'] = df_positions_raw['expiry'].dt.month
        df_positions_raw['expiryDay'] = df_positions_raw['expiry'].dt.day
        
        df_positions_raw['quantity'] = df_positions_raw['longQuantity'] - df_positions_raw['shortQuantity']

        # Format the 'expiry' column
        df_positions_raw['expiry'] = df_positions_raw['expiry'].dt.strftime('%d-%b-%y')
        
        # Replace 'symbol' values with 'contractSpec' values where 'assetType' is 'EQUITY'
        df_positions_raw.loc[df_positions_raw['assetType'] == 'EQUITY', 'symbol'] = df_positions_raw['contractSpec']
        
        return df_positions_raw
        
        
    