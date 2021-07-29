from math import acos
import sys
sys.path.insert(1, 'lib')
from module import Node
sys.path.insert(1, 'module/market/binance')
from node import BinanceNode
import zmq
import json
import time
from datetime import datetime
from binance import Client, ThreadedWebsocketManager, AsyncClient
import asyncio
import numpy as np
import pandas as pd
import asyncio
from zmq.eventloop import ioloop, zmqstream
from binance.enums import *

class BinanceTrader(BinanceNode):
    def __init__(self,system_name) -> None:
        self.name = "Trader"
        super().__init__(system_name, self.name)
        self.setup()
    
    def setup(self):
        self.load_config()
        self.setup_upstream()
        self.setup_heartbeat()

    def load_config(self):
        try:
            with open("config/generated/" + self.system_name + "/trader/" + self.system_name + ".json") as config:
                raw_config = json.load(config)
                #print(raw_config)
                self.config = raw_config
        except FileNotFoundError:
            print("config/generated/" + self.system_name + "/trader/" + self.system_name + ".json")

            raise FileNotFoundError

    def setup_upstream(self):
        trader_proxy_port = self.config["trader_proxy_port"]
        self.upstream_controller.add_stream( 
                            "DATA",
                            trader_proxy_port,
                            zmq.SUB,
                            bind=False,
                            register=False
                        )

    def submit_order(self):
        pass

    def run(self):
        ioloop.IOLoop.instance().start()
        while True:
            try:
                raw_data = self.recv_from("DATA").decode('UTF-8')
                data = {'topic': raw_data[:1], 'message':raw_data[1:]}
                account_result = json.loads(data["message"])
                #print(account_result)
                if account_result["trade_type"] == 0b1 << 3:
                    now = datetime.now().time()
                    print(self.name, " : ", now)
                    # order = self.client.order_market_buy(
                    # symbol=account_result["symbol"],
                    # quantity=account_result["quantity"])
                    # Did You know you can track the status of your order?
                    # That's right. Every Order that is created gets an ID.

                    # This means we can do this

                    # OCO Order.

                    # while count < 5 or order_not_filled:
                    #     Check ir order is filled.
                    #    time.sleep(1)

                    # This is blocking. but will be solved in the websocket update
                    # order = self.client.create_oco_order(
                    # symbol= account_result["symbol"],
                    # side=SIDE_SELL,
                    # stopLimitTimeInForce=TIME_IN_FORCE_GTC,
                    # quantity=account_result["quantity"],
                    # stopPrice=account_result["stop_price"],
                    # price=account_result["target_price"])
            except Exception as e:
                pass
                print(e)
            #time.sleep(1)
            
if __name__ == "__main__":
    system_name =  sys.argv[1]
    # Append a UUID to name
    
    BT = BinanceTrader(system_name)
    BT.run()
    


    



