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
use Term::ANSIColor;
use vars qw($opt_n $opt_a);

getopts("n:a:");



my $enable_debug = 0;
my $target_node = defined $opt_n ? $opt_n : undef;
my @libs;

my $cur_dir = getcwd;
#print (color('bold red'));
# print(localtime()."\n");
#print(color('bold blue'));

my $module_count = int(`pgrep -lafc "python3 /home/warrenf/git_tree/f_trade/*"`)-1; # There is one Extra for some unknown reason
if ($module_count > 0) {
    print("F:");
    print($module_count); 
} else {
    print("Offline");
}

