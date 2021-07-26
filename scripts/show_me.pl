#!/usr/bin/perl
use strict;
use warnings;
use Cwd;


# The Idea for this script is to find a module and connect to it's STDOOUT/STDERR. This is super work in progress
print "Error: Root Permissions Required\n" unless not $>;
exit (-1) unless not $>;
my @args = @ARGV;

system("echo 0 >> /proc/sys/kernel/yama/ptrace_scope");
my $cur_dir = getcwd;
my @output = split ('\n',  `pgrep -laf "python3 $cur_dir/*"`);
#my @output = grep "f_trade" , @output;
my $count = 1;
foreach my $arg (@args) {
    @output = grep "*$_*" =~ $arg, @output;
}

print("We Found:\n");
foreach(@output) {
    print("$_ \n");
}
if (@output == 1) { #length equal 1
    print("We have only found one ouput. Connecting");
    my @split = split (' ',  $output[0]);
    # We need to connect the probe and then disconnect the probe when we are done. DO NOT USE CTRL C
    system("reptyr -s $split[0] >> view");
 }
