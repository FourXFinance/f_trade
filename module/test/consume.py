import sys
sys.path.insert(1, 'lib')
from module import Node
import zmq
import time
import json

class Test(Node):
    def __init__(self, name, ticker) -> None:
        super().__init__(name)
        self.ticeker = ticker
        self.add_upstream("RT", 4000, zmq.SUB, "0", bind=False)
        self.add_upstream("1M", 4001, zmq.SUB, "0", bind=False)
        self.add_upstream("2M", 4002, zmq.SUB, "0", bind=False)
        self.add_upstream("3M", 4003, zmq.SUB, "0", bind=False)
    def run(self):
        while True:
            streams = self.consume_next()
            for stream in streams:
                print(stream.recv())
            time.sleep(1)
            pass

if __name__ == "__main__":
    name = "Test Node"
    ticker = sys.argv[1]
    T = Test(name,ticker)
    T.run()
    





