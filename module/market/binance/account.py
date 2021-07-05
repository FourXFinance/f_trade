import sys
sys.path.insert(1, 'lib')
from module import Node
import zmq
import json
import time
from datetime import datetime
from binance import Client, ThreadedWebsocketManager
import numpy as np
import pandas as pd
import math


class Account(Node):
    ticker_config = {}
    open_trades = 0 # Cache Open Trades.
    max_open_trades = 10
    precision = 0
    def __init__(self,name, downstream_port,ticker) -> None:
        super().__init__(name)
        self.ticker = ticker
        self.add_downstream("DATA", downstream_port, zmq.PUB, bind=True, register=False)

    def load_market_config(self): 
        try:
            with open("config/secrets/binance.json") as user_credentials:
                raw_credentials = json.load(user_credentials)
                self.API_KEY = raw_credentials["API_KEY"]
                self.SECRET_KEY = raw_credentials["SECRET_KEY"]
        except FileNotFoundError:
            print("Error, config/secrets/binance.json file not found")
            raise FileNotFoundError

    def connect_to_market(self, test_mode = False):
        self.client  = Client(self.API_KEY, self.SECRET_KEY, testnet=test_mode)

    def get_market_status(self):
        return self.client.get_system_status()

    def is_market_open(self):
        status = self.get_market_status()
        return status["status"] == 0
        
    def get_account_data(self):
        raw_data = self.client.get_open_orders(symbol=self.ticker)
        recent_trades =  np.array(raw_data)
        df = pd.DataFrame(data=recent_trades)
        return df

    def get_ticker_config_from_market(self):
        raw_data = self.client.get_symbol_info(symbol=self.ticker)
        filters = raw_data["filters"]
        
        for f in filters:
            print(f)
            if f["filterType"] == "PRICE_FILTER":
                self.tick_size = float(f["tickSize"])
                ts = self.tick_size
                ts = 1/ts
                self.precision = int(math.log10(ts)) # Use this for rounding!
            if f["filterType"] == "LOT_SIZE":
                self.min_qty = float(f["minQty"]) # Minimum number of units we can purchase
            
        pass

    def create_order(self, order):
        #TODO: Build a valid order by taking in the algorithm's result and 'shaping'
        # it to be Binance compatible
        pass

    def run(self):
        self.load_market_config()
        self.connect_to_market()
        self.get_ticker_config_from_market()
        # TODO: Get Clock Signal from Executive!
        # If the above functions pass, we are ready to start consuming information
        tick_count = 0
        # Accounts should wait for an algorithm to be ready. Then it will fetch new account data.
        while True:
            # data_in = self.recv...
            try:
               # Check to see if we have too many open trades or not
                if self.open_trades >= self.max_open_trades:
                   orders = self.client.get_open_orders(symbol=self.ticker)
                   self.open_trades = len(orders)
                if self.open_trades >= self.max_open_trades:
                    # Sorry, nothing to do here! We have exausted the maximum number of open trades
                    continue
            except Exception as e:
                print("Caught Exception: " + str(e))
            
if __name__ == "__main__":
    name = "Account"
    downstream_port = int(sys.argv[1])
    ticker = sys.argv[2]
    A = Account(name, downstream_port, ticker)
    A.run()
    


    



