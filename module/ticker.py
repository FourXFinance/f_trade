import sys
sys.path.insert(1, 'lib')
from module import Node
import zmq
import json

class Ticker(Node):
    def __init__(self) -> None:
        super().__init__()
    def run():
        while True:
            pass

if __name__ == "__main__":
    name = "Ticker"
    ticker = sys.argv[0]
    upstream = sys.argv[1]
    downstream = sys.argv[2]
    





