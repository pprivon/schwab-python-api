import requests
import schwab_python_api.utilities as Utilities
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
        df_positions = util.extract_options_data(df_products)
        
        return df_positions
        
    