import sys
from time import time
sys.path.insert(1, 'lib')
from constants import POLLER_TIMEOUT
from os import name

import zmq

# A Stream is a ZMQ socket
class Stream:
    """
    Streams are 'named' versions of zmq_stream objects.
    """
    def __init__(self, name, port, type, topic="0", bind=False) -> None:
        self.context = zmq.Context()
        self.name = name
        self.port = int(port)
        self.topic = topic
        self.type = type
        self.bind = bind
        self.socket = None
        self.setup_stream()

    def setup_stream(self):
        self.socket = self.context.socket(self.type)
        self.socket.set_hwm(1)
        if self.bind:
            self.socket.bind("tcp://*:%d" % self.port)
        else:
            self.socket.connect("tcp://localhost:%d" % self.port)
            if self.type == zmq.SUB:
                self.socket.setsockopt_string(zmq.SUBSCRIBE, str(self.topic))

    def get_socket(self):
        return self.socket

    def send(self, message, topic="0"):
        self.socket.send_string("%s %s" % (topic, message))
    def get_stream_info(self):
        return {
            "name" : self.name,
            "port" : self.port,
            "topic" : self.topic,
            "bind" : self.bind,
        }
class Controller:
    """
    Controllers are collecitons of Streams with some additional functionality built on top
    """
    def __init__(self) -> None:
        self.streams = {}
        self.poller = zmq.Poller()
        self.PTIMEOUT = POLLER_TIMEOUT
    
    def add_stream(self, name, port, type, topic="0", bind=False, register=False):
        if name in self.streams:
            raise Exception("Controller already has stream")
        self.streams[name] = Stream(name, port, type, topic, bind)      
        if register:
            self.poller.register(self.streams[name].get_socket(), zmq.POLLIN)
    
    def get_stream_raw(self, name):
        return self.get_stream(name).get_socket()

    def get_stream(self, name):
        return self.streams[name]
    
    def get_streams(self):
        return self.streams
    
    def get_streams_list(self):
        return self.streams.keys()
    # Communication Methods
    # Designed to be invarient of underlying stream type

    def send(self, message):
        s = self.streams[list(self.streams.keys())[0]]
        s.send(message)
        return True

    def send_to(self, target_stream, message, topic="0"):
        s = self.streams[target_stream]
        s.send(message, topic=topic)
        return True

    def recv(self):
        r = self.streams[list(self.streams.keys())[0]]
        message = r.get_stream().recv()
        return message

    def recv_from(self, target_stream):
        r = self.streams[target_stream]
        message = r.get_socket().recv()
        return message

    def recv_snapshot(self, timeout=POLLER_TIMEOUT):              
        streams = dict(self.poller.poll(timeout))
        #for stream in streams:
            #yield stream # Should check on the performance of this.
        return streams
    def get_controller_info(self):
        content = {}
        for stream_name in self.streams.keys():
            content[stream_name] = self.streams[stream_name].get_stream_info()
