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
import argparse

class AlwaysBuy(Algorithm):
    name = "always_buy"
    def __init__(self, system_name, ticker, test_mode=False) -> None:
        super().__init__(system_name, ticker, test_mode)
        self.ticker_name = ticker
        pass
    def setup_defaults(self):
        pass
    def setup_config(self):
        pass
    def iterate(self, stream, msg):
        raw_data = msg[0]  # For Reaons beyond me, this is an array of data.
        #print(raw_data)
        #data = {'topic': raw_data[:1], 'message': raw_data[1:]}
        #message = pd.read_json(data["message"])
        #print (raw_data)
        #data = {'topic': raw_data[:1], 'message':raw_data[1:]}
        #message = pd.read_json(data["message"])
        #decision = self.check(message)            
        #print(data["message"])##
        #time.sleep(1) # Let's not be too hasty
        message = {}
        now = datetime.now().time()
        print(self.name, " : ", now)
        message["weight"] = 0
        message["ticker_name"] = self.ticker_name
        message["trade_type"] = 0b1 << 3
        message["ticker_price"] = 0.0000050 # This should come from the Ticker Module!
        message["stop_price"] = 0.0000040 # This should come from the Ticker Module!
        message["target_price"] = 0.55 # This should come from the Ticker Module!
        print(message)
        self.downstream_controller.send_to("PROXY", message)

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
        if self.test_mode:
            print("TEST_MODE")
            while True:
                test_data = "TEST"
                print(test_data)
                self.downstream_controller.send_to("PROXY", test_data)
                time.sleep(1)
        ioloop.IOLoop.instance().start()
         



if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("market")
    parser.add_argument("ticker")
    parser.add_argument("--test", help="Runs the module in test mode", action="store_true")
    args = parser.parse_args()
    AB = AlwaysBuy(str(args.market), str(args.ticker), test_mode=args.test)
    AB.run()
