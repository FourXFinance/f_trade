#!/usr/bin/perl
use strict;
use warnings;
use v5.10;

use ZMQ::FFI;
use ZMQ::FFI::Constants qw(ZMQ_PAIR ZMQ_SUB ZMQ_DONTWAIT);

use TryCatch;
use Time::HiRes qw(usleep);
use Getopt::Std;
use POSIX;
use vars qw($opt_t $opt_m $opt_s $opt_q);

getopts("t:m:sq");

my $target_port = $opt_t;
die "No Target Port Specified" unless $target_port;
my $max_count = $opt_m // 15;

my $context = ZMQ::FFI->new();

my $CONNECTION = $context->socket(ZMQ_PAIR);
$CONNECTION->connect("tcp://127.0.0.1:$target_port");

$CONNECTION->send("PING");
my $iterate_count = -1;
my $was_success = 0;

my $client_name = undef;
usleep(300 * 1000 * 1);
$| = 1; # Clears the IO buffer.
while (1) {

  PROCESS_UPDATE:
	while (1) {
		try {
			my $msg = $CONNECTION->recv(ZMQ_DONTWAIT);
			print($msg."\n") unless defined $opt_s;
			$was_success = 1;
		}catch {
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
			print("Trying Again: ($iterate_count/$max_count)\n") unless defined $opt_s;
		}
		if ($opt_q) {
			usleep(100 * 1000 * 1);
		} else {
			usleep(1000 * 1000 * 1);
		}

	}

}
if ($was_success){
	exit 0;
} else {
	exit 1;
}
