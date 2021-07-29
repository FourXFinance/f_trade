from os import remove
from sys import path,argv
from pandas.core import algorithms
path.insert(1, 'lib')
from module import Algorithm
from binance import Client, ThreadedWebsocketManager
from binance.helpers import round_step_size
from enums import TradeType
import json
import zmq
import time
import numpy as np
import pandas as pd
import json
import sys
import csv
from zmq.eventloop import ioloop, zmqstream
from datetime import datetime
from util import bcolors

class AlwaysBuy(Algorithm):
    name = "always_buy"
    def __init__(self, system_name, ticker) -> None:
        super().__init__(system_name, ticker)
        self.ticker_name = ticker
        self.test_mode = False
        pass
    def setup_defaults(self):
        pass
    def setup_config(self):
        pass
    def iterate(self):
        # To Be Used for Callbacks! - Coming Soon!!!
        pass
    def clean(self):
        pass
    def check(self, data):
        # This Algorithm Always Submits a Request to Buy Whenever it gets data
        #print(bcolors.OKGREEN + "(" + "\u0024" + ") Buying " + self.ticker_name)
        message = {}
        message["result"] = "BUY"
        message["weight"] = 0
        message["ticker_name"] = self.ticker_name
        # df = pd.DataFrame(data=message)
        #print(message)
        self.downstream_controller.send_to("PROXY", json.dumps(message))
            
    def run(self):
        ioloop.IOLoop.instance().start()
        while True:
            if not self.test_mode:
                raw_data = self.recv_from("DATA").decode('UTF-8')
                #print (raw_data)
                #data = {'topic': raw_data[:1], 'message':raw_data[1:]}
                #message = pd.read_json(data["message"])
                #decision = self.check(message)            
                #print(data["message"])##
                #time.sleep(1) # Let's not be too hasty
                message = {}
                now = datetime.now().time()
                #print(self.name, " : ", now)
                message["weight"] = 0
                message["ticker_name"] = self.ticker_name
                message["trade_type"] = 0b1 << 3
                message["ticker_price"] = 0.0000050 # This should come from the Ticker Module!
                message["stop_price"] = 0.0000040 # This should come from the Ticker Module!
                message["target_price"] = 0.55 # This should come from the Ticker Module!
                #print(message)
                self.downstream_controller.send_to("PROXY", json.dumps(message))
            else:
                message = {}
                
                message["weight"] = 0
                message["ticker_name"] = self.ticker_name
                message["trade_type"] = 0b1 << 3
                message["ticker_price"] = 0.0000050 # This should come from the Ticker Module!
                message["stop_price"] = 0.0000040 # This should come from the Ticker Module!
                message["target_price"] = 0.55 # This should come from the Ticker Module!
                #print(message)
                self.downstream_controller.send_to("PROXY", json.dumps(message))
                #time.sleep(1)
            



if __name__ == "__main__":
    AB =  AlwaysBuy(str(argv[1]),str(argv[2]))
    AB.run()
