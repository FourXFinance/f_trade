import sys
sys.path.insert(1, 'lib')
from module import Node
import zmq
import json
import time
class Ticker(Node):
    def __init__(self, ticker, upstream_root, downstream_root, enabled_clocks) -> None:
        super().__init__("Ticker." + ticker)
        self.ticker =  ticker
        self.upstream_root = upstream_root
        self.downstream_root = downstream_root
        self.enabled_clocks = enabled_clocks
        self.setup()
    def setup(self):
        # Add Downstreams
        self.add_downstream("DATA", self.downstream_root, zmq.PUB, "0", bind=True, register=False)
        # Add Upstreams ( Upstreams are on a poller)
        for i in range(0, len(self.enabled_clocks),1):
            ec  = self.enabled_clocks[i]
            self.add_upstream(ec, self.upstream_root + i + 1, zmq.SUB, "0", bind=False, register=True)
    def run(self):
        while True:
            us_snapshot = self.upstream_controller.poll()
            # Process Upstream Connections
            print (us_snapshot)
            ds_snapshot = self.downstream_controller.poll()
            # Process Downstream. Why would you poll a downstream? - Sub
            print (ds_snapshot)

            time.sleep(0.5)

if __name__ == "__main__":
    ticker, upstream_root, downstream_root = None, None, None
    try:
        ticker = sys.argv[1]
    except IndexError as IE:
        print("No Ticker Provided")
        sys.exit(-1)
    
    try:        
        upstream_root = int(sys.argv[2])
    except IndexError as IE:
        print("No Upstream Root Provided")
        sys.exit(-1)
    except ValueError as VE:
        print("Upstream Root is not a number")
        sys.exit(-1)

    try:        
        downstream_root = int(sys.argv[3])
    except IndexError as IE:
        print("No Downstream Root Provided")
        sys.exit(-1)
    except ValueError as VE:
        print("Downstream Root is not a number")
        sys.exit(-1)

    enabled_clocks = sys.argv[4:]
    if enabled_clocks == []:
        enabled_clocks= ["RT", "1M", "5M"]
        print("No Clocks provided. Using: " + ", ".join(enabled_clocks))

    T = Ticker(ticker, upstream_root, downstream_root, enabled_clocks)
    T.run()





