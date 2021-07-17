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

use vars qw($opt_n);

getopts("n:");

print "Error: Root Permissions Required\n" unless not $>;
exit (-1);
my $enable_debug = 0;
my $target_node = defined $opt_n ? $opt_n : undef;
my $cur_dir = getcwd;

my @shutdown_libs = ('module', 'algorithm');
for my $lib (@shutdown_libs) {
    my @found_modules = split ('\n',  `pgrep -laf "python3 $cur_dir/$lib/*"`);
    foreach(@found_modules) {
        print("DEBUG: ".$_."\n") if $enable_debug;
        my @split_module = split(" ", $_);
        next unless $split_module[1] eq "python3";
        my $module_pid = $split_module[0];
        my $res = `kill -15 $module_pid`;
    }
}
