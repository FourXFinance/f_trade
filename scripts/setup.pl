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


my $module_data = delete $config->{modules};
die "No Module Data Found" unless $module_data;
my $ticker_data = delete $config->{tickers};
die "No Ticker Data Found" unless $ticker_data;
$system_name = ucfirst $system_name;
my $version = $config->{version};
my $test_mode = $config->{test};

# Algorithm config entries
my $algorithm_base_port = $config->{algorithm_base_port};
my $algorithm_port_increment = $config->{algorithm_port_increment};
my $algorithm_proxy_offset = $config->{algorithm_port_increment};
my $algorithm_account_offset = $config->{algorithm_account_offset};


print "Loading Config for $system_name Version: $version\n";
print "Test Mode: $test_mode\n";

my $market;

my $module_config;
my $ticker_config;
my $algorithm_config;
foreach (@$module_data) {
    
    my $module_name = $_->{name};
    die "No Module Name Defined" unless $module_name;

    if ($module_name eq "market") {
        $market = $_; 
        next;
    }
    #print Dumper($_);
    my $ds = $_->{downstream};
    my @module_downstream = ();
    
    foreach my $downstream (@$ds){
        my $ds_name = $downstream->{name};
        die "$module_name Downstream - No Port Name Defined" unless $ds_name;
        my $ds_port = $downstream->{port};
        die "$module_name No Port Defined For $ds_name" unless $ds_port;
        my $ds_type = $downstream->{type};
        my $ds_bind = $downstream->{bind} // "False";
        push @module_downstream, {  name => $ds_name,
                                    port => $ds_port,
                                    type => $ds_type,
                                    bind => $ds_bind
                                    };
    };
    print Dumper(\@module_downstream);
    my @module_upstream = ();
    my $us = $_->{upstream};
     foreach my $upstream (@$us){
        my $us_name = $upstream->{name};
        die "$module_name Upstream - No Port Name Defined" unless $us_name;
        my $us_port = $upstream->{port};
        die "$module_name No Port Defined For $us_name" unless $us_port;
        my $us_type = $upstream->{type};
        my $us_bind = $upstream->{bind} // "False";
        push @module_upstream, {    name => $us_name,
                                    port => $us_port,
                                    type => $us_type,
                                    bind => $us_bind
                                    };
    };
    print Dumper(\@module_upstream);
    $module_config->{$module_name} = {
        name => $module_name,
        downstream => \@module_downstream,
        upstream => \@module_upstream,
    };
}
print Dumper($module_config);
die "No Market Module Defined" unless $market;

my $current_port_address = $algorithm_base_port;
foreach (@$ticker_data) {
    my $ticker_name = $_->{name};
    my $supported_ticks = $_->{supported_ticks};
    my $enabled = $_->{enabled};
    next unless defined $enabled and $enabled;
    my $ticker_algorithms = $_->{algorithms};

    # Pass all the required algorithm nodes
    foreach my $algorithm (@$ticker_algorithms) {
        my $a_name = $algorithm->{name};
        my $enabled = $algorithm->{enabled};
        next unless defined $enabled and $enabled;
        my $parameters = $algorithm->{parameters};
        if (defined $algorithm_config->{$ticker_name} and defined $algorithm_config->{$ticker_name}->{$a_name}) {
            die "$ticker_name has two or more entries for $a_name";
        }
        $algorithm_config->{$ticker_name}->{$a_name} = {
            name => $a_name,
            parameters => $parameters,
            upstream => [{
                port => $current_port_address,
                bind => "False",
                type => "SUB",
                name => "$ticker_name.$a_name.US"
            }],
            downstream => [{
                port => $current_port_address + $algorithm_proxy_offset
                bind => "False",
                type => "PUB",
                name => "$ticker_name.$a_name.DS"
            }]

        };
    }
    $ticker_config->{ticker_name} = {
        
    };
    $current_port_address+=$algorithm_port_increment;
}
print Dumper($algorithm_config);