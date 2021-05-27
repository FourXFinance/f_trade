import sys
sys.path.insert(1, 'lib')
from module import Node
import zmq
import json

class Account(Node):
    def __init__(self) -> None:
        super().__init__()


if __name__ == "__main__":
    name = "Account"
    ticker = sys.argv[0]
    upstream = sys.argv[1]
    downstream = sys.argv[2]

    



