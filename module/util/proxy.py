import sys
sys.path.insert(1, 'lib')
from module import Proxy

# A proxy simply connects the port mentioned in arg[2] to arg[3]
if __name__ == "__main__":
    system_name = sys.argv[1]
    ticker_name = (sys.argv[2])
    P = Proxy(system_name, ticker_name)
    P.run()