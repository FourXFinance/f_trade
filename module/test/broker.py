import sys
sys.path.insert(1, 'lib')
from module import Node
import zmq
import time
import json

class TestBroker(Node):
    def __init__(self, name, ticker) -> None:
        super().__init__(name)
        self.ticeker = ticker
        self.add_upstream("UP", 4000, zmq.XREQ, "0", bind=True)
        self.add_downstream("DOWN", 4001, zmq.XPUB, "0", bind=True)
        self.poller = zmq.Poller()
        self.upstream = self.upstream_controller.get_streams()["UP"].get_stream()
        self.downstream = self.downstream_controller.get_streams()["DOWN"].get_stream()

    def run(self):
        zmq.proxy(self.upstream, self.downstream)


if __name__ == "__main__":
    name = "Test Node"
    ticker = None
    try:
        ticker = sys.argv[1]
    except IndexError as IE:
        ticker = "TESTTEST"
    T = TestBroker(name,ticker)
    T.run()
    





