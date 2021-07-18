#!/usr/bin/perl
use strict;
use warnings;
use Cwd;

print "Error: Root Permissions Required\n" unless not $>;
exit (-1) unless not $>;

my $cur_dir = getcwd;
system("tmux -2 -f $cur_dir/config/f_trade/tmux.conf");

# The Idea for this script is 