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

class Scalp(Algorithm):
    name = "scalp"
    def __init__(self, system_name, ticker) -> None:
        super().__init__(system_name, ticker)
        self.setup()
        pass

    def iterate(self):
        # To Be Used for Callbacks! - Coming Soon!!!
        pass
    def run(self):
        while True:
            raw_data = self.recv_from("DATA").decode('UTF-8')
            #print (raw_data)
            #data = {'topic': raw_data[:1], 'message':raw_data[1:]} # TODO: This is handled badly
            #print(data["message"])##
            time.sleep(1) # Let's not be too hasty
            



if __name__ == "__main__":
    S =  Scalp(str(argv[1]),str(argv[2]))
    S.run()
