import sys  
sys.path.insert(1, 'lib')
from module import Node
from constants import DEFUALT_LOG_PROXY, DEFUALT_VIEW_ROOT
import zmq
import time
import json

class View(Node):
    def __init__(self, name,upstream_port, downstream_port) -> None:
        super().__init__(name)
        self.system_snapshot = {}
        self.add_upstream("VIEW", upstream_port, zmq.SUB, "0", bind=False, register=True)

        self.add_downstream("COMM", downstream_port + 0, zmq.SUB, "0", bind=False, register=True)
        self.add_downstream("DATA", downstream_port + 1, zmq.PUB, "0", bind=True)
    def run(self):
        while True:
            us_snapshot = self.upstream_controller.poll()
            # Build the system snapshot from the US data
            # Figure out what data is in the upstream
            us_snapshot = {"NODE_1" : {"UP": 3000, "DOWN": 4000}}
            for k in us_snapshot.keys():
                print(k)
            ds_snapshot = self.downstream_controller.poll()
            if ds_snapshot != {}:
                print ("We Got Data")
            time.sleep(1)


if __name__ == "__main__":
    name = "View"
    upstream_port = None
    downstream_port = None
    try:
        upstream_port = sys.argv[1]
    except IndexError as IE:
        print("Using Default Log Proxy: " + str(DEFUALT_LOG_PROXY))
        upstream_port = DEFUALT_LOG_PROXY
    try:
        downstream_port = sys.argv[2]
    except IndexError as IE:
        print("Using Default Downstream Port: " + str(DEFUALT_VIEW_ROOT))
        downstream_port = DEFUALT_VIEW_ROOT

    V = View(name,upstream_port, downstream_port)
    V.run()
    





