import sys
sys.path.insert(1, 'lib')
from module import Market
from enums import AcceptableKlineValues
import zmq
import json

class AlpacaMarket(Market):
    def __init__(self, name, interval, tickers,id=None) -> None:
        super().__init__()
        self.tracked_tickers = tickers
    def run(self):
        pass

if __name__ == "__main__":
    name = "Market"
    market = sys.argv[1]
    upstream = sys.argv[2]
    downstream = sys.argv[3]
    interval = sys.argv[4]
    if interval not in [item.value for item in AcceptableKlineValues]:
        raise Exception("Error Unknown Time Interval")
    tickers = sys.argv[3:]
    AM = AlpacaMarket(market + "." + name + "." + interval, tickers,id=-1)



