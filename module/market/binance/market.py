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
    def __init__(self, name, downstream_port, interval, tickers,id=None) -> None:
        self.interval = interval
        self.downstream_port = downstream_port
        self.tickers = tickers
        super().__init__(name)
        self.tracked_tickers = tickers
        self.add_downstream("DATA", self.downstream_port, zmq.PUB, "0", bind=True, register=False)     

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
            tick_count+=1
            now = datetime.now()
            try:
                await self.get_new_data()
            except Exception as e:
                print("Caught Exception: " + str(e))
            later = datetime.now()
            difference = (later - now).total_seconds()
            # print(str(tick_count) + " Took " + str(round(difference,3))  + " seconds")
            time.sleep(get_sleep_unit_for_interval(self.interval))

if __name__ == "__main__":
    name = "market"
    downstream = int(sys.argv[1])
    interval = sys.argv[2]
    if interval not in [item.value for item in AcceptableKlineValues]:
        raise Exception("Error Unknown Time Interval: " + interval)
    tickers = sys.argv[3:]
    MW = MarketWorker("binance" + "." + name + "." + interval, downstream , interval, tickers)
    loop = asyncio.get_event_loop()
    loop.run_until_complete(MW.run())



