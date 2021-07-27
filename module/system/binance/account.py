from os import name
import sys
sys.path.insert(1, 'lib')
sys.path.insert(1, 'module/market/binance')
from enums import TradeType
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
from binance.enums import *

class Account(BinanceNode):
    ticker_config = {}
    open_trades = 0 # Cache Open Trades.
    max_open_trades = 10
    precision = 0
    lot_price_size = 25 # IN USDT
    def __init__(self,system_name, ticker_name,) -> None:
        self.name = "Account"
        self.ticker_name = ticker_name
        self.lot_size = 25 #Euros
        super().__init__(system_name, self.name)
        self.setup()

    def setup(self):
        self.load_config()
        self.setup_upstream()
        self.setup_downstream()
        self.get_ticker_config_from_market()

    def load_config(self):
        try:
            with open("config/generated/" + self.system_name + "/account/" + self.ticker_name + ".json") as config:
                raw_credentials = json.load(config)
                print(raw_credentials)
                self.config = raw_credentials
        except FileNotFoundError:
            print("config/generated/" + self.system_name + "/account/" + self.market_name + ".json")
            raise FileNotFoundError

    def setup_upstream(self):
        account_proxy_port = self.config["account_proxy_port"]
        self.upstream_controller.add_stream( 
                            "DATA",
                            account_proxy_port,
                            zmq.SUB,
                            bind=False,
                            register=False
                        )
    def setup_downstream(self):
        broker_proxy_port = self.config["broker_proxy_port"]
        self.downstream_controller.add_stream( 
                            "PROXY",
                            broker_proxy_port,
                            zmq.PUB,
                            bind=False,
                            register=False
                        )

    def get_open_orders(self):
        raw_data = self.client.get_open_orders(symbol=self.ticker_name)
        # Do Something with Account Data?
        return raw_data
    def shutdown(self):
        pass

    def hard_shutdown(self):
        # Close all Open Orders
        # Move all assets to ETH
        # Withdraw ETH to Wallet.
        # The 'binance got raided' solution. Triggered by email.
        pass
    def get_ticker_config_from_market(self):
        raw_data = self.client.get_symbol_info(symbol=self.ticker_name)
        #print(self.ticker_name)
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


    def run(self):
        # TODO: Get Clock Signal from Executive!
        # If the above functions pass, we are ready to start consuming information
        # Accounts should wait for an algorithm to be ready. Then it will fetch new account data.
        while True:
            raw_data = self.upstream_controller.recv_from("DATA").decode('UTF-8')
            data = {'topic': raw_data[:1], 'message':raw_data[1:]}
            algorithm_result = json.loads(data["message"])
            if algorithm_result["trade_type"] == 0b1 << 3:
                now = datetime.now().time()
                print(self.name, " : ", now)
                # Buy With Sell
                message = {}
                message["symbol"] = self.ticker_name
                price = algorithm_result["ticker_price"] # 0.25
                quantity = round(self.lot_size / price, self.precision)
                message["quantity"] =  quantity
                message["target_price"] = algorithm_result["target_price"]
                message["stop_price"] = algorithm_result["stop_price"]
                message["trade_type"] = algorithm_result["trade_type"]
                #print(message)
                self.downstream_controller.send_to("PROXY", json.dumps(message));
            # Check to see if we have too many open trades or not
            if self.open_trades >= self.max_open_trades:
                orders = self.get_open_orders()
                self.open_trades = len(orders)
            if self.open_trades >= self.max_open_trades:
                # Sorry, nothing to do here! We have exausted the maximum number of open trades
                # TODO: Log Abandoned Trade
                continue
            else:
                # We're In Business
                self.downstream_controller.send_to("PROXY", json.dumps(data["message"]));
                    
            time.sleep(1)
            
if __name__ == "__main__":
    A = Account(sys.argv[1], sys.argv[2])
    A.run()
    


    



