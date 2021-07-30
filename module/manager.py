from sys import path, argv
path.insert(1, 'lib')
import os
import asyncio
from datetime import datetime
from zmq.eventloop import ioloop, zmqstream
from ast import literal_eval
import pandas as pd
import time
import json
import zmq
from module import Node
from enums import AcceptableKlineValues, Sleep


class Manager(Node):
    def __init__(self, system_name) -> None:
        self.name = "Manager"
        super().__init__(system_name, self.name)
        self.market_configs = {}
        self.ticker_configs = {}
        self.tickers_with_topic = {}
        self.setup()

    def setup(self):
        self.load_configs()
        self.setup_upstream()
        self.setup_downstream()
        self.build_mappings()
        self.setup_heartbeat(self.heartbeat_port)

    def iterate(self, stream, msg):
        now = datetime.now().time()
        # Now we have the name of our stream!
        stream_name = self.upstream_socket_map[stream.socket]
        raw_data = msg[0]  # For Reaons beyond me, this is an array of data.
        data = {'topic': raw_data[:1], 'message': raw_data[1:]}
        message = pd.read_json(data["message"])
        #print(message)
        self.downstream_controller.send_to(stream_name, message.to_json())

    def load_configs(self):
        # Manager Node needs three sets of configs to work: Manager, Tickers and Markets

        # Load Manager Config
        with open(os.path.join(os.getcwd() + "/config/generated/" + self.system_name + "/manager/" + "manager.json"), 'r') as config:
            raw_config = json.load(config)
            self.heartbeat_port = raw_config["heartbeat_port"]

        # Load Market Configs
        for filename in os.listdir(os.getcwd() + "/config/generated/" + self.system_name + "/market"):
            with open(os.path.join(os.getcwd() + "/config/generated/" + self.system_name + "/market/" + filename), 'r') as config:
                raw_config = json.load(config)
                self.market_configs[raw_config["name"]] = raw_config
                self.mappings = raw_config["tracked_tickers"]
                for mapping in self.mappings:
                    self.tickers_with_topic.update(mapping)

        # Load Ticker Configs
        for filename in os.listdir(os.getcwd() + "/config/generated/" + self.system_name + "/ticker"):
            with open(os.path.join(os.getcwd() + "/config/generated/" + self.system_name + "/ticker/" + filename), 'r') as config:
                raw_config = json.load(config)
                self.ticker_configs[raw_config["name"]] = raw_config

    def setup_upstream(self):
        for market in self.market_configs.keys():
            # TODO: Extra Level of Abstraction for Collection of Controllers
            for interval in self.market_configs[market]["sources"].keys():
                port = self.market_configs[market]["sources"][interval]
                # TODO: Multimarket support
                # TODO: Multiticker supports
                for ticker in self.tickers_with_topic.keys():
                    topic = self.tickers_with_topic[ticker]
                    self.upstream_controller.add_stream(
                        interval + "." + ticker,
                        port,
                        zmq.SUB,
                        topic=topic,
                        bind=False,
                        register=True
                    )
                    socket = self.upstream_controller.get_stream_raw(
                        interval + "." + ticker)
                    stream_sub = zmqstream.ZMQStream(socket)
                    stream_sub.on_recv_stream(self.iterate)

    def setup_downstream(self):
        for ticker in self.ticker_configs.keys():
            # TODO: Extra Level of Abstraction for Collection of Controllers
            for market in self.ticker_configs[ticker]["required_sources"].keys():
                for interval in self.ticker_configs[ticker]["required_sources"][market].keys():
                    port = self.ticker_configs[ticker]["required_sources"][market][interval]
                    self.downstream_controller.add_stream(
                        interval + "." + ticker,
                        port,
                        zmq.PUB,
                        bind=True,
                        register=False
                    )

    def run(self):
        while True:
            # TODO: Event Loop
            ioloop.IOLoop.instance().start()
            return


if __name__ == "__main__":
    M = Manager(str(argv[1]))
    M.run()
