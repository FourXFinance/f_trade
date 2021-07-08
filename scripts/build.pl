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
my $step_count = 1;
my $f = "%-30s%-30s\n";
my $system_config = $config->{system};
printf("$f", "Error:" , "No System Entry Defined") and die ("Startup Error")unless $system_config;
my $config_name = $system_config->{name};

printf("$f", "Warn:" , "No System Name Defined") unless $config_name;
$config_name ||= "UNDEFINED";
printf("$f", "System Name:" , $config_name);
my $test_mode = $system_config->{test} // "False";
printf("$f", "Test Mode:" , $test_mode);

my $logs_enabled = $system_config->{logs} // "False";

my $viewer_enabled = $system_config->{viewer} // "False";

my $markets = $config->{markets};
printf("$f", "Error:" , "No Markets Defined") and die ("Startup Error") unless $markets;


printf("$f", "Step $step_count:" , "Checking Markets");
$step_count+=1;

my $market_config = {};
for my $market (@$markets) {
    my $market_name = $market->{name};
    my $market_enabled = $market->{enabled};
    my @temp = $market->{enabled_tick_sources};
    print($temp[0]);
    my $market_tick_sources = map +{$_ => 1}, $market->{enabled_tick_sources};
    print(Dumper($market_tick_sources));
    # Correct Way to get this Array!
}
# Validate Config

# Create Perl Dictionaries of each object

# If Valid, Delete old configs

# Startup each module, they will load data from configs