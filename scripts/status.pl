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

my @market_modules;
my @manager_modules;
my @ticker_modules;
my @algorithm_modules;
my @proxy_modules;
my @account_modules;
my @broker_modules;
my @trader_modules;
print (color('bold red'));
print(localtime()."\n");
print(color('bold blue'));

my @found_modules = split ('\n',  `pgrep -laf "python3 $cur_dir/*"`);
print("The Following F Trader System Nodes exist:\n") if @found_modules > 1;
unless (@found_modules > 1) {
    print("No F Trader System Nodes are Running\n");
    exit();
}
push @market_modules , grep(/\/market.py/, @found_modules);
push @manager_modules , grep(/\/manager.py/, @found_modules);
push @ticker_modules , grep(/\/ticker.py/, @found_modules);
push @algorithm_modules , grep(/\/algorithm/, @found_modules);
push @account_modules , grep(/\/account.py/, @found_modules);
push @proxy_modules , grep(/\/proxy.py/, @found_modules);
push @broker_modules , grep(/\/broker.py/, @found_modules);
push @trader_modules , grep(/\/trader.py/, @found_modules);


print("\n")  if @market_modules;
print(color('bold blue'));
print("Market Nodes Running:\n") if @market_modules;
print(color('bold white'));
foreach(@market_modules) {        
    my @split_module = split(" ", $_);
    next unless $split_module[1] eq "python3";
    print("".$_."\n");
}

print("\n") if @manager_modules;
print(color('bold blue'));
print("Manager Nodes Running:\n") if @manager_modules;
print(color('bold white'));
foreach(@manager_modules) {        
    my @split_module = split(" ", $_);
    next unless $split_module[1] eq "python3";
    print("".$_."\n");
}

print("\n") if @ticker_modules; 
print(color('bold blue'));
print("Ticker Nodes Running:\n") if @ticker_modules;
print(color('bold white'));
foreach(@ticker_modules) {        
    my @split_module = split(" ", $_);
    next unless $split_module[1] eq "python3";
    print("".$_."\n");
}

print("\n") if @algorithm_modules;
print(color('bold blue'));
print("Algorithm Nodes Running:\n") if @algorithm_modules;
print(color('bold white'));
foreach(@algorithm_modules) {        
    my @split_module = split(" ", $_);
    next unless $split_module[1] eq "python3";
    print("".$_."\n");
}

print("\n") if @proxy_modules;
print(color('bold blue'));
print("Proxy Nodes Running:\n") if @proxy_modules;
print(color('bold white'));
foreach(@proxy_modules) {        
    my @split_module = split(" ", $_);
    next unless $split_module[1] eq "python3";
    print("".$_."\n");
}


print("\n") if @account_modules;
print(color('bold blue'));
print("Account Nodes Running:\n")  if @account_modules;
print(color('bold white'));
foreach(@account_modules) {        
    my @split_module = split(" ", $_);
    next unless $split_module[1] eq "python3";
    print("".$_."\n");
}


print("\n") if @broker_modules;
print(color('bold blue'));
print("Broker Nodes Running:\n") if @broker_modules;
print(color('bold white'));
foreach(@broker_modules) {        
    my @split_module = split(" ", $_);
    next unless $split_module[1] eq "python3";
    print("".$_."\n");
}

print("\n") if @trader_modules;
print(color('bold blue'));
print("Trader Nodes Running:\n") if @trader_modules;
print(color('bold white'));
foreach(@trader_modules) {        
    my @split_module = split(" ", $_);
    next unless $split_module[1] eq "python3";
    print("".$_."\n");
}
