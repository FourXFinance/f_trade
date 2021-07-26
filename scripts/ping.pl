#!/usr/bin/perl
use strict;
use warnings;
use v5.10;

use ZMQ::FFI;
use ZMQ::FFI::Constants qw(ZMQ_PUB ZMQ_SUB ZMQ_DONTWAIT);

use TryCatch;
use Time::HiRes qw(usleep);

# Connect to task ventilator
my $context = ZMQ::FFI->new();
#my $receiver = $context->socket(ZMQ_PUB);
#$receiver->connect('tcp://localhost:5557');

# Connect to weather server
my $subscriber = $context->socket(ZMQ_SUB);
$subscriber->connect('tcp://127.0.0.1:11000');
$subscriber->subscribe('0');

# Process messages from both sockets
# We prioritize traffic from the task ventilator

my $iterate_count = 0;
my $was_success = 0;
my $max_count = 15;
$| = 1;
while (1) {

    PROCESS_UPDATE:
    while (1) {
        try {
            my $msg = $subscriber->recv(ZMQ_DONTWAIT);
            $was_success = 1;
        }
        catch {
            last PROCESS_UPDATE;
        }
    }

    # No activity, so sleep for 1 msec
    if($was_success){
        last;
    }
    if ($iterate_count == $max_count) {
        #We Timeout!
        last;
    } else {
        
        $iterate_count +=1;
        print("Trying Again: ($iterate_count/$max_count)\n");
        sleep(1);
    }
    
}
print("Result: $was_success ($iterate_count)\n");