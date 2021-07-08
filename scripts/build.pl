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
    $config = LoadFile("config/system/$system_name.yaml");
    1;
} or do {
    my $error = $@ || "Zombie Error";
    die "Error Loading System Config: $error";
};
my $system_config = $config->{system};
printf("%-30s%30s\n", "Error: " , "No System Entry Defined") and die("Startup Error")unless $system_config;
my $config_name = $system_config->{name};

printf("%-30s%30s\n", "Warn: " , "No System Name Defined") unless $config_name;
$config_name ||= "UNDEFINED";
printf("%-30s%30s\n", "Setting Up: " , $config_name);

# Validate Config

# Create Perl Dictionaries of each object

# If Valid, Delete old configs

# Startup each module, they will load data from configs