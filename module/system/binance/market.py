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
    def __init__(self, system_name, market_name, interval) -> None:
        self.name = "Market"
        self.market_name = market_name
        self.system_name = system_name
        self.interval = interval
        self.tickers_with_topic = {}
        super().__init__(system_name, self.name)
        self.setup()
        self.load_secrets()
        
        

    def setup(self):
        self.load_config()
        self.setup_downstream()

    
    def load_config(self):
        try:
            with open("config/generated/" + self.system_name + "/market/" + self.market_name + ".json") as config:
                raw_credentials = json.load(config)
                print(raw_credentials)
                sources = raw_credentials["sources"]
                self.port = sources[self.interval]
                self.mappings = raw_credentials['tracked_tickers']
        except FileNotFoundError:
            print("config/generated/" + self.system_name + "/market/" + self.market_name + ".json")
            raise FileNotFoundError

    def setup_downstream(self):
        for mapping in self.mappings:
            self.tickers_with_topic.update(mapping)
        self.tickers = list(self.tickers_with_topic.keys())
        print(self.tickers)
        self.downstream_controller.add_stream( 
                            self.interval,
                            self.port,
                            zmq.PUB,
                            bind=True,
                            register=True
                        )
            
    async def create_market_connection(self, test_mode = False):
        self.client = await AsyncClient.create(self.API_KEY, self.SECRET_KEY, testnet=test_mode)

    async def get_kline_data_for_ticker(self, ticker_name):
        raw_data = None
        try:
            raw_data = await self.client.get_klines(symbol=ticker_name, interval=self.interval)
            # print(raw_data)
        except Exception as e:
            print(e)
        recent_trades =  np.array(raw_data)
        df = pd.DataFrame(data=recent_trades)
        #print(df.to_json())
        #print(ticker_name + "\t" + str(self.tickers_with_topic[ticker_name]))
        self.send_to(self.interval, df.to_json(), topic=self.tickers_with_topic[ticker_name])
    
    # TODO: This value 'limit' Should be dynamically calculated to avoid over/under fetching data
    async def get_last_trades(self, ticker_name, limit=50):
        raw_data = None
        try:
            raw_data = await self.client.get_recent_trades(symbol=ticker_name, limit=limit)
        except Exception as e:
            print(e)
        recent_trades = np.array(raw_data)
        df = pd.DataFrame(data=recent_trades)
        #print(df.to_json())
        #print(ticker_name + "\t" + str(self.tickers_with_topic[ticker_name]))
        self.send_to(self.interval, df.to_json(), topic=self.tickers_with_topic[ticker_name])
        self.send_to(self.interval, df.to_json(), topic=self.tickers_with_topic[ticker_name])
        
    async def get_data_for_ticker(self, ticker):
        
        if self.interval == 'RT':
            await self.get_last_trades(ticker)
        else:
            await self.get_kline_data_for_ticker(ticker)

    async def get_new_data(self):
      
        # res = await asyncio.gather(self.get_market_data_for_ticker(ticker[0], ticker[1]) for ticker in tickers)
        # TODO: This should accomodate as many tickers as supplied.
        #print("Test")
        await asyncio.gather(* [self.get_data_for_ticker(ticker) for ticker in self.tickers])
    async def run(self):
        tick_count = 0
        await self.create_market_connection()
        while True:
            # TODO: Make This an Event Loop!!!!
            await self.get_new_data()
            time.sleep(get_sleep_unit_for_interval(self.interval))

if __name__ == "__main__":
    interval = sys.argv[3]
    if interval not in [item.value for item in AcceptableKlineValues]:
        raise Exception("Error Unknown Time Interval: " + interval)
    tickers = sys.argv[4:]
    MW = MarketWorker(sys.argv[1], sys.argv[2], sys.argv[3])
    loop = asyncio.get_event_loop()
    loop.run_until_complete(MW.run())



