from datetime import datetime
from zmq.eventloop import ioloop, zmqstream
from enums import AcceptableKlineValues
import uuid
import signal
import json
import zmq
from controller import Controller
import sys
import argparse

sys.path.insert(1, 'lib')
import argparse
class Node:
    enabled = False

    def __init__(self, system_name, name, test_mode = False):
        
        self.mode = 0  # TODO: System Modes
        self.name = name  # TODO: System Name should be more specilized
        self.test_mode = test_mode
        self.system_name = system_name
        self.context = zmq.Context()
        self.logging_enabled = False

        # A controller is a group of streams.
        self.upstream_controller = Controller()
        self.downstream_controller = Controller()
        self.executive_controller = Controller()
        self.logging_controller = Controller()
        self.heartbeat_controller = Controller()

        # A Default Controller
        self.default_controller = Controller()
        # This 'might' be used for loggin purposes later on.
        self.identifier = uuid.uuid4()

        if self.logging_enabled:
            self.logging_controller.add_stream(
                "LOG", 10000, zmq.PUB, topic="0", bind=False, register=False)

        # We want to define how we interrupt the system
        # This is required as we might want to do clean up. Or even ignore certain events!
        signal.signal(signal.SIGINT, self.shutdown)  # Ctrl+c
        # signal.signal(signal.SIGUSR1, None) # TODO: User Defined 1
        # signal.signal(signal.SIGUSR2, None) # TODO: User Defined 2

    def setup_heartbeat(self, override_port=None):
        """
        Setup up the required port for the heartbeat. In Future this will be automated. As it stands now Heart
        beat ports are not related to the node port
        """
        port = None
        if override_port != None:  # The Manager Node does not have a generated config. TODO: Create Config for Manager Node. Even if it is just it's heartbeat port
            port = override_port
        else:
            port = self.config["heartbeat_port"]
        # print(port)
        self.heartbeat_controller.add_stream(
            "HEARTBEAT", port, zmq.PAIR, topic="0", bind=True, register=False)
        socket = self.heartbeat_controller.get_stream_raw("HEARTBEAT")
        stream_sub = zmqstream.ZMQStream(socket)
        stream_sub.on_recv_stream(self.heartbeat)

    def heartbeat(self, stream, msg):
        """
        Heartbeat What do we respond with when we get a liveliness check from the heartbeat controller
        """
        message = msg[0].decode('UTF-8')
        now = datetime.now().time()
        if message == "PING":
            self.heartbeat_controller.send_to("HEARTBEAT", {
                "name": self.name,
                "response": "",
                "ts": str(now)
            }
            )
        # TODO: Move these to executive
        elif message == "SETUP":
            self.enable()
        elif message == "STOP":
            self.disable()
        elif message == "START":
            pass
        else:
            # We should not be sending other messages on the heartbeat request.
            pass

    def handle_executive(self, stream, msg):
        """
        handle_executive. How do we action and respond to messages from the executive controller
        """
        pass

    def add_stream(self, name, port, type, topic="0", bind=False, register=False):
        """
        Add a Stream to the nodes default_controller
        This is generally not recommended. But sometimes streams don't fall into nice catagories
        """
        self.default_controller.add_stream(
            name, port, type, topic, bind, register)

    def add_upstream(self, name, port, type, topic="0", bind=False, register=False):
        """
        Add a Stream to the nodes upstream_controller
        """
        self.upstream_controller.add_stream(
            name, port, type, topic, bind, register)

    def add_downstream(self, name, port, type, topic="0", bind=False, register=False):
        """
        Add a Stream to the nodes downstream_controller
        """
        self.downstream_controller.add_stream(
            name, port, type, topic, bind, register)

    def enable(self):
        # Set up the system to run and consume date.
        # Set up event handlers, etc
        raise Exception("Override Me!")

    def disable(self):
        # Pause execution/clean if required
        raise Exception("Override Me!")

    def load_config(self, path):
        # TODO: Load Configs in as standard a way as possible
        pass

    def recv(self):
        """
        DEPRECATED:
        Recv content from a upstream_controller stream
        This only works if the upstream_controller has on stream        
        """
        return self.upstream_controller.recv()

    def recv_from(self, stream_name):
        """
        DEPRECATED:
        Recv content from a specific upstream_controller stream

        This is generally avoided as we are now event-driven        
        """
        return self.upstream_controller.recv_from(stream_name)

    def send_to(self, stream_name, message, topic="0"):
        """
        Send content to a specific downstream_controller stream
        """
        # TODO: Iterate through all controllers to find target stream
        result = self.downstream_controller.send_to(
            stream_name, message, topic)
        if result and self.logging_enabled:
            # Not Sure what else do to with logging. Add PORT!
            self.logging_controller.send_to(
                "LOG", str(self.identifier) + message)

    def run(self):
        """
        Start the main execution loop of this node
        """
        raise Exception("Override Me!")

    def shutdown(self, sig, frame):
        """
        Gracefully handle a SIGINT (15) request from the OS
        """
        print("Safe Shutdown Process")
        ioloop.IOLoop.instance().stop()
        # TODO: Send out a
        sys.exit(0)

    def build_mappings(self):
        """
        Build the zmq_object-stream mappings (for upstream_controller)
        Build the stream-zmq_object mappings (for upstream_controller)
        """
        upstreams = self.upstream_controller.get_streams()
        downstreams = self.downstream_controller.get_streams()
        # TODO: Build Mappings for other controllers
        self.upstream_socket_map = {}
        self.downstream_name_map = {}
        for stream in upstreams.keys():
            self.upstream_socket_map[upstreams[stream].get_socket(
            )] = upstreams[stream].name
        for stream in downstreams.keys():
            self.downstream_name_map[downstreams[stream].name] = downstreams[stream].get_socket(
            )


class Algorithm(Node):
    def __init__(self, system_name, ticker, test_mode=False):
        self.ticker = ticker
        super().__init__(system_name, self.name, test_mode)
        self.setup()
        # TODO:Algorithms should have HWM set to 1!

    def load_config(self):
        try:
            with open("config/generated/" + self.system_name + "/algorithm/" + self.ticker + "/" + self.name + ".json") as config:
                self.config = json.load(config)
        except FileNotFoundError:
            print("Algorithm Config Is Missing!")

    def setup(self):
        self.load_config()
        self.configure()
        self.setup_heartbeat()

    def configure(self):
        for source in self.config["available_ticker_sources"]:
            self.upstream_controller.add_stream("DATA." + str(source),
                                                self.config["algorithm_port"],
                                                zmq.SUB,
                                                topic=str(source))
            socket = self.upstream_controller.get_stream_raw("DATA." + str(source))
            stream_sub = zmqstream.ZMQStream(socket)
            stream_sub.on_recv_stream(self.iterate)

        self.downstream_controller.add_stream("PROXY",
                                              self.config["proxy_port"],
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
    # TODO: Proxies should be more generic
    # TODO: Rewrite Proxies to be Event Driven.
    def __init__(self, system_name, ticker_name):
        self.name = "PROXY"
        self.ticker_name = ticker_name
        super().__init__(system_name, self.name)
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
            print("config/generated/" + self.system_name +
                  "/proxy/" + self.market_name + ".json")
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
        zmq.proxy(self.upstream_controller.get_stream("UP").get_socket(),
                  self.downstream_controller.get_stream("DOWN").get_socket())
