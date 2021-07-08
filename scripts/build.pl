#!/usr/bin/perl
use strict;
use warnings;
use YAML::XS 'LoadFile';
use Data::Dumper;

my ($system_name) = lcfirst shift;

if (not defined $system_name) {
    die "System Name not provided";
}
my $config;
eval  {
    $config = LoadFile("config/$system_name.yaml");
    1;
} or do {
    my $error = $@ || "Zombie Error";
    die "Error Loading System Config: $error";
};


# Validate Config

# Create Perl Dictionaries of each object

# If Valid, Delete old configs

# Startup each module, they will load data from configs