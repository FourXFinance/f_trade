#!/usr/bin/perl
use strict;
use warnings;
use YAML::XS 'LoadFile';
use JSON;
use Data::Dumper;

my ($system_name) = lcfirst shift;

if (not defined $system_name) {
    die "System Name not provided";
}
my $config;
my $system_config = {};
my $ticker_config = {};
my $algorithm_config = {};
my $proxy_config = {};
my $account_config = {};
my $trader_config = {};
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
$system_config= $config->{system};
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

my $base_ticker_port = $system_config->{base_ticker_port};
printf("$f", "Error:" , "No Base Ticker Port Defined") and die ("Startup Error") unless $base_ticker_port;

my $base_ticker_offset = $system_config->{base_ticker_offset};
printf("$f", "Error:" , "No Base Ticker Offset Defined") and die ("Startup Error") unless $base_ticker_offset;

my $algorithm_offset = $system_config->{algorithm_offset};
printf("$f", "Error:" , "No Algorithm Offset Defined") and die ("Startup Error") unless $algorithm_offset;


my $algorithm_proxy_offset = $system_config->{algorithm_proxy_offset};
printf("$f", "Error:" , "No Algorithm Proxy Offset Defined") and die ("Startup Error") unless $algorithm_proxy_offset;

my $account_offset = $system_config->{account_offset};
printf("$f", "Error:" , "No Account Offset Defined") and die ("Startup Error") unless $account_offset;

my $broker_port = $system_config->{broker_port};
printf("$f", "Error:" , "No Broker Port Defined") and die ("Startup Error") unless $broker_port;

my $logger_port = $system_config->{logger_port};
printf("$f", "Error:" , "No Logger Port Defined") and die ("Startup Error") unless $logger_port;



printf("$f", "Base Ticker Port (Offset):" , $base_ticker_port." (".$base_ticker_offset.")");


my $markets = $config->{markets};
printf("$f", "Error:" , "No Markets Defined") and die ("Startup Error") unless $markets;


printf("$f", "Step $step_count:" , "Checking Market Configurations");
my $current_ticker_port = $base_ticker_port;
my $current_algorithm_proxy_port = $base_ticker_port + $algorithm_proxy_offset;
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

for my $ticker (@$tickers) {
    my $ticker_enabled = $ticker->{enabled};
    next if $ticker_enabled eq "False";
    my $ticker_name = $ticker->{name};
    my $ticker_algorithms = $ticker->{algorithms};
    my $required_sources = {};
    if (not defined $ticker->{required_data}) {
        foreach my $key (keys % {$market_config}){
            $required_sources->{$key} = $market_config->{$key}->{sources};
        }
    } else {
        #TODO Handle Custom Tick Sources.
    }
    $ticker_config->{$ticker_name} = {
        name => $ticker_name,
        upstream_root_port => $current_ticker_port,
        required_sources => $required_sources,
        algorithm_port => $current_ticker_port + $algorithm_offset,
    };
    my $current_algorithm_port = $current_ticker_port + 1;
    printf("$f", "Step $step_count.$sub_count:" , "Checking Algorithm Configuration for $ticker_name");
    for my $algorithm (@$ticker_algorithms){
        my $algorithm_enabled = $algorithm->{enabled};
        next if $algorithm_enabled eq "False";
        my $algorithm_name = $algorithm->{name};
        my $config = $algorithm->{config};
        if (defined $algorithm_config->{$ticker_name} and defined $algorithm_config->{$ticker_name}->{$algorithm_name}) {
            printf("$f", "Error:" , "Algorithm $algorithm_name already defined for $ticker_name") and die ("Startup Error")
        }
        $algorithm_config->{$ticker_name}->{$algorithm_name} = {
            algorithm_port => $current_ticker_port, #TODO: Figure out what to do with this?
            algorithm_name => $algorithm_name,
            configuration_options => $config,
            proxy_port => $current_algorithm_proxy_port
        };
        $current_algorithm_port+=1;
    }
    $proxy_config->{$ticker_name} = {
        algorithm_proxy_port => $current_ticker_port + $algorithm_proxy_offset,
        account_proxy_port => $current_ticker_port + $account_offset,
    };
    $account_config->{$ticker_name} = {
        account_proxy_port => $current_ticker_port + $account_offset,
        broker_port => $broker_port,
    };
    $sub_count+=1;
    $current_algorithm_proxy_port += $base_ticker_offset;
    $current_ticker_port += $base_ticker_offset;
    
}
$sub_count=1;
# print(Dumper($algorithm_config));
# print(Dumper($ticker_config));
# print(Dumper($market_config));
# printf("$f", "Success:" , "System Config is Valid");
# Create Perl Dictionaries of each object

# If Valid, Delete old configs
qx\rm -rf ./config/generated/$system_name/\;
qx\mkdir ./config/generated/$system_name\;
# if ($? >> 8) {
#     printf("$f", "WARN:" , "It seems an old instance of the system config exists. Deleting");
#     qx\rm -rf ./config/generated/$system_name/\;
#     qx\mkdir ./config/generated/$system_name\;
# }

$step_count+=1;
printf("$f", "Step $step_count:" , "Creating F_Trader System");
printf("$f", "Step $step_count.$sub_count:" , "Writting Node Configs");

# Build Market Configs
qx\mkdir ./config/generated/$system_name/market/\;
for my $market_name  (keys %$market_config) {
    my $market = $market_config->{$market_name};
    my $json = encode_json $market;
    qx\touch ./config/generated/$system_name/market/$market_name.json\;
    open(FH, '>', "./config/generated/$system_name/market/$market_name.json") or die $!;
    print FH $json;
    close(FH);
}


# Build Ticker Configs
qx\mkdir ./config/generated/$system_name/ticker/\;
for my $module_name  (keys %$ticker_config) {
    my $module = $ticker_config->{$module_name};
    my $json = encode_json $module;
    qx\touch ./config/generated/$system_name/ticker/$module_name.json\;
    open(FH, '>', "./config/generated/$system_name/ticker/$module_name.json") or die $!;
    print FH $json;
    close(FH);
}

# Build Algorithm Configs
qx\mkdir ./config/generated/$system_name/algorithm/\;
for my $ticker_name  (keys %$algorithm_config) {
    qx\mkdir ./config/generated/$system_name/algorithm/$ticker_name/\;
    for my $algorithm_name (keys %{$algorithm_config->{$ticker_name}}) {
        my $algorithm = $algorithm_config->{$ticker_name}->{$algorithm_name};
        my $json = encode_json $algorithm;
        qx\touch ./config/generated/$system_name/algorithm/$ticker_name/$algorithm_name.json\;
        open(FH, '>', "./config/generated/$system_name/algorithm/$ticker_name/$algorithm_name.json") or die $!;
        print FH $json;
        close(FH);
    }
}

# Build Proxy Configs
qx\mkdir ./config/generated/$system_name/proxy/\;
for my $proxy_name  (keys %$proxy_config) {
    my $proxy = $proxy_config->{$proxy_name};
    my $json = encode_json $proxy;
    qx\touch ./config/generated/$system_name/proxy/$proxy_name.json\;
    open(FH, '>', "./config/generated/$system_name/proxy/$proxy_name.json") or die $!;
    print FH $json;
    close(FH);
}

# Build Account Configs
qx\mkdir ./config/generated/$system_name/account/\;
for my $account_name  (keys %$account_config) {
    my $account = $account_config->{$account_name};
    my $json = encode_json $account;
    qx\touch ./config/generated/$system_name/account/$account_name.json\;
    open(FH, '>', "./config/generated/$system_name/account/$account_name.json") or die $!;
    print FH $json;
    close(FH);
}
return;
$sub_count+=1;
# Startup Order:
# Create Markets
# Create 
# Create Tickers
# Add Algorithms to Tickers
# Create Accounts

# Startup each module, they will load data from configs

# TODO: Check if We want to overwrite the old configs
$sub_count=1;
$step_count+=1;
printf("$f", "Step $step_count" , "Starting Up F_Trader System");
 # How Does the system start up? Quite Simple.

 # 1. Start a module
 # 2. Ping a module for liveliness using ping.pl


#TODO: Communicate Directly With Node to get Status. Then Move onto next node

