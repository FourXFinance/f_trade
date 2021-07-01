import sys
sys.path.insert(1, 'lib')
import pandas as pd
import numpy as np
from module import Node
from enums import AcceptableKlineValues
import zmq
import json
from datetime import datetime
import time

from binance import Client, ThreadedWebsocketManager, AsyncClient
import asyncio
# This is a tick Node. You will run one of these for every time interval

class Worker(Node):
    def __init__(self, name, interval, tickers,id=None) -> None:
        super().__init__(name)
        self.tracked_tickers = tickers
    # The Market config contains the API KEY and SECRET KEY for Binance    
    async def load_market_config(self):
        try:
            with open("config/secrets/binance.json") as user_credentials:
                raw_credentials = json.load(user_credentials)
                self.API_KEY = raw_credentials["API_KEY"]
                self.SECRET_KEY = raw_credentials["SECRET_KEY"]
        except FileNotFoundError:
            print("Error, config/secrets/binance.json file not found")
            raise FileNotFoundError
  
    async def connect_to_market(self, test_mode = False):
        self.client  = await AsyncClient.create(self.API_KEY, self.SECRET_KEY, testnet=test_mode)

    async def get_market_status(self):
        return await self.client.get_system_status()

    async def is_market_open(self):
        status = await self.get_market_status()
        return status["status"] == 0
        
    async def get_kline_data_for_ticker(self, ticker_name, ticker_topic):
            raw_data = await self.client.get_klines(symbol=self.ticker, interval=self.interval)
            recent_trades =  np.array(raw_data)
            df = pd.DataFrame(data=recent_trades)
            # TODO We have this data, what do we do with it        
    
    async def get_last_trades(self, ticker_name, limit=50):
        raw_data = await self.client.get_recent_trades(symbol=ticker_name, limit=limit)
        recent_trades =  np.array(raw_data)
        df = pd.DataFrame(data=recent_trades)
        # TODO We have this data, what do we do with it

    async def get_data_for_ticker(self, ticker):
        pass
    async def get_new_data(self):
        tickers = self.tracked_tickers
        
        # res = await asyncio.gather(self.get_market_data_for_ticker(ticker[0], ticker[1]) for ticker in tickers)
        await asyncio.gather(
                            self.get_data_for_ticker(self.tracked_tickers[0], 0),
                            self.get_data_for_ticker(self.tracked_tickers[1], 1),
                            self.get_data_for_ticker(self.tracked_tickers[2], 2),
                            self.get_data_for_ticker(self.tracked_tickers[3], 3)
                            )
    async def run(self):
        await self.load_market_config()
        await self.connect_to_market()
        tick_count = 0
        while True:
            tick_count+=1
            now = datetime.now()
            try:
                await self.get_market_data_for_tracked_tickers()
            except Exception as e:
                print("Caught Exception")
            later = datetime.now()
            difference = (later - now).total_seconds()
            # print(str(tick_count) + " Took " + str(round(difference,3))  + " seconds")
            time.sleep(0.8)

if __name__ == "__main__":
    name = "market"
    downstream = sys.argv[1]
    interval = sys.argv[2]
    if interval not in [item.value for item in AcceptableKlineValues]:
        raise Exception("Error Unknown Time Interval: " + interval)
    tickers = sys.argv[3:]
    W = Worker("binance" + "." + name + "." + interval, interval, tickers)
    loop = asyncio.get_event_loop()
    loop.run_until_complete(W.run())



