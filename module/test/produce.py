import sys
sys.path.insert(1, 'lib')
from module import Node
import zmq
import time
import json

class TestProducer(Node):
    def __init__(self, name, ticker) -> None:
        super().__init__(name)
        self.ticker = ticker
        self.add_downstream("RT", 4001, zmq.PUB, "0", bind=True)
        self.downstream = self.downstream_controller.get_streams().get("RT").get_stream()
        self.downstream.hwm = 1        
        #self.add_downstream("1M", 4001, zmq.PUB, "0", bind=True)
        #self.add_downstream("2M", 4002, zmq.PUB, "0", bind=True)
        #self.add_downstream("3M", 4003, zmq.PUB, "0", bind=True)
        
    def run(self):
        tick = 0    
        while True:
            #message = self.produce_for(message="RT", target_stream="RT")
            self.downstream.send_string("%d %s" % (0 ,str(tick)))
            #message = self.downstream.recv()
            print(str(tick))
            tick+=1
            #self.produce_for(message="1M DATA", target_stream="1M")
            #self.produce_for(message="2M DATA", target_stream="2M")
            #self.produce_for(message="3M DATA", target_stream="3M")
            time.sleep(1)
            pass

if __name__ == "__main__":
    name = "Test Node"
    ticker = None
    try:
        ticker = sys.argv[1]
    except IndexError as IE:
        ticker = "TESTTEST"
    T = TestProducer(name,ticker)
    T.run()
    





