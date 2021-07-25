import sys
sys.path.insert(1, 'lib')
from controller import Controller
import zmq
import json
import signal
import uuid
from enums import AcceptableKlineValues

class Node:
    enabled = False
    def __init__(self, system_name, name, id=None):
        self.system_name = system_name
        self.context = zmq.Context()
        self.name = name
        self.upstream_controller = Controller()
        self.downstream_controller = Controller()
        self.executive_controller = Controller()
        self.logging_controller = Controller()
        self.heartbeat_controller = Controller()
        self.identifier = uuid.uuid4() # This 'might' be used for loggin purposes later on.
        #TODO: Add Heartbeat
        signal.signal(signal.SIGINT, self.shutdown)
        self.logging_controller.add_stream("LOG", 10000, zmq.PUB, topic="0", bind=False, register=False)

    def add_upstream(self, name, port, type, topic="0", bind=False, register=False):
        self.upstream_controller.add_stream(name, port, type, topic, bind, register)
        
    def add_downstream(self, name, port, type, topic="0", bind=False, register=False):
        self.downstream_controller.add_stream(name, port, type, topic, bind, register)

    def enable(self):
        self.enabled = True

    def disable(self):
        self.enabled = False

    def recv(self):
        return self.upstream_controller.recv()

    def recv_from(self,stream_name):
        return self.upstream_controller.recv_from(stream_name)

    def send_to(self, stream_name, message, topic="0"):
        #TODO: Iterate through all controllers to find target stream
        
        result = self.downstream_controller.send_to(stream_name, message, topic)
        if result:
            self.logging_controller.send_to("LOG: " + stream_name + "", str(self.identifier) + message) # Not Sure what else do to with logging. Add PORT!

    def consume_next(self):
        return self.upstream_controller.consume_next()

    def consume_from(self, target_stream=None):
        return self.upstream_controller.consume_from(target_stream)

    def produce_for(self, message, target_stream=None):
        return self.downstream_controller.produce_for(message,target_stream)

    def run(self):
        raise Exception("Override Me!")

    def shutdown(self, sig, frame):
        print("Safe Shutdown Process")
        sys.exit(0)

    def heartbeat(self):
        # TODO: Handle Heartbeat with Callbacks! - Coming Soon!!!
        return "Beep!"

class Algorithm(Node):
    def __init__(self, system_name, ticker):
        self.ticker = ticker
        super().__init__(system_name, self.name)
        self.setup()
        # Algorithms should have HWM set to 1!
    def load_config(self):
        try:
            with open("config/generated/" + self.system_name + "/algorithm/" + self.ticker + "/" + self.name + ".json") as config:
                self.config_raw = json.load(config)
                
                print(self.config_raw)
        except FileNotFoundError:
            print("Algorithm Config Is Missing!")

    def setup(self):
        self.load_config()
        self.configure()

    def configure(self):
        self.upstream_controller.add_stream("DATA", 
            self.config_raw["algorithm_port"], 
            zmq.SUB)

        self.downstream_controller.add_stream("PROXY", 
            self.config_raw["proxy_port"], 
            zmq.PUB)
        
    def run():
        raise Exception("Override Me!")

    def precheck():
        raise Exception("Override Me!")

    def check():
        raise Exception("Override Me!")

    def reset():
        raise Exception("Override Me!")


class Proxy(Node):
    #TODO: Proxies should be more generic
    def __init__(self, system_name, ticker_name):
        self.name = "PROXY"
        self.ticker_name = ticker_name
        super().__init__(system_name,self.name)
        self.setup()

    def setup(self):
        self.load_config()
        self.setup_upstream()
        self.setup_downstream()

    def load_config(self):
        try:
            with open("config/generated/" + self.system_name + "/proxy/" + self.ticker_name + ".json") as config:
                raw_credentials = json.load(config)
                print(raw_credentials)
                self.config = raw_credentials
        except FileNotFoundError:
            print("config/generated/" + self.system_name + "/proxy/" + self.market_name + ".json")
            raise FileNotFoundError

    def setup_upstream(self):
        algorithm_proxy_port = self.config["algorithm_proxy_port"]
        self.upstream_controller.add_stream( 
                            "UP",
                            algorithm_proxy_port,
                            zmq.XSUB,
                            bind=True,
                            register=False
                        )
        

    def setup_downstream(self):
        account_proxy_port = self.config["account_proxy_port"]
        self.downstream_controller.add_stream( 
                            "DOWN",
                            account_proxy_port,
                            zmq.XPUB,
                            bind=True,
                            register=False
                        )
    def run(self):
        zmq.proxy(self.upstream_controller.get_stream("UP").get_socket(), self.downstream_controller.get_stream("DOWN").get_socket())
