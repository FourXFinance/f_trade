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
        self.setup()
        #TODO: Load Upstream From Config
        #TODO: Load Ticker Starting Ports from Generated Config
    
    def load_configs(self):
        # Manager Node needs two configs to work: Traders and Market

        # Load Market Configs
        for filename in os.listdir(os.getcwd() + "/config/generated/" + self.system_name + "/market"):
            with open(os.path.join(os.getcwd()+ "/config/generated/" + self.system_name + "/market/"  + filename), 'r') as config:
                raw_config = json.load(config)
                self.market_configs[raw_config["name"]] = raw_config
        # Load Ticker Configs
        for filename in os.listdir(os.getcwd() + "/config/generated/" + self.system_name + "/ticker"):
            with open(os.path.join(os.getcwd()+ "/config/generated/" + self.system_name + "/ticker/"  + filename), 'r') as config:
                raw_config = json.load(config)
                self.ticker_configs[raw_config["name"]] = raw_config

        print(self.market_configs)
        print(self.ticker_configs)

    def setup(self):
        self.load_configs()
        pass

    def run(self):
        while True:
            time.sleep(1)
            
if __name__ == "__main__":
    M = Manager(str(argv[1]))
    M.run()
        


    



