import sys
sys.path.insert(1, 'lib')
from module import Node
import zmq
import json
import time

class TestManager(Node):
    def __init__(self,name, upstream_port, ticker_port_pairs) -> None:
        super().__init__(name)
        self.add_upstream(self.name + "." + "up.proxy", upstream_port, zmq.SUB, bind=False)
        for tpp in ticker_port_pairs:
            self.add_downstream(self.name + "." + "down." + tpp[0], tpp[1], zmq.PUB, bind=True)

    def run(self):
        while True:
            time.sleep(1)
            
if __name__ == "__main__":
    name = "Test Manager"
    upstream_port = int(sys.argv[1])
    downstreams = sys.argv[2:]
    ticker_port = []
    if len(downstreams)%2 != 0:
        raise Exception("Odd number of ticker port pairs given")
    for i in range(0,len(downstreams),2):
        ticker = downstreams[i]
        port = downstreams[i+1]
        ticker_port.append((ticker, int(port)))
    TM = TestManager(name, upstream_port,ticker_port)
    TM.run()


    



