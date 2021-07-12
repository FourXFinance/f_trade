import sys
sys.path.insert(1, 'lib')
from controller import Controller
import zmq
import json
import signal
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
        #TODO: Add Heartbeat
        signal.signal(signal.SIGINT, self.shutdown)
        

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

    def send_to(self, stream_name, message):
        #TODO: Iterate through all controllers to find target stream
        return self.downstream_controller.send_to(stream_name, message)

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
        pass

class Algorithm(Node):
    def __init__(self, system_name, ticker):
        self.ticker = ticker
        super().__init__(system_name, self.name)
        # Algorithms should have HWM set to 1!
    def load_config(self):
        try:
            with open("config/generated/" + self.system_name + "/algorithm/" + self.ticker + "/" + self.name + ".json") as config:
                self.config_raw = json.load(config)
                self.configuration_options = self.config_raw["configuration_options"]
                print(self.configuration_options)
        except FileNotFoundError:
            print("Algorithm Config Is Missing!")
        pass
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
    def __init__(self, name, id):
        super().__init__(name, id=id)
    def run(self):
        return super().run()
