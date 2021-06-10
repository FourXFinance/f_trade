import sys  
sys.path.insert(1, 'lib')
from module import Node
import zmq
import time
import json

class TestConsumer(Node):
    def __init__(self, name, ticker) -> None:
        super().__init__(name)
        self.ticker = ticker
        self.add_upstream("RT", 4001, zmq.REQ, "0", bind=False)
        self.upstream = self.upstream_controller.get_stream("RT")
        #self.add_upstream("1M", 4001, zmq.SUB, "0", bind=False)
        #self.add_upstream("2M", 4002, zmq.SUB, "0", bind=False)
        #self.add_upstream("3M", 4003, zmq.SUB, "0", bind=False)
    def run(self):
        while True:
            message = self.recv()
            print(message)
            #message = self.upstream.send(b"World")
            time.sleep(5)

if __name__ == "__main__":
    name = "Test Node"
    ticker = None
    try:
        ticker = sys.argv[1]
    except IndexError as IE:
        ticker = "TESTTEST"
    T = TestConsumer(name,ticker)
    T.run()
    





