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

class PriceOf(BinanceNode):
    def __init__(self,system_name, target_tickers) -> None:
        self.target_tickers = target_tickers
        self.name = "Trader"
        super().__init__(system_name, self.name)

    def run(self):
        for ticker in self.target_tickers:
            avg_price = self.client.get_avg_price(symbol=ticker)
            if "".join(ticker[-4:]) == "USDT":
                print("\u0024" + str(round(float(avg_price["price"]),2)), end="")
            elif "".join(ticker[-3:]) == "EUR":
                print("\u20AC" + str(round(float(avg_price["price"]),2)), end="")
            if ticker != self.target_tickers[-1]:
                print(" ",end="")
            
if __name__ == "__main__":
    system_name =  sys.argv[1]
    target_tickers =  sys.argv[2:]
    # Append a UUID to name
    
    PO = PriceOf(system_name, target_tickers)
    PO.run()
    


    



