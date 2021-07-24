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
    def __init__(self, system_name,name) -> None:
        super().__init__(system_name, name)
        self.load_secrets()
        self.create_market_connection()

    def load_secrets(self):
        try:
            with open("config/secrets/" + self.system_name + ".json") as secrets:
                raw_secrets = json.load(secrets)
                self.API_KEY = raw_secrets["API_KEY"]
                self.SECRET_KEY = raw_secrets["SECRET_KEY"]
        except FileNotFoundError:
            print("No Secrets Found")
            raise FileNotFoundError
        #print("API KEY:" + self.API_KEY)
        #print("SECRET KEY:" + self.SECRET_KEY)

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