import sys
sys.path.insert(1, 'lib')
from controller import Controller
import zmq
import json
import signal
from enums import AcceptableKlineValues

class Node:
    enabled = False
    def __init__(self, name, id=None):
        self.context = zmq.Context()
        self.name = name
        self.upstream_controller = Controller()
        self.downstream_controller = Controller()
        signal.signal(signal.SIGINT, self.shutdown)

    def add_upstream(self, name, port, type, topic="0", bind=False):
        self.upstream_controller.add_stream(name, port, type, topic, bind)
        
    def add_downstream(self, name, port, type, topic="0", bind=False):
        self.downstream_controller.add_stream(name, port, type, topic, bind)

    def enable(self):
        self.enabled = True

    def disable(self):
        self.enabled = False

    def recv(self):
        return self.upstream_controller.recv()

    def send(self):
        return self.downstream_controller.send()

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
    def heartbeat():
        pass
class Algorithm(Node):
    def __init__(self, name, ticker, topic, upstream_port, downstream_port, nobind=False):
        super().__init__(name)
        self.data_controller = Controller()
        self.upstream_controller = Controller()
        self.downstream_controller = Controller()
        
    def load_config(self):
        try:
            with open("config/generated.json") as config:
                raw_config = json.load(config)
        except FileNotFoundError:
            print("Algorithm Config Is Missing!")
        pass
    def add_data_clock(self, port, name):
        self.data_controller.add_stream(name, port, type=zmq.SUB)

    def remove_data_clock(self, name):
        # TODO: Close the connection properly.
        pass

    def recv_config_data(self):
        pass

    def recv_ready_signal(self):
        pass

    def recv_all_data(self):
        pass

    def recv_data(self, clock=AcceptableKlineValues.KLINE_INTERVAL_RT):
        # Pull it from the correct data port
        pass

    def reload_config(self):
        # self.clean()
        # self.disable
        self.load_config()
        # self.enable
    def setup():
        raise Exception("Override Me!")

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