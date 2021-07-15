from sys import path,argv
path.insert(1, 'lib')
from module import Node
import zmq
import json
import time
from enums import AcceptableKlineValues, Sleep
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
                print(self.tickers_with_topic)
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
                print(port)
                #TODO: Multimarket support
                #TODO: Multiticker supports
                self.upstream_controller.add_stream( 
                    interval,
                    port,
                    zmq.SUB,
                    bind=False,
                    register=True
                )                    
    def setup_downstream(self):
        for ticker in self.ticker_configs.keys():
            # TODO: Extra Level of Abstraction for Collection of Controllers
            for market in self.ticker_configs[ticker]["required_sources"].keys():
                for source in self.ticker_configs[ticker]["required_sources"][market].keys():
                    port = self.ticker_configs[ticker]["required_sources"][market][source]
                    self.downstream_controller.add_stream( 
                        ticker + "." + source,
                        port,
                        zmq.PUB,
                        bind=True,
                        register=False
                    )

    def run(self):
        while True:
            #TODO: Event Loop
            all_streams = self.upstream_controller.get_streams()
            #print(all_streams)
            stream_socket_map = {}
            for stream in all_streams.keys():
                #print(all_streams[stream])
                #print(all_streams[stream].name)
               stream_socket_map[all_streams[stream].get_socket()] = all_streams[stream].name
            print(stream_socket_map)
            for stream in self.upstream_controller.recv_snapshot():
                #We have a dictionary of streams. Which one do we have
                print (stream_socket_map[stream]) # Yes we are using an object hash as a key!
                # From here we can figure out what Upstream We have!

            
            #print("Getting Message")
            #message = self.upstream_controller.recv_from("5m")
            #print(message)
            time.sleep(1)
            
if __name__ == "__main__":
    M = Manager(str(argv[1]))
    M.run()
        


    



