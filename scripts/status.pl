#!/usr/bin/perl

# This script will Send SIGINT requests to all Algorithms and All Nodes.
# This will cause all computationaly modules to exit

use strict;
use warnings;

use lib;
use JSON;

use Data::Dumper;
use Getopt::Std;
use Cwd;

use vars qw($opt_n $opt_a);

getopts("n:a:");

print "Error: Root Permissions Required\n" unless not $>;
exit (-1) unless not $>;


my $enable_debug = 0;
my $target_node = defined $opt_n ? $opt_n : undef;
my @libs;
if ($opt_a) {
    @libs= ( 'algorithm');
} else {
    @libs= ('module', 'algorithm');
}
my $cur_dir = getcwd;
print("The Following F Trader System Nodes exist:\n");
for my $lib (@libs) {
    my @found_modules = split ('\n',  `pgrep -laf "python3 $cur_dir/$lib/*"`);
    my @market_modules = grep $_ ~~ "*market*", @found_modules;
    foreach(@found_modules) {        
        my @split_module = split(" ", $_);
        next unless $split_module[1] eq "python3";
        print("".$_."\n");
    }
}
