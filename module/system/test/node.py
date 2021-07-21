import sys
sys.path.insert(1, 'lib')
from module import Node
import zmq
import json
import time
from datetime import datetime
from binance import Client, ThreadedWebsocketManager, AsyncClient

class TestNode(Node):
    market_name = "Test"
    def __init__(self, system_name,name) -> None:
        super().__init__(system_name, name)
        self.load_secrets()
        self.create_market_connection()

    def load_secrets(self):
        self.API_KEY = "TEST_KEY"
        self.SECRET_KEY = "TEST_KEY"

    def create_market_connection(self, test_mode = False):
        self.client = None

    def get_market_status(self):
        return True

    def is_market_open(self):
        status = self.get_market_status()
        return True

if __name__ == "__main__":
    raise Exception("Do Not Run Test Node Directly")

#TODO: Binance Node for Common Binance operations