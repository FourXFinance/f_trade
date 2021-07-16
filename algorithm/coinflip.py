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
from random import randint
from datetime import datetime

class Coinflip(Algorithm):
    name = "coinflip"
    def __init__(self, system_name, ticker) -> None:
        super().__init__(system_name, ticker)
        self.head_weight = self.config_raw["head_weight"]
        self.tail_weight = self.config_raw["tail_weight"]
        self.period = self.config_raw["period"]
        # TODO: Throw error if head_weight + tail_weight != 100
    def iterate(self):
        # To Be Used for Callbacks! - Coming Soon!!!
        pass
    def run(self):
        while True:
            raw_data = self.recv_from("DATA").decode('UTF-8')
            data = {'topic': raw_data[:1], 'message':raw_data[1:]}
            message = pd.read_json(data["message"])
            p = randint()
            print(message)
            flip = randint(1,100)
            decision = "BUY"
            if flip > float(self.head_weight):
                decision = "SELL"
            
            time.sleep(int(self.period)) # Let's not be too hasty
            



if __name__ == "__main__":
    CF =  Coinflip(str(argv[1]),str(argv[2]))
    CF.run()
