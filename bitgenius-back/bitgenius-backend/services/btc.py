import os
import requests
from typing import Dict, List, Optional

class BTCClient:
    def __init__(self):
        self.base_url = "https://blockstream.info/api"
    
    def get_address_info(self, address: str) -> Dict:
        url = f"{self.base_url}/address/{address}"
        response = requests.get(url)
        
        if response.status_code != 200:
            raise Exception(f"Error fetching address info: {response.status_code} - {response.text}")
        
        return response.json()
    
    def get_address_transactions(self, address: str, limit: int = 10) -> List[Dict]:
        url = f"{self.base_url}/address/{address}/txs"
        response = requests.get(url)
        
        if response.status_code != 200:
            raise Exception(f"Error fetching address transactions: {response.status_code} - {response.text}")
        
        return response.json()[:limit]
    
    def get_transaction(self, tx_id: str) -> Dict:
        url = f"{self.base_url}/tx/{tx_id}"
        response = requests.get(url)
        
        if response.status_code != 200:
            raise Exception(f"Error fetching transaction: {response.status_code} - {response.text}")
        
        return response.json()
    
    def get_btc_price(self) -> float:
        url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd"
        response = requests.get(url)
        
        if response.status_code != 200:
            raise Exception(f"Error fetching BTC price: {response.status_code} - {response.text}")
        
        data = response.json()
        return data["bitcoin"]["usd"]

btc_client = BTCClient()
