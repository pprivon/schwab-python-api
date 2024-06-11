import pandas as pd 

class Utilities:
    def extract_options_data(df, contractSpecificationColumn='symbol'):
        # Regular expression to extract the relevant parts
        regex = r'(\d{6})([CPS])(\d{8})'

        # Extracting using vectorized string operations
        matches = df[contractSpecificationColumn].str.extract(regex)

        # Converting and formatting the expiration date
        df['expiry'] = pd.to_datetime(matches[0], format='%y%m%d').dt.strftime('%d-%b-%y')

        # Formatting the strike price
        df['strike'] = matches[2].astype(float) / 1000

        return df