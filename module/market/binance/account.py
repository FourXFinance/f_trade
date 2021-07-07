import sys
sys.path.insert(1, 'lib')
sys.path.insert(1, 'module/market/binance')
from module import Node
from node import BinanceNode
import zmq
import json
import time
from datetime import datetime
from binance import Client, ThreadedWebsocketManager
import numpy as np
import pandas as pd
import math


class Account(BinanceNode):
    ticker_config = {}
    open_trades = 0 # Cache Open Trades.
    max_open_trades = 10
    precision = 0
    lot_price_size = 25 # IN USDT
    def __init__(self,name, downstream_port,ticker) -> None:
        super().__init__(name)
        self.ticker = ticker
        self.add_downstream("DATA", downstream_port, zmq.PUB, bind=True, register=False)

    def get_open_orders(self):
        raw_data = self.client.get_open_orders(symbol=self.ticker)
        # Do Something with Account Data?
        return raw_data

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
        target_sale_price = round(order.target_sale_price, self.precision)
        # In Future, we should calculate a dynamic lot size
        # Send Order To Broker
        pass

    def run(self):
        # TODO: Get Clock Signal from Executive!
        # If the above functions pass, we are ready to start consuming information
        # Accounts should wait for an algorithm to be ready. Then it will fetch new account data.
        while True:
            # data_in = self.recv...
            try:
               # Check to see if we have too many open trades or not
                if self.open_trades >= self.max_open_trades:
                   orders = self.get_open_orders()
                   self.open_trades = len(orders)
                if self.open_trades >= self.max_open_trades:
                    # Sorry, nothing to do here! We have exausted the maximum number of open trades
                    # TODO: Log Abandoned Trade
                    continue
            except Exception as e:
                print("Caught Exception: " + str(e))
            time.sleep(1)
            
if __name__ == "__main__":
    downstream_port = int(sys.argv[1])
    ticker = sys.argv[2]
    name = "Account." + ticker
    A = Account(name, downstream_port, ticker)
    A.run()
    


    



