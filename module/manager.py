from sys import path,argv
path.insert(1, 'lib')
from module import Node
import zmq
import json
import time
import pandas as pd
from ast import literal_eval
from enums import AcceptableKlineValues, Sleep

from zmq.eventloop import ioloop, zmqstream
import asyncio

import os


class Manager(Node):
    def __init__(self,system_name) -> None:
        self.name = "Manager"
        super().__init__(system_name, self.name)
        self.market_configs = {}
        self.ticker_configs = {}
        self.tickers_with_topic = {}
        self.setup()
        #TODO: Load Upstream From Config
        #TODO: Load Ticker Starting Ports from Generated Config
        
    def setup(self):
        self.load_configs()
        self.setup_upstream()
        self.setup_downstream()
        #TODO Map Bindings of Ticker to Port.
    def test_message(self, msg):
        print ("TESTTESTTEST")
    def load_configs(self):
        # Manager Node needs two configs to work: Traders and Market

        # Load Market Configs
        for filename in os.listdir(os.getcwd() + "/config/generated/" + self.system_name + "/market"):
            with open(os.path.join(os.getcwd()+ "/config/generated/" + self.system_name + "/market/"  + filename), 'r') as config:
                raw_config = json.load(config)
                self.market_configs[raw_config["name"]] = raw_config
                self.mappings = raw_config["tracked_tickers"]
                for mapping in self.mappings:
                    self.tickers_with_topic.update(mapping)
        # Load Ticker Configs
        for filename in os.listdir(os.getcwd() + "/config/generated/" + self.system_name + "/ticker"):
            with open(os.path.join(os.getcwd() + "/config/generated/" + self.system_name + "/ticker/"  + filename), 'r') as config:
                raw_config = json.load(config)
                self.ticker_configs[raw_config["name"]] = raw_config
        print(self.market_configs)
        print(self.ticker_configs)

    def setup_upstream(self):
        for market in self.market_configs.keys():
            # TODO: Extra Level of Abstraction for Collection of Controllers
            for interval in self.market_configs[market]["sources"].keys():
                port = self.market_configs[market]["sources"][interval]
                #TODO: Multimarket support 
                #TODO: Multiticker supports
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
                    socket = self.upstream_controller.get_stream_raw(interval + "." + ticker)
                    stream_sub = zmqstream.ZMQStream(socket)
                    stream_sub.on_recv(self.test_message)
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
            #TODO: Event Loop
            ioloop.IOLoop.instance().start()
            return
            upstreams = self.upstream_controller.get_streams()
            downstreams = self.downstream_controller.get_streams()
            #print(all_streams)
            upstream_socket_map = {}
            downstream_name_map = {}
            for stream in upstreams.keys():
                #print(all_streams[stream])
                #print(all_streams[stream].name)
               upstream_socket_map[upstreams[stream].get_socket()] = upstreams[stream].name

            #print(stream_socket_map)
            #print(len(self.upstream_controller.recv_snapshot().keys()))

            for stream in downstreams.keys():
                #print(all_streams[stream])
                #print(all_streams[stream].name)
               downstream_name_map[downstreams[stream].name] = downstreams[stream].get_socket()


            for stream in self.upstream_controller.recv_snapshot():
                #We have a dictionary of streams. Which one do we have
                input_stream = upstream_socket_map[stream]
                raw_data = stream.recv().decode('UTF-8')
                data = {'topic': raw_data[:1], 'message':raw_data[1:]}
                message = pd.read_json(data["message"])
                print(input_stream)
                print(self.downstream_controller.get_stream(input_stream).port)
                self.downstream_controller.send_to(input_stream, message.to_json())
            time.sleep(1)
            
if __name__ == "__main__":
    M = Manager(str(argv[1]))
    M.run()
        


    



