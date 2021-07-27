import sys
sys.path.insert(1, 'lib')
from controller import Controller
import zmq
import json
import signal
import uuid
from enums import AcceptableKlineValues
from zmq.eventloop import ioloop, zmqstream
from datetime import datetime
class Node:
    enabled = False
    def __init__(self, system_name, name, id=None):
        self.mode = 0 # TODO: Define the Modes (Ionian....)
        self.system_name = system_name
        self.context = zmq.Context()
        self.name = name
        self.upstream_controller = Controller()
        self.downstream_controller = Controller()
        self.executive_controller = Controller()
        self.logging_controller = Controller()
        self.heartbeat_controller = Controller()
        self.identifier = uuid.uuid4() # This 'might' be used for loggin purposes later on.        
        signal.signal(signal.SIGINT, self.shutdown)
        self.logging_controller.add_stream("LOG", 10000, zmq.PUB, topic="0", bind=False, register=False)

    
    def setup_heartbeat(self, override_port=None):
        port = None
        if override_port != None: #The Manager Node does not have a generated config. TODO: Create Config for Manager Node. Even if it is just it's heartbeat port
            port = override_port
        else:
            port = self.config["heartbeat_port"]
        self.heartbeat_controller.add_stream("HEARTBEAT", port, zmq.PAIR, topic="0", bind=True, register=False)
        socket = self.heartbeat_controller.get_stream_raw("HEARTBEAT")
        stream_sub = zmqstream.ZMQStream(socket)
        stream_sub.on_recv_stream(self.heartbeat)

    def heartbeat(self, stream , msg):
        """ Heartbeat What do we respond with when we get a liveliness check from the heartbeat controller"""
        message = msg[0].decode('UTF-8')
        now = datetime.now().time()
        if message == "PING":            
            self.heartbeat_controller.send_to("HEARTBEAT", {
                "name" : self.name,
                "response" : "",
                "ts" : str(now)
                }
            )
        else:
            pass #fucking panic. Nothing else should be on this heartbeat controller.
    
    def handle_executive(self, stream, msg):
        """handle_executive. How do we action and respond to messages from the executive controller"""
        message = msg[0].decode('UTF-8')
        if message == "START":
            ioloop.IOLoop.instance().start()
            self.heartbeat_controller.send_to("HEARTBEAT", {
                "name" : self.name,
                "response" : "starting",
                "ts" : str(now)
                }
            ) 
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
            self.logging_controller.send_to("LOG", str(self.identifier) + message) # Not Sure what else do to with logging. Add PORT!

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
        ioloop.IOLoop.instance().stop()
        sys.exit(0)

    
    def build_mappings(self):
        upstreams = self.upstream_controller.get_streams()
        downstreams = self.downstream_controller.get_streams()
        # TODO: Build Mappings for other controllers
        self.upstream_socket_map = {}
        self.downstream_name_map = {}
        for stream in upstreams.keys():
            self.upstream_socket_map[upstreams[stream].get_socket()] = upstreams[stream].name
        for stream in downstreams.keys():
            self.downstream_name_map[downstreams[stream].name] = downstreams[stream].get_socket()


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
                
                #print(self.config_raw)
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
