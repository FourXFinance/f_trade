import sys
sys.path.insert(1, 'lib')
import pandas as pd
import numpy as np
from module import Node
from enums import AcceptableKlineValues, Sleep
import zmq
import json
from datetime import datetime
import time

from binance import Client, ThreadedWebsocketManager, AsyncClient
import asyncio
# This is a tick Node. You will run one of these for every time interval

class Worker(Node):
    def __init__(self, name, downstream_port, interval, tickers,id=None) -> None:
        self.interval = interval
        self.downstream_port = downstream_port
        self.tickers = tickers
        super().__init__(name)
        self.tracked_tickers = tickers
        self.setup()
    def setup(self):
        self.add_downstream("DATA", self.downstream_port, zmq.PUB, "0", bind=True, register=False)
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
        # TODO We have this data, what do we do with it
        return True

    async def get_data_for_ticker(self, ticker):
        if self.interval == 'RT':
            return await self.get_last_trades(ticker)
        else:
            return await self.get_kline_data_for_ticker(ticker)

    async def get_new_data(self):
        tickers = self.tracked_tickers
        
        # res = await asyncio.gather(self.get_market_data_for_ticker(ticker[0], ticker[1]) for ticker in tickers)
        await asyncio.gather(
                            self.get_data_for_ticker(self.tickers[0]),
                            self.get_data_for_ticker(self.tickers[1]),
                            self.get_data_for_ticker(self.tickers[2]),
                            self.get_data_for_ticker(self.tickers[3])
                            )
    async def run(self):
        await self.load_market_config()
        await self.connect_to_market()
        tick_count = 0
        while True:
            tick_count+=1
            now = datetime.now()
            try:
                await self.get_new_data()
            except Exception as e:
                print("Caught Exception: " + str(e))
            later = datetime.now()
            difference = (later - now).total_seconds()
            # print(str(tick_count) + " Took " + str(round(difference,3))  + " seconds")
            time.sleep(0.8)

if __name__ == "__main__":
    name = "market"
    downstream = int(sys.argv[1])
    interval = sys.argv[2]
    if interval not in [item.value for item in AcceptableKlineValues]:
        raise Exception("Error Unknown Time Interval: " + interval)
    tickers = sys.argv[3:]
    W = Worker("binance" + "." + name + "." + interval, downstream , interval, tickers)
    loop = asyncio.get_event_loop()
    loop.run_until_complete(W.run())



