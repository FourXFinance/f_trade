import sys
sys.path.insert(1, 'lib')
from module import Node
import zmq
import json

class Manager(Node):
    def __init__(self) -> None:
        super().__init__()


if __name__ == "__main__":
    name = "Trader"
    ticker = sys.argv[0]
    upstream = sys.argv[1]
    



