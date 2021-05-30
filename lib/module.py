import sys
sys.path.insert(1, 'lib')
from controller import DownstreamController, UpstreamController
import zmq
import json
import signal

class Node:
    enabled = False
    def __init__(self, name, id=None):
        self.context = zmq.Context()
        self.name = name
        self.upstream_controller = UpstreamController()
        self.downstream_controller = DownstreamController()
        signal.signal(signal.SIGINT, self.shutdown)

    def add_upstream(self, name, port, type, topic="0", bind=False):
        self.upstream_controller.add_stream(name, port, type, topic, bind)
        
    def add_downstream(self, name, port, type, topic="0", bind=False):
        self.downstream_controller.add_stream(name, port, type, topic, bind)

    def enable(self):
        self.enabled = True

    def disable(self):
        self.enabled = False

    def consume(self):
        return self.upstream_controller.consume()

    def produce(self):
        return self.downstream_controller.produce()

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

class Algorithm(Node):
    def __init__(self, name, ticker, topic, upstream_port, downstream_port, nobind=False):
        super().__init__(name)
    def load_config(self):
        try:
            with open("config/generated.json") as config:
                raw_config = json.load(config)
        except FileNotFoundError:
            print("Algorithm Config Is Missing!")
        pass
    def reload_config(self):
        self.load_config()
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