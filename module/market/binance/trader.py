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
    def __init__(self,name, downstream_port,ticker) -> None:
        super().__init__(name)
        self.ticker = ticker
        self.add_downstream("DATA", downstream_port, zmq.PUB, bind=True, register=False)
        
    def submit_order(self):
        pass

    def run(self):
        self.load_market_config()
        self.connect_to_market()
        tick_count = 0
        while True:
            # Get Request from Broker
            # Submit Trade to Binance API
            time.sleep(1)
            
if __name__ == "__main__":
    name = "BinanceTrader." + sys.argv[1]
    # Append a UUID to name
    upstream_port = int(sys.argv[2])
    
    BT = BinanceTrader(name, upstream_port)
    BT.run()
    


    



