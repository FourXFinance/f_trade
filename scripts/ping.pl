#!/usr/bin/perl
use strict;
use warnings;
use v5.10;

use ZMQ::FFI;
use ZMQ::FFI::Constants qw(ZMQ_PAIR ZMQ_SUB ZMQ_DONTWAIT);

use TryCatch;
use Time::HiRes qw(usleep);

my $target_port = shift;
die "No Target Port Specified" unless $target_port;
my $max_count = shift // 15;

my $context = ZMQ::FFI->new();

my $CONNECTION = $context->socket(ZMQ_PAIR);
$CONNECTION->connect("tcp://127.0.0.1:$target_port");

$CONNECTION->send("PING");
my $iterate_count = -1;
my $was_success = 0;

my $client_name = undef; 

$| = 1; # Clears the IO buffer. 
while (1) {

    PROCESS_UPDATE:
    while (1) {
        try {
            my $msg = $CONNECTION->recv(ZMQ_DONTWAIT);
            print($msg."\n");
            $was_success = 1;
        }
        catch {
            last PROCESS_UPDATE;
        }
    }

    if($was_success){
        last;
    }
    if ($iterate_count == $max_count) {
        #We Timeout!
        last;
    } else {
        
        $iterate_count +=1;
        if($iterate_count > 0){
            print("Trying Again: ($iterate_count/$max_count)\n");
        }
        
        usleep(1000 * 1000 * 1);
    }
    
}
if ($iterate_count == $max_count) {
    print("tcp://127.0.0.1:$target_port is Not Responding\n");
    exit;
} else {
    print("tcp://127.0.0.1:$target_port is Alive\n");
    exit 1;
}
