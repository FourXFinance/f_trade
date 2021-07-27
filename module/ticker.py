from sys import path,argv
path.insert(1, 'lib')
from module import Node
import zmq
import json
import time
import pandas as pd
from ast import literal_eval
from zmq.eventloop import ioloop, zmqstream
from enums import AcceptableKlineValues, Sleep
import os
from datetime import datetime
class Ticker(Node):
    def __init__(self,system_name, ticker_name) -> None:
        self.name = "Ticker"
        self.ticker_name = ticker_name
        super().__init__(system_name, self.name)
        self.algorithm_config = {}
        self.setup()
    def setup(self):
        
        self.load_config()
        self.setup_upstream()
        self.setup_downstream()
        self.setup_heartbeat()

    def load_config(self):
        try:
            with open("config/generated/" + self.system_name + "/ticker/" + self.ticker_name + ".json") as config:
                raw_credentials = json.load(config)
                #print(raw_credentials)
                self.config = raw_credentials
        except FileNotFoundError:
            print("config/generated/" + self.system_name + "/market/" + self.market_name + ".json")
            raise FileNotFoundError

        for filename in os.listdir(os.getcwd() + "/config/generated/" + self.system_name + "/algorithm/" + self.ticker_name):
            with open(os.path.join(os.getcwd() + "/config/generated/" + self.system_name + "/algorithm/"  + self.ticker_name + "/" + filename), 'r') as config:
                raw_config = json.load(config)
                self.algorithm_config[raw_config["algorithm_name"]] = raw_config
        #print(self.algorithm_config)

    def setup_upstream(self):
        required_sources = self.config["required_sources"]
        for market in required_sources:
            for interval in required_sources[market]:
                port = required_sources[market][interval]
                self.upstream_controller.add_stream( 
                            interval,
                            port,
                            zmq.SUB,
                            bind=False,
                            register=True
                        )

    def setup_downstream(self):
        self.downstream_controller.add_stream( 
                            "DATA",
                            self.config["algorithm_port"],
                            zmq.PUB,
                            bind=True,
                            register=False
                        )
            
    def disable_algorithm(self):
        pass
    def enable_algorithm(self):
        pass
    def clean_all(self):
        pass
    def clean_algorithm(self):
        pass
    def run(self):
        
        upstreams = self.upstream_controller.get_streams()
        upstream_socket_map = {}
        for stream in upstreams.keys():
            #print(all_streams[stream])
            #print(all_streams[stream].name)
            upstream_socket_map[upstreams[stream].get_socket()] = upstreams[stream].name
        while True:
            for stream in self.upstream_controller.recv_snapshot():
                now = datetime.now().time()
                #print(self.name, " : ", now)
                #We have a dictionary of streams. Which one do we have
                input_stream = upstream_socket_map[stream]
                raw_data = stream.recv().decode('UTF-8')
                data = {'topic': raw_data[:1], 'message':raw_data[1:]}
                message = pd.read_json(data["message"])
                #print(message)
                self.downstream_controller.send_to("DATA", message.to_json())
            #time.sleep(1)

if __name__ == "__main__":
    T = Ticker(str(argv[1]), str(argv[2]))
    T.run()





