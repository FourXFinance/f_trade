#!/usr/bin/perl
use strict;
use warnings;
use Cwd;
my $cur_dir = getcwd;
system("tmux -2 -f $cur_dir/config/f_trade/tmux.conf");

