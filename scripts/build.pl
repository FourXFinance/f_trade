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
my $sub_count = 1;
my $sub_sub_count = 1;
my $node_delay = 0.3;
my $f = "%-30s%-30s\n";


# Validate System Config
my $system_config = $config->{system};
printf("$f", "Error:" , "No System Entry Defined") and die ("Startup Error")unless $system_config;
my $config_name = $system_config->{name};

printf("$f", "Warn:" , "No System Name Defined") unless $config_name;
$config_name ||= "UNDEFINED";
printf("$f", "System Name:" , $config_name);
my $test_mode = $system_config->{test} // "False";
printf("$f", "Test Mode:" , $test_mode);

my $logs_enabled = $system_config->{logs} // "False";
printf("$f", "Logs Enabled:" , $logs_enabled);

my $viewer_enabled = $system_config->{viewer} // "False";
printf("$f", "Viewer Enabled:" , $viewer_enabled);

my $markets = $config->{markets};
printf("$f", "Error:" , "No Markets Defined") and die ("Startup Error") unless $markets;


printf("$f", "Step $step_count:" , "Checking Market Configurations");

my $market_config = {};
for my $market (@$markets) {
    my $market_enabled = $market->{enabled};
    next if $market_enabled eq "False";
    my $market_name = $market->{name};
    my $temp = $market->{enabled_tick_sources};
    my @market_tick_sources = ();
    for my $tick (@$temp) { 
        push @market_tick_sources, $tick;
    }
    $market_config->{$market_name} = {
        name => $market_name,
        sources => \@market_tick_sources
    };
    printf("$f", "Step $step_count.$sub_count:" , "Market '$market_name' has valid Configuration");
    $sub_count+=1;
}
$sub_count=1;
$step_count+=1;

my $tickers = $config->{tickers};
printf("$f", "Error:" , "No Tickers Defined") and die ("Startup Error") unless $tickers;


printf("$f", "Step $step_count:" , "Checking Ticker Configuration");
my $ticker_config = {};
for my $ticker (@$tickers) {
    my $ticker_enabled = $ticker->{enabled};
    next if $ticker_enabled eq "False";
    my $ticker_name = $ticker->{name};
    my $ticker_algorithms = $ticker->{algorithms};
    for my $algorithm (@$ticker_algorithms){
        my $algorithm_enabled = $algorithm->{enabled};
        next if $algorithm_enabled eq "False";
        printf("$f", "Step $step_count.$sub_count.$sub_sub_count:" , "Checking Algorithm Configuration");
        my $algorithms = $ticker->{algorithms};
        printf("$f", "Error:" , "No Algorithms Defined") and die ("Startup Error") unless $algorithms;
        $sub_sub_count+=1;
    }
    printf("$f", "Step $step_count  .$sub_count:" , "Ticker $ticker_name has valid Configuration");
    $sub_sub_count = 1;
    $sub_count+=1;
    
}
$sub_count=1;

printf("$f", "Success:" , "System Config is Valid");
# Create Perl Dictionaries of each object

# If Valid, Delete old configs

# Startup each module, they will load data from configs
sleep($node_delay);
#TODO: Communicate Directly With Node to get Status. Then Move onto next node

