import sys
sys.path.insert(1, 'lib')
sys.path.insert(1, 'module/market/binance')
from node import BinanceNode
import pandas as pd
import numpy as np
from module import Node
from enums import AcceptableKlineValues, Sleep
from utils import get_sleep_unit_for_interval
import zmq
import json
from datetime import datetime
import time

from binance import Client, ThreadedWebsocketManager, AsyncClient
import asyncio
# This is a tick Node. You will run one of these for every time interval

class MarketWorker(BinanceNode):
    def __init__(self, system_name, market_name) -> None:
        self.name = "Market"
        self.market_name = market_name
        self.system_name = system_name
        super().__init__(system_name, self.name)
        self.setup()

    def setup(self):
        self.load_config()
        self.setup_downstream()

    def load_config(self):
        try:
            with open("config/generated/" + self.system_name + "/market/" + self.market_name + ".json") as config:
                raw_credentials = json.load(config)
                print(raw_credentials)
        except FileNotFoundError:
            print("config/generated/" + self.system_name + "/market/" + self.market_name + ".json")
            raise FileNotFoundError

    def setup_downstream(self):
        pass

    def create_market_connection(self, test_mode = False):
        self.client  = Client(self.API_KEY, self.SECRET_KEY, testnet=test_mode)

    async def get_kline_data_for_ticker(self, ticker_name):
        raw_data = None
        try:
            raw_data = await self.client.get_klines(symbol=ticker_name, interval=self.interval)
            print(raw_data)
        except Exception as e:
            print(e)
            return False
        recent_trades =  np.array(raw_data)
        df = pd.DataFrame(data=recent_trades)
        self.send_to("DATA", df.to_json())
        return True
    
    async def get_last_trades(self, ticker_name, limit=50):
        raw_data = None
        try:
            raw_data = await self.client.get_recent_trades(symbol=ticker_name, limit=limit)
        except Exception as e:
            return False
        recent_trades =  np.array(raw_data)
        df = pd.DataFrame(data=recent_trades)
        self.send_to("DATA", df.to_json())
        return True

    async def get_data_for_ticker(self, ticker):
        if self.interval == 'RT':
            return await self.get_last_trades(ticker)
        else:
            return await self.get_kline_data_for_ticker(ticker)

    async def get_new_data(self):
        tickers = self.tracked_tickers
        
        # res = await asyncio.gather(self.get_market_data_for_ticker(ticker[0], ticker[1]) for ticker in tickers)
        # TODO: This should accomodate as many tickers as supplied.
        await asyncio.gather(
                            self.get_data_for_ticker(self.tickers[0]),
                            self.get_data_for_ticker(self.tickers[1]),
                            self.get_data_for_ticker(self.tickers[2]),
                            self.get_data_for_ticker(self.tickers[3])
                            )
    async def run(self):
        tick_count = 0
        while True:
            time.sleep(1)

if __name__ == "__main__":
    # interval = sys.argv[2]
    # if interval not in [item.value for item in AcceptableKlineValues]:
    #     raise Exception("Error Unknown Time Interval: " + interval)
    # tickers = sys.argv[3:]
    MW = MarketWorker(sys.argv[1], sys.argv[2])
    loop = asyncio.get_event_loop()
    loop.run_until_complete(MW.run())



