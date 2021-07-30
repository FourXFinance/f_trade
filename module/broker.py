import sys
import zmq
import json
sys.path.insert(1, 'lib')
from module import Node

# A proxy simply connects the port mentioned in arg[2] to arg[3]
class BrokerProxy(Node):
    #TODO: Proxies should be more generic
    def __init__(self, system_name):
        self.name = "Broker PROXY"
        super().__init__(system_name,self.name)
        self.setup()

    def setup(self):
        self.load_config()
        self.setup_upstream()
        self.setup_downstream()

    def load_config(self):
        try:
            with open("config/generated/" + self.system_name + "/broker/" + self.system_name + ".json") as config:
                raw_credentials = json.load(config)
                #print(raw_credentials)
                self.config = raw_credentials
        except FileNotFoundError:
            print("config/generated/" + self.system_name + "/broker/" + self.system_name + ".json")
            raise FileNotFoundError

    def setup_upstream(self):
        algorithm_proxy_port = self.config["broker_proxy_port"]
        self.upstream_controller.add_stream( 
                            "UP",
                            algorithm_proxy_port,
                            zmq.XSUB,
                            bind=True,
                            register=False
                        )
        

    def setup_downstream(self):
        account_proxy_port = self.config["trader_proxy_port"]
        self.downstream_controller.add_stream( 
                            "DOWN",
                            account_proxy_port,
                            zmq.XPUB,
                            bind=True,
                            register=False
                        )
    def run(self):
        zmq.proxy(self.upstream_controller.get_stream("UP").get_socket(), self.downstream_controller.get_stream("DOWN").get_socket())

if __name__ == "__main__":
    system_name = sys.argv[1]
    P = BrokerProxy(system_name)
    P.run()