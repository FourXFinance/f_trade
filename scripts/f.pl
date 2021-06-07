#!/usr/bin/perl

# This script will send requests to the executive python node
use strict;
use warnings;
use v5.10;

use ZMQ::FFI;
use ZMQ::FFI::Constants qw(ZMQ_PULL ZMQ_SUB ZMQ_DONTWAIT);

use TryCatch;
use Time::HiRes qw(usleep);

my $context = ZMQ::FFI->new();

my $subscriber = $context->socket(ZMQ_SUB);
$subscriber->connect('tcp://localhost:5556');
$subscriber->subscribe('0');

print("Connecting\n")