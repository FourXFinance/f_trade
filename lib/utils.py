from os import name
import zmq

class Stream:
    def __init__(self, name, port, type, topic="0", bind=False) -> None:
        self.context = zmq.Context()
        self.name = name
        self.port = port
        self.topic = topic
        self.type = type
        self.bind = bind
        self.socket = None
        self.setup_stream()

    def setup_stream(self):
        self.socket = self.context.socket(self.type)
        if self.type in (zmq.XSUB, zmq.XPUB, zmq.PUB) or self.bind:
            self.socket.bind("tcp://*:%d" % self.port)
        elif self.type == zmq.SUB:
            self.socket.connect("tcp://localhost:%d" % self.port)
            self.socket.setsockopt_string(zmq.SUBSCRIBE, self.topic)
        else:
            raise Exception("Other Zmq socket types not supported")
    def getStream(self):
        return self.socket

class Controller:
    def __init__(self) -> None:
        self.streams = {}
        self.poller = zmq.Poller()
    def add_stream(self, name, port, type, topic="0", bind=False):
        if name in self.streams:
            raise Exception("Controller already has stream")
        self.streams[name] = Stream(name, port, type, topic, bind)
        self.poller.register(self.streams[name].getStream(), zmq.POLLIN)

    def get_list_of_streams(self):
        return self.streams.keys
            
class DownstreamController(Controller):
    def __init__(self) -> None:
        super().__init__()
    def add_stream(self, name, port, type, topic, bind=False):
        return super().add_stream(name, port, type, topic=topic, bind=bind)
        
    def produce(self, message):
        if len(self.streams) == 0 :
            raise Exception("Downstream Controller has no streams!")
        elif len(self.streams) > 1 :
            raise Exception("Downstream Controller has more than one stream!")
        target_stream = self.streams[0]
        target_stream.getStream().send_string("%d %s" % (self.topic ,message))

    def produce_for(self, message, target_stream=None):
        if len(self.streams) == 0 :
            raise Exception("Downstream Controller has no streams!")
        elif len(self.streams) == 1 :
            return self.produce()
        target_stream = self.streams[target_stream]
        target_stream.getStream().send_string("%d %s" % (target_stream.topic ,message))
    
class UpstreamController(Controller):
    def __init__(self) -> None:
        super().__init__()
        
    def add_stream(self, name, port, type, topic="0", bind=False):
        return super().add_stream(name, port, type, topic=topic, bind=bind)

    def consume(self):
        if len(self.streams) == 0 :
            raise Exception("Upstream Controller has no streams!")
        elif len(self.streams) > 1 :
            raise Exception("Upstream Controller has more than one stream!")
        target_stream = self.streams[0]
        target_stream.getStream().consume()

    def consume_from(self,target_stream=None):
        if len(self.streams) == 0 :
            raise Exception("Upstream Controller has no streams!")
        elif len(self.streams) == 1 :
            return self.produce()
        target_stream = self.streams[target_stream]
        target_stream.getStream().consume()

    def consume_next(self):
        if len(self.streams) == 0 :
            raise Exception("Upstream Controller has no streams!")
        streams = dict(self.poller.poll())
        for stream in streams:
            print (stream.recv_string())