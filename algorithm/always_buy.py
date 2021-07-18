from os import remove
from sys import path,argv
from pandas.core import algorithms
path.insert(1, 'lib')
from module import Algorithm
from binance import Client, ThreadedWebsocketManager
from binance.helpers import round_step_size
import json
import zmq
import time
import numpy as np
import pandas as pd
import json
import signal
import sys
import csv
from datetime import datetime
from util import bcolors

class AlwaysBuy(Algorithm):
    name = "always_buy"
    def __init__(self, system_name, ticker) -> None:
        super().__init__(system_name, ticker)
        self.ticker_name = ticker
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
        print(bcolors.OKGREEN + "(" + "\u0024" + ") Buying " + self.ticker_name)
        message = {}
        message["result"] = "BUY"
        message["weight"] = 0
        message["ticker_name"] = self.ticker_name
        # df = pd.DataFrame(data=message)
        print(message)
        self.downstream_controller.send_to("PROXY", json.dumps(message))
            
        

    def run(self):
        while True:
            raw_data = self.recv_from("DATA").decode('UTF-8')
            #print (raw_data)
            data = {'topic': raw_data[:1], 'message':raw_data[1:]}
            message = pd.read_json(data["message"])
            decision = self.check(message)            
            #print(data["message"])##
            time.sleep(1) # Let's not be too hasty
            



if __name__ == "__main__":
    AB =  AlwaysBuy(str(argv[1]),str(argv[2]))
    AB.run()
