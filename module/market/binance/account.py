import sys
sys.path.insert(1, 'lib')
from module import Node
import zmq
import json
import time
from datetime import datetime
from binance import Client, ThreadedWebsocketManager, AsyncClient
import asyncio
import numpy as np
import pandas as pd



class Account(Node):
    def __init__(self,name, downstream_port,ticker) -> None:
        super().__init__(name)
        self.ticker = ticker
        self.add_downstream("DATA", downstream_port, zmq.PUB, bind=True, register=False)

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
        
    async def get_account_data(self):
        raw_data = await self.client.get_open_orders(symbol=self.ticker)
        recent_trades =  np.array(raw_data)
        df = pd.DataFrame(data=recent_trades)
        return df

    async def create_order(self, order):
        pass
    
    async def run(self):
        await self.load_market_config()
        await self.connect_to_market()
        tick_count = 0
        # Accounts should wait for an algorithm to be ready. Then it will fetch new account data.
        while True:
            # data_in = self.recv...
            tick_count+=1
            now = datetime.now()
            acc_data = None
            try:
               acc_data = await self.get_account_data()
               print(acc_data)
            except Exception as e:
                print("Caught Exception: " + str(e))
            later = datetime.now()
            difference = (later - now).total_seconds()
            # print(str(tick_count) + " Took " + str(round(difference,3))  + " seconds")
            time.sleep(1)
            
if __name__ == "__main__":
    name = "Account Data"
    downstream_port = int(sys.argv[1])
    ticker = sys.argv[2]
    A = Account(name, downstream_port, ticker)
    loop = asyncio.get_event_loop()
    loop.run_until_complete(A.run())
    


    



