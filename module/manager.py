from lib.controller import Controller
import sys
sys.path.insert(1, 'lib')
from module import Node
import zmq
import json
import time
from enums import AcceptableKlineValues, Sleep

class Manager(Node):
    def __init__(self,name, upstream_port, ticker_port_pairs) -> None:
        super().__init__(name)
        #TODO: Load Upstream From Config
        #TODO: Load Ticker Starting Ports from Generated Config
        self.ticker_controllers = {}
        for ticker in ticker_port_pairs.keys():
            self.ticker_controllers[ticker] = Controller()
            for time_interval in ticker_port_pairs[ticker]:
                #TODO: Get Interval Offset Bump
                self.ticker_controllers[ticker].add_stream(time_interval, 4000, zmq.PUB, bind=True, register=False)

    def run(self):
        while True:
            time.sleep(1)
            
if __name__ == "__main__":
    name = "Manager"
    ticker_port_map = {}
    cur_ticker = None
    cur_rates = []
    # Nice Fancy way to read in command line arugments and build defualts
    for arg in sys.argv[1:]:
        if arg not in [item.value for item in AcceptableKlineValues]:
            # Arg Must be a ticker
            if cur_ticker != None:
                # We have a ticker and arg combination
                if cur_rates == []: 
                    # We have a ticker with no Times specified. Use Defaults
                    cur_rates = ["1m", "3m", "5m"] # Defaults. #TODO: Specify in config
                ticker_port_map[cur_ticker] = cur_rates
                cur_ticker = arg
                cur_rates = []
            else:
                cur_ticker = arg
        else:
            # Arg Must be a Rate
            cur_rates.append(arg)
    else:
        if cur_ticker != None:
            if cur_rates == []:
                # We have a ticker with no Times specified. Use Defaults
                cur_rates = ["1m", "3m", "5m"] # Defaults. #TODO: Specify in config
            ticker_port_map[cur_ticker] = cur_rates
        

print(ticker_port_map)
    #M = Manager(name, ticker_port_map)
    #M.run()


    



