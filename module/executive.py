import sys
sys.path.insert(1, 'lib')
from module import Node
import zmq
import json

class Executive(Node):
    def __init__(self, name, downstream_port) -> None:
        super().__init__(name)
        self.set_downstream(zmq.PUB, downstream_port, nobind=True)
    def run(self):
        while True:
            pass

def load_downstream_from_config():
    try:
        with open("config/config.json") as ticker_credentials:
            loadded_config = json.load(ticker_credentials)
            for ticker in loadded_config["module_config"]:
                if ticker["name"] != "executive":
                    next
                return ticker["downstream"]["port"]

    except FileNotFoundError:
        print("Error, config/config.json file not found")
        exit(-1)
    return loadded_config

def heartbeat():
    # Check to make sure every single node is alive.
    pass

if __name__ == "__main__":
    name = "Executive"
    downstream_port = None
    try:
        downstream_port = int(sys.argv[1])
    except IndexError:
        downstream_port = load_downstream_from_config()
    E = Executive(name, downstream_port)
    E.run()

    