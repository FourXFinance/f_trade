#!/usr/bin/perl
use strict;
use warnings;
use Cwd;
use Term::ANSIColor;

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

#print("We Found:\n");
#foreach(@output) {
#    print("$_ \n");
#}
if (@output == 1) { #length equal 1
    print color('bold green');
    print("We have only found one ouput. Connecting to:\n");
    print color('bold yellow');
    print($output[0]."\n");
    my @split = split (' ',  $output[0]);
    # We need to connect the probe and then disconnect the probe when we are done. DO NOT USE CTRL C
    # TODO: Move to seperate function
    system("reptyr -s $split[0] >> view");
 } elsif (@output >= 1) {
     print color('bold red');
     print("Muliple Outputs have been detected. Select a Number to connect:\n");
     my $count = 0;
     my $mapping = {};
     foreach (@output) {
         $count+=1;
         print color('reset');
         print("[");
         print color('bold green');
         print("$count");
         print color('reset');
         print("]\t");
         print($_);
         print("\n");
         $mapping->{$count} = $_; 
         
     }
    my $choice = <STDIN>;
    chomp $choice;
    # TODO: Check that User Choice is less than count
    # Execute Connection 
 } else {
     print color('bold red');
     print("No Modules Found with Search Criteria\n");
 }
