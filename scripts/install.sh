#!/bin/bash

# Setup required Perl Libs

cpan ZMQ
cpan ZMQ::FFI
cpan YAML::XS 
cpan JSON

# Setup required python Libs
# TODO: Proper way to get libs. We should not need sudo?

# Or, we should run as root at all times.
sudo apt-get -y install python3-pip
sudo apt-get install libzmq3-dev



pip3 install python-binance
pip3 install pyzmq

# Setup required aliases

