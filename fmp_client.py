import ssl
import certifi
import json
from urllib.request import urlopen 
import requests

class FMPAPIClient:
    """A class to interact with Financial Modeling Prep (FMP) API and fetch raw data."""

    def __init__(self, api_key):
        self.api_key = api_key

    def get_json_data(self, url):
        """Fetch and Parse JSON data from a URL"""
        try:
            context = ssl.create_default_context(cafile=certifi.where())
            response = urlopen(url, context=context)
            data = response.read().decode("utf-8")
            return json.loads(data)
        except Exception as e:
            print(f"Error fetching data from {url}: {e}")
            return None

    def fetch_stock_list(self):
        """Fetch the list of all stocks."""
        url = f"https://financialmodelingprep.com/api/v3/stock/list?apikey={self.api_key}"
        return self.get_json_data(url)

    def fetch_company_profile(self, symbol):
        """Fetch the company profile for a specific symbol."""
        url = f"https://financialmodelingprep.com/api/v3/profile/{symbol}?apikey={self.api_key}"
        return self.get_json_data(url)

