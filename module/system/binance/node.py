import sys
sys.path.insert(1, 'lib')
from module import Node
import zmq
import json
import time
from datetime import datetime
from binance import Client, ThreadedWebsocketManager, AsyncClient

class BinanceNode(Node):
    market_name = "Binance"
    def __init__(self, name) -> None:
        super().__init__(name)
        self.setup()
    def setup(self):
        self.load_market_config()
        self.create_market_connection()
        self.is_market_open()
        self.load_market_config()
        
        
    def load_market_config(self): 
        try:
            with open("config/secrets/binance.json") as user_credentials:
                raw_credentials = json.load(user_credentials)
                self.API_KEY = raw_credentials["API_KEY"]
                self.SECRET_KEY = raw_credentials["SECRET_KEY"]
        except FileNotFoundError:
            print("Error, config/secrets/binance.json file not found")
            raise FileNotFoundError

    def create_market_connection(self, test_mode = False):
        self.client  = Client(self.API_KEY, self.SECRET_KEY, testnet=test_mode)

    def get_market_status(self):
        return self.client.get_system_status()

    def is_market_open(self):
        status = self.get_market_status()
        return status["status"] == 0

if __name__ == "__main__":
    raise Exception("Do Not Run Binance Node Directly")

#TODO: Binance Node for Common Binance operations