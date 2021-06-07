from os import name
import zmq

# A Stream is a ZMQ socket
class Stream:
    def __init__(self, name, port, type, topic="0", bind=False) -> None:
        self.context = zmq.Context()
        self.name = name
        self.port = port
        self.topic = int(topic)
        self.type = type
        self.bind = bind
        self.socket = None
        self.setup_stream()

    def setup_stream(self):
        self.socket = self.context.socket(self.type)
        if self.bind:
            self.socket.bind("tcp://*:%d" % self.port)
        else:
            self.socket.connect("tcp://localhost:%d" % self.port)
            print (str(self.port))
            if self.type == zmq.SUB:
                print(self.topic)
                self.socket.setsockopt_string(zmq.SUBSCRIBE, str(self.topic))

    def get_stream(self):
        return self.socket

class Controller:
    def __init__(self) -> None:
        self.streams = {}
        self.poller = zmq.Poller()
    
    def add_stream(self, name, port, type, topic="0", bind=False, register=True):
        if name in self.streams:
            raise Exception("Controller already has stream")
        self.streams[name] = Stream(name, port, type, topic, bind)
        if register:
            self.poller.register(self.streams[name].get_stream(), zmq.POLLIN)
    
    def get_stream(self, name):
        return self.streams[name]
    
    def get_streams(self):
        return self.streams
    
    # Communication Methods
    # Designed to be invarient of underlying stream type

    def send(self, message):
        s = self.streams[list(self.streams.keys())[0]]
        s.send(message.encode('utf-8'))
        return True

    def send_to(self, target_stream, message):
        s = self.streams[target_stream]
        s.send(message.encode('utf-8'))
        return True

    def recv(self):
        r = self.streams[list(self.streams.keys())[0]]
        message = r.get_stream().recv()
        return message

    def recv_from(self, target_stream, message):
        r = self.streams[target_stream]
        message = r.recv()
        return message

    def poll(self):
        streams = dict(self.poller.poll())
        return streams