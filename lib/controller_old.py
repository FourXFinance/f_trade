from os import name
import zmq

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
                print ("Setting Topic to " + str(self.topic))
                self.socket.setsockopt_string(zmq.SUBSCRIBE, str(self.topic))

    def get_stream(self):
        return self.socket

class Controller:
    def __init__(self) -> None:
        self.streams = {}
        self.poller = zmq.Poller()
    def add_stream(self, name, port, type, topic="0", bind=False):
        if name in self.streams:
            raise Exception("Controller already has stream")
        self.streams[name] = Stream(name, port, type, topic, bind)
        self.poller.register(self.streams[name].get_stream(), zmq.POLLIN)

    def get_streams(self):
        return self.streams
            
class DownstreamController(Controller):
    def __init__(self) -> None:
        super().__init__()
    def add_stream(self, name, port, type, topic="0", bind=False):
        super().add_stream(name, port, type, topic=topic, bind=bind)
        
    def produce(self, message):
        if len(self.streams) == 0 :
            raise Exception("Downstream Controller has no streams!")
        elif len(self.streams) > 1 :
            raise Exception("Downstream Controller has more than one stream!")
        target_stream = self.streams[list(self.streams.keys())[0]]
        if target_stream.type == zmq.PUB:
            target_stream.get_stream().send_string("%d %s" % (target_stream.topic ,message))
            return True
        elif target_stream.type == zmq.REQ:
            target_stream.get_stream().send_string("%d %s" % (target_stream.topic ,message))
            return target_stream.get_stream().recv()

    def produce_for(self, message, target_stream=None):
        if len(self.streams) == 0 :
            raise Exception("Downstream Controller has no streams!")
        elif len(self.streams) == 1 :
            return self.produce(message)
        
        target_stream = self.streams[target_stream]
        if target_stream.type == zmq.PUB:
            target_stream.get_stream().send_string("%d %s" % (target_stream.topic ,message))
            return True
        elif target_stream.type == zmq.REQ:
            target_stream.get_stream().send_string("%d %s" % (target_stream.topic ,message))
            return target_stream.get_stream().recv()
        
    
class UpstreamController(Controller):
    def __init__(self) -> None:
        super().__init__()
        
    def add_stream(self, name, port, type, topic="0", bind=False):
        super().add_stream(name, port, type, topic=topic, bind=bind)

    def consume(self):
        if len(self.streams) == 0 :
            raise Exception("Upstream Controller has no streams!")
        elif len(self.streams) > 1 :
            raise Exception("Upstream Controller has more than one stream!")
        target_stream = self.streams[list(self.streams.keys())[0]]
        return target_stream.get_stream().recv()

    def consume_from(self,target_stream=None):
        if len(self.streams) == 0 :
            raise Exception("Upstream Controller has no streams!")
        elif len(self.streams) == 1:
            return self.consume()
        stream = None
        try:
            stream = self.streams[target_stream]
        except KeyError as KE:
            print ("Stream: %s does not exist" % (target_stream))
            return None
        return stream.get_stream().recv()

    def consume_next(self):
        if len(self.streams) == 0 :
            raise Exception("Upstream Controller has no streams!")
        streams = dict(self.poller.poll())
        return streams

    def respond(self, message):
        if len(self.streams) == 0 :
            raise Exception("Upstream Controller has no streams!")
        elif len(self.streams) > 1 :
            raise Exception("Upstream Controller has more than one stream!")
        target_stream = self.streams[list(self.streams.keys())[0]]
        if target_stream.type != zmq.REP:
            raise Exception("Stream is not of type REP")
        

    def respond_to(self,message, target_stream=None):
        if len(self.streams) == 0:
            raise Exception("Upstream Controller has no streams!")
        elif len(self.streams) == 1:
            return self.respond()
        stream = None
        try:
            stream = self.streams[target_stream]
        except KeyError as KE:
            print ("Stream: %s does not exist" % (target_stream))
            return None
        if target_stream.type != zmq.REP:
            raise Exception("Stream is not of type REP")
        stream.get_stream().send_string("%d %s" % (target_stream.topic ,message)) 
        return True
    


class LoggingController(Controller):
    def __init__(self) -> None:
        super().__init__()

class ExecutiveController(Controller):
    def __init__(self) -> None:
        super().__init__()