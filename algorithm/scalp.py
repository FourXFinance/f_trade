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
from zmq.eventloop import ioloop, zmqstream
from datetime import datetime
from enums import TradeType
from util import bcolors, TradeRequest


class Scalp(Algorithm):
    name = "scalp"
    def __init__(self, system_name, ticker) -> None:
        super().__init__(system_name, ticker)
        self.ticker_name = ticker
        self.setup_defaults()
        self.setup_config()
        pass
    
    def setup_defaults(self):
        self.previous_price = None
        self.window = None

    def setup_config(self):
        self.target_percent = self.config["configuration_options"]["target_growth"] or 1.03
        self.window = int(self.config["configuration_options"]["window"]) or 3
        self.count = 0
        self.fail_count = 0
    def iterate(self):
        # To Be Used for Callbacks! - Coming Soon!!!
        pass
    def clean(self):
        self.previous_count = self.config["configuration_options"]["target_growth"] or 1.03
        self.window = int(self.config["configuration_options"]["window"]) or 3
        self.count = 0
        self.fail_count = 0
    def check(self, data):
        raw_data = data.values.tolist()
        cur_time = None
        lowest_id = None
        highest_id = None
        # TODO: This is complicated and needs a lot of optiization. Time to go over some more advanced data structures.
        # Essentially, this takes a lot of time.. And might not be required. Ideally we should try build a stream of data
        
        raw_data = sorted(raw_data, key=lambda entry: entry[0]["id"]) # Ooh Baby it's lambda time.
        price = 0.00
        for trade in raw_data:
            buyer_maker_count = 0
            best_match_count = 0
            trade = trade[0]            
            #print(trade)
            if cur_time == None:
                cur_time = int(trade["time"])
            elif int(trade["time"]) >= cur_time:
                cur_time = int(trade["time"])
            else:
                pass
                #print("Time Inconsistency!")
                # TODO: Figure out what this means? Maybe we are getting a previous set.
            price+=float(trade["price"])
            buyer_maker_count += 1 if trade["isBuyerMaker"] else 0
            best_match_count += 1 if trade["isBuyerMaker"] else 0
        price = price/len(raw_data)
        lowest_id = raw_data[0][0]["id"]
        highest_id = raw_data[-1][0]["id"]
        print(bcolors.OKCYAN + "AVG Price\t" + str(price) + ": " , end="")
        if self.previous_price == None:
            print(bcolors.WARNING + "\u0398")
            self.previous_price = price
        elif self.previous_price < price:
            print(bcolors.OKGREEN + '\u2197')
            self.previous_price = price
            self.count+=1
        elif self.previous_price == price:
            print(bcolors.OKCYAN + '\u21dd')
            pass
        else:
            print(bcolors.FAIL + '\u2198')
            self.previous_price = None
            self.count = 0
            self.fail_count +=1
            #TODO: weight increase?
            next
        if self.count == self.window:
            #Make a Buy Request
            print(bcolors.OKGREEN + "(" + "\u0024" + ") Buying " + self.ticker_name)
            self.recent_trade_request =  TradeRequest()
            self.recent_trade_request.set_market(self.system_name)
            self.recent_trade_request.set_trade_type(TradeType.BUY_WITH_OCO)
            self.recent_trade_request.set_purchase_price(-1)
            self.recent_trade_request.set_sale_price(price * self.target_percent)
            return True
    def send_most_recent_trade_request(self):
        self.downstream_controller.send_to("PROXY", message.to_json(), topic=stream_name)
        pass
    def iterate(self, stream, msg):
        stream_name = self.upstream_socket_map[stream.socket]   
        #print(stream_name)             
        #print(stream)
        # Now we have the name of our stream!
        raw_data = msg[0].decode("utf-8")  # For Reaons beyond me, this is an array of data.
        #print(raw_data)
        print(stream_name)
        data = {'topic': raw_data[:2], 'message': raw_data[2:]}
        parsed_data = pd.read_json(data["message"])
        result = self.check(parsed_data)
        if result == True:
            self.send_trade_request({"Trade Data": {}})
        return;
        message = {}
        print(message)
        #TODO: Tickers have an N:1 input:ouput mapping. Let's change this to a N:N (Output has N streams on the same port, different topics though)
        self.downstream_controller.send_to("PROXY", message.to_json(), topic=stream_name)
    def run(self):
        ioloop.IOLoop.instance().start()
            



if __name__ == "__main__":
    S =  Scalp(str(argv[1]),str(argv[2]))
    S.run()
