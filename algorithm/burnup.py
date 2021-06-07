from os import remove
from sys import path,argv
from pandas.core import algorithms
path.insert(1, 'lib')
from module import Algorithm
from binance import Client, ThreadedWebsocketManager
from binance.helpers import round_step_size
import json
from utils import Trade, get_quantity_for_dollars, TradeType
import zmq
import time
import numpy as np
import pandas as pd
import json
import signal
import sys
import csv
from datetime import datetime

class Burnup():
    name = "Burnup"
    previous_average = 0
    burndown_count = 0
    lot_size = 25
    trades = []
    trades_in_flight = []
    sale_count = 0
    max_invested = 750 # Per Ticker
    max_in_flight = max_invested/lot_size
    start_up_time = datetime.now()
    rounding_value = 4
    cool_down_count = 0
    cool_down_max = 10
    tick_count = 0
    post_check_average = None
    sale_cool_down = 0
    cool_down_mode = False
    def __init__(self, ticker, topic, upstream_port, downstream_port, algorithm_config) -> None:
        super().__init__(self.name, ticker, topic, upstream_port, downstream_port, algorithm_config, nobind=True)
        signal.signal(signal.SIGINT, self.shutdown)
    def precheck(self, message):
        return True
    def check(self, message):
        list_of_trades = message.values.tolist()
        total = 0
        for entry in list_of_trades:
            total += float(entry[0]["price"])
        avg_price = round(total/len(list_of_trades),8) # TODO Get rounding value from ticker config
        print(  "" + self.ticker + "\t" + 
                datetime.now().strftime("%H:%M:%S") + 
                "\t AVG: " + str(avg_price) + 
                "\t SC: " + str(self.sale_count) + 
                "\t IFC: " +str(len(self.trades_in_flight)) + 
                "\t CD: " + str(self.cool_down_mode))
        for trade in self.trades_in_flight:
            if trade[1] < avg_price:
                # print("We would have Sold " + str(trade[0]) + " at " + str(trade[1]) + " and made " + str(round(trade[0]*trade[1],5)))
                self.sale_count+=1
                self.trades_in_flight.remove(trade)
        if self.sale_cool_down > 0:
            self.sale_cool_down -=1
            return False
        if self.cool_down_mode:
            return False
        if avg_price < self.previous_average:
            self.previous_average = None

        if self.previous_average == None:
            self.previous_average = avg_price
            self.burndown_count = 0

        if avg_price > self.previous_average:
            self.burndown_count+=1
            self.previous_average = avg_price

        if self.burndown_count >= self.window:
            if len(self.trades_in_flight) <= self.max_in_flight: #TODO: Make the validity requirement a function of time since last trade. 

                # We should reduce the allowed in flight if the 
                trade_amount = round(get_quantity_for_dollars(avg_price, self.lot_size),0)
                #print("We will buy " + str(trade_amount) + " at " + str(round(self.previous_average,self.rounding_value)) + " for a cost of " + "USDT " + str(round(trade_amount*self.previous_average,self.rounding_value)))
                #print("We will Sell " + str(trade_amount) + " at " + str(round(self.previous_average * (1 + self.percent_growth),self.rounding_value)) + " at a price of " + "USDT " + str(round(trade_amount*self.previous_average*(1 +self.percent_growth),self.rounding_value)))               
                self.trades_in_flight.append((trade_amount, round(self.previous_average * (1 + self.percent_growth),self.rounding_value)))
                #print("In Flight Trades: " + str(len(self.trades_in_flight)))
                #print("Sale Count " + str(self.sale_count)) 
                self.sale_cool_down = 15
            else:
                print("Max Trades in Flight!")
                return False
            
            buy_trade = Trade(TradeType.MARKET_BUY,trade_amount, self.ticker)
            sale_price = round(avg_price* (1 + self.percent_growth),self.rounding_value)
            sell_trade = Trade(TradeType.LIMIT_SELL,trade_amount, self.ticker, trade_price=sale_price)
            self.trades.append(buy_trade)
            self.trades.append(sell_trade)
            return True
        return False
    def postcheck(self, message):
        #TODO: This should use 1 minute Kline values from another market ticker Node
        list_of_trades = message.values.tolist()
        total = 0
        for entry in list_of_trades:
            total += float(entry[0]["price"])
        avg_price = round(total/len(list_of_trades),8) 
        if self.post_check_average == None:
            self.post_check_average = avg_price
            return True
        elif self.post_check_average > avg_price:
            # We are going down. Break
            self.cool_down_mode = True
            self.cool_down_count = 2
            return False
        else:
            self.cool_down_count-=1 # How Many cool down windows need to be fulfilled
            if (self.cool_down_count == 0):
                self.post_check_average = None
                self.cool_down_mode = False
            return True

        return True
    def shutdown(self, sig, frame):
        self.write_to_file()
        sys.exit(0)
        pass
    def write_to_file(self):
        filename = "Test_" + str(self.name) + "_" + self.ticker + "_"
        date_time = self.start_up_time.strftime("%m_%d_%Y, %H:%M:%S")
        end_time = datetime.now().strftime("%m_%d_%Y, %H:%M:%S")
        with open(filename + date_time + ".csv", 'w', newline='') as csvfile:
            fw = csv.writer(csvfile, delimiter=' ',
                            quotechar='|', quoting=csv.QUOTE_MINIMAL)
            fw.writerow([self.sale_count, str(len(self.trades_in_flight)), date_time, end_time])
    def setup(self):
        self.window = self.algorithm_config["window"]
        self.percent_growth = self.algorithm_config["percent_growth"]/100
    def reset(self):
        self.previous_average = 0
        self.burndown_count = 0
        self.trades = []
    def run(self):
        while True:
            self.tick_count+=1
            raw_data = self.consume().decode('UTF-8')
            #print (raw_data)
            
            data = {'topic': raw_data[:1], 'message':raw_data[1:]} # TODO: This is handled badly
            #print(data["message"])##
            
            message = pd.read_json(data["message"])
            self.pre_pass = self.precheck(message)
            self.check_pass = self.check(message) 
            self.post_pass = True
            if self.tick_count % 6 == 0: # Every 10 Seconds
                self.post_pass = self.postcheck(message)                 
            if self.pre_pass and self.check_pass and self.post_pass:
                for trade in self.trades:
                    trade_message = str(trade)
                    self.produce(trade_message)
                self.reset()
            time.sleep(1) # Let's not be too hasty
            



if __name__ == "__main__":
    BDT =  BurnupTest(argv[1], str(argv[2]), int(argv[3]), int(argv[4]), argv[5])
    BDT.setup()
    BDT.run()
