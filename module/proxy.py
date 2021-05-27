  
import sys
sys.path.insert(1, 'lib')
from module import Proxy

if __name__ == "__main__":
    proxy_name = sys.argv[1]
    upstream_port = int(sys.argv[2])
    downstream_port = int(sys.argv[3])
    P = Proxy(proxy_name, upstream_port, downstream_port)
    P.run()