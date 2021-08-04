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
import argparse
from datetime import datetime
class Ticker(Node):
    def __init__(self,system_name, ticker_name, test_mode = False) -> None:
        self.name = "Ticker"
        self.ticker_name = ticker_name
        super().__init__(system_name, self.name, test_mode)
        self.algorithm_config = {}
        self.setup()

    def setup(self):
        self.load_config()
        self.setup_streams()
        self.build_mappings()
        #self.setup_downstream()
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
        # print(self.algorithm_config)

    def setup_streams(self):
        required_sources = self.config["required_sources"]
        for market in required_sources:
            for interval in required_sources[market]:
                port = required_sources[market][interval]
                #print(port, ".", interval)
                self.upstream_controller.add_stream( 
                            interval,
                            port,
                            zmq.SUB,
                            # topic=interval, #TODO: Topic is vital for us to reduce port usage. WI
                            bind=False,
                            register=True
                        )
                #print(self.downstream_controller.get_stream(interval))
                socket = self.upstream_controller.get_stream_raw(interval)
                stream_sub = zmqstream.ZMQStream(socket)
                stream_sub.on_recv_stream(self.iterate)
                #TODO: Only RT is supported for now. Well Technicaly only '1' data stream is supported. Working on this
        self.downstream_controller.add_stream( 
                    "DATA",
                    self.config["algorithm_port"],
                    zmq.PUB,    
                    topic=interval,
                    bind=True, #Maybe a Proxy can prevent this
                    register=False,
                        )
    def disable_algorithm(self):
        pass
    def enable_algorithm(self):
        pass    
    def clean_all(self):
        pass
    def clean_algorithm(self):
        pass

    def iterate(self, stream, msg):
        #print(stream)
        now = datetime.now().time()
        # print(self.upstream_socket_map)
        # print(self.downstream_name_map)
        stream_name = self.upstream_socket_map[stream.socket]
        #stream = self.downstream_controller.get_stream(stream_name)
        # (stream_name)
        #print(stream)
        # Now we have the name of our stream!
        raw_data = msg[0].decode("utf-8")  # For Reaons beyond me, this is an array of data.
        data = {'topic': raw_data[:1], 'message': raw_data[1:]}
        message = pd.read_json(data["message"])
        #print(message)
        #TODO: Tickers have an N:1 input:ouput mapping. Let's change this to a N:N (Output has N streams on the same port, different topics though)
        self.downstream_controller.send_to("DATA", message.to_json(), topic=stream_name)

    def run_test_mode(self):
        print("We Are In Test Mode")
        while True:
                for stream_name in self.downstream_controller.get_streams_list():
                    stream = self.downstream_controller.get_stream(stream_name)
                    self.downstream_controller.get_stream(stream_name).send("TEST_MSG", stream.topic)
                    time.sleep(1)
    def run(self):        
        if self.test_mode:
            self.run_test_mode()
        ioloop.IOLoop.instance().start()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("market")
    parser.add_argument("ticker")
    parser.add_argument("--test", help="Runs the module in test mode", action="store_true")
    parser.add_argument("--verbose", help="Runs the module in verbose mode (all data will be dumped to screen)", action="store_true")
    args = parser.parse_args()
    T = Ticker(str(args.market), str(args.ticker), test_mode=args.test)
    T.run()





