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

class BinanceTrader(BinanceNode):
    def __init__(self,system_name) -> None:
        self.name = "Trader"
        super().__init__(system_name, self.name)
        self.setup()
    
    def setup(self):
        self.load_config()
        self.setup_upstream()

    def load_config(self):
        try:
            with open("config/generated/" + self.system_name + "/trader/" + self.system_name + ".json") as config:
                raw_config = json.load(config)
                print(raw_config)
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
        while True:
            raw_data = self.recv_from("DATA").decode('UTF-8')
            data = {'topic': raw_data[:1], 'message':raw_data[1:]}
            message = pd.read_json(data["message"])
            print(message)
            time.sleep(1)
            
if __name__ == "__main__":
    system_name =  sys.argv[1]
    # Append a UUID to name
    
    BT = BinanceTrader(system_name)
    BT.run()
    


    



