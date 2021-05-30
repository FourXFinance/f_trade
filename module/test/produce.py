import sys
sys.path.insert(1, 'lib')
from module import Node
import zmq
import time
import json

class Test(Node):
    def __init__(self, name, ticker) -> None:
        super().__init__(name)
        self.ticker = ticker
        self.add_downstream("RT", 4000, zmq.PUB, "0", bind=True)
        self.add_downstream("1M", 4001, zmq.PUB, "0", bind=True)
        self.add_downstream("2M", 4002, zmq.PUB, "0", bind=True)
        self.add_downstream("3M", 4003, zmq.PUB, "0", bind=True)
    def run(self):
        while True:
            self.produce_for(message="RT", target_stream="RT")
            self.produce_for(message="1M DATA", target_stream="1M")
            self.produce_for(message="2M DATA", target_stream="2M")
            self.produce_for(message="3M DATA", target_stream="3M")
            time.sleep(1)
            pass

if __name__ == "__main__":
    name = "Test Node"
    ticker = sys.argv[1]
    T = Test(name,ticker)
    T.run()
    





