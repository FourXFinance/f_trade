#!/usr/bin/perl

# This script builds the f_trader system
# But how does it build it?
# First we check to make sure a config for the system specified exists
# Then we check the validity of the config (This can be improved with a hashmap)
# Then we build a logical hash of the system ports
# Then we write these hashes as configs for each node to read
# Then we start up each node
# Then we ping each node to make sure they pass startup check (Nifty!)
# TODO: After this is done we then start the executive node (Who then takes over)
#
#
# Usage: 
# -t to specify test mode
# -s [SYSTEM_NAME] specifies which system we are building.
use strict;
use warnings;
use YAML::XS 'LoadFile';
use JSON;
use Data::Dumper;
use Term::ANSIColor;
use Cwd;
use Storable 'dclone';
use Getopt::Std;
use vars qw($opt_t $opt_s $opt_d);
getopts("ts:d");

my $std_tty = 'null';
my $std_err_tty = 'null';
my $cur_dir = getcwd;
my $system_name = undef;
my $dry_run = defined $opt_d;
# Format String. Makes things pretty.
my $f = "%-40s%30s\n";

if (defined $opt_t){
	print color('magenta');
	print ("Test Mode Enabled\n");
	$std_tty = 'tty';
	$std_err_tty = 'tty';
}

if (defined $opt_s){
	$system_name = $opt_s;
} else {
	die "System Name not provided";
}


sub ping_node {
	my $target_node_port = shift;
	my $target_node_name = shift;
	print color('green');
	system("perl $cur_dir/scripts/ping.pl -s -t $target_node_port -m 15");
	if ($? >> 8) {
		print color('red');
		print "Failed Heartbeat: $target_node_name ($target_node_port)\n";
		exit(-1);
	} else {
		print "Succesful Heartbeat: $target_node_name ($target_node_port)\n";
	}
}
# Configs for each node 'type'
my $config;
my $system_config = {};
my $ticker_config = {};
my $algorithm_config = {};
my $proxy_config = {};
my $account_config = {};
my $trader_config = {};
my $manager_config = {};

# STEP 1: Load the Config of the specified system. or Die
eval  {
	$config = LoadFile("config/system/$system_name.yaml");
	1;
} or do {
	my $error = $@ || "Zombie Error";
	die "Error Loading System Config: $error";
};
system("perl $cur_dir/scripts/shutdown.pl");

# STEP 2: Validate System Config
$system_config= $config->{system};


if (defined $system_config->{override_system_name}) {

	print color('bold red');
	print("Overriden System name from $system_name to ");
	$system_name = $system_config->{override_system_name};
	print("$system_name \n");
}
print color('reset');

#print color('bold magenta');
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

my $base_market_port = $system_config->{base_market_port};
printf("$f", "Error:" , "No Base Market Port Defined") and die ("Startup Error") unless $base_market_port;

my $base_market_offset = $system_config->{base_market_offset};
printf("$f", "Error:" , "No Base Market Offset Defined") and die ("Startup Error") unless $base_market_offset;

my $base_ticker_port = $system_config->{base_ticker_port};
printf("$f", "Error:" , "No Base Ticker Port Defined") and die ("Startup Error") unless $base_ticker_port;

my $base_ticker_offset = $system_config->{base_ticker_offset};
printf("$f", "Error:" , "No Base Ticker Offset Defined") and die ("Startup Error") unless $base_ticker_offset;

my $base_algorithm_port = $system_config->{base_algorithm_port};
printf("$f", "Error:" , "No Base Algorithm Port Defined") and die ("Startup Error") unless $base_algorithm_port;

my $algorithm_offset = $system_config->{algorithm_offset};
printf("$f", "Error:" , "No Algorithm Offset Defined") and die ("Startup Error") unless $algorithm_offset;

my $algorithm_proxy_offset = $system_config->{algorithm_proxy_offset};
printf("$f", "Error:" , "No Algorithm Proxy Offset Defined") and die ("Startup Error") unless $algorithm_proxy_offset;

my $account_offset = $system_config->{account_offset};
printf("$f", "Error:" , "No Account Offset Defined") and die ("Startup Error") unless $account_offset;

my $logger_port = $system_config->{logger_port};
printf("$f", "Error:" , "No Logger Port Defined") and die ("Startup Error") unless $logger_port;

my $broker_proxy_port = $system_config->{broker_proxy_port};
printf("$f", "Error:" , "No Broker Proxy Port Defined") and die ("Startup Error") unless $broker_proxy_port;

my $trader_proxy_port = $system_config->{trader_proxy_port};
printf("$f", "Error:" , "No Trader Proxy Port Defined") and die ("Startup Error") unless $trader_proxy_port;

printf("$f", "Base Ticker Port (Offset):" , $base_ticker_port." (".$base_ticker_offset.")");

my $heartbeat_base_port = $system_config->{heartbeat_base_port};
printf("$f", "Error:" , "No Heart Beat Server Port Defined") and die ("Startup Error") unless $heartbeat_base_port;

my $markets = $config->{markets};
printf("$f", "Error:" , "No Markets Defined") and die ("Startup Error") unless $markets;

# STEP 3: Build logical System
my $current_ticker_port = $base_ticker_port;
my $current_algorithm_port = $base_algorithm_port;
my $current_market_base = $base_market_port;
my $current_algorithm_proxy_port = $base_algorithm_port + $algorithm_proxy_offset;
my $current_heartbeat_port = $heartbeat_base_port;
my $market_config = {};
my $heartbeat_config = {};
for my $market (@$markets) {
	my $current_market_port = $current_market_base;
	my $market_enabled = $market->{enabled};
	next if $market_enabled eq "False";
	my $market_name = lc $market->{name};
	my $temp = $market->{enabled_tick_sources};
	my $market_socket_bindings = {};
	my $market_heartbeat_ports = {};
	my @market_tick_sources = ();

	for my $tick (@$temp) {
		push @market_tick_sources, $tick;
		$market_socket_bindings->{$tick} = $current_market_port;
		$current_market_port +=1;
		$market_heartbeat_ports->{$tick} = $current_heartbeat_port;
		$current_heartbeat_port+=1;
	}
	$market_config->{$market_name} = {
		name => $market_name,
		sources => $market_socket_bindings,
		tracked_tickers => [],
		heartbeat_port => $market_heartbeat_ports
	};

	$current_market_base += $base_market_offset;

	#printf("$f", "Step $step_count.$sub_count:" , "Market '$market_name' has valid Configuration");

}
my $tickers = $config->{tickers};
printf("$f", "Error:" , "No Tickers Defined") and die ("Startup Error") unless $tickers;

my $ticker_count = 0;
my $topic = 0;


$manager_config->{heartbeat_port} = $current_heartbeat_port;
$current_heartbeat_port+=1;
for my $ticker (@$tickers) {
	my $ticker_enabled = $ticker->{enabled};
	next if $ticker_enabled eq "False";
	my $ticker_name = $ticker->{name};
	my $ticker_algorithms = $ticker->{algorithms};
	my $required_sources = {};
	if (not defined $ticker->{required_data}) {
		foreach my $key (keys % {$market_config}){
			$required_sources->{$key} = dclone $market_config->{$key}->{sources};
			foreach(keys %{$required_sources->{$key}}) {

				# TODO: Whateber nightmare this is. Fix it
				# print($base_ticker_offset * $ticker_count);
				# This can 100% be done better
				$required_sources->{$key}->{$_} += ($base_ticker_port - $base_market_port) + ($base_ticker_offset * $ticker_count);
			}
		}
	} else {

		#TODO Handle Custom Tick Sources.
	}
	$ticker_config->{$ticker_name} = {
		name => $ticker_name,
		upstream_root_port => $current_ticker_port,
		required_sources => $required_sources,
		algorithm_port => $current_algorithm_port,
		heartbeat_port => $current_heartbeat_port,
	};

	#TODO: Handle Different Markets with Different Tickers
	$current_heartbeat_port+=1;
	push @{$market_config->{$system_name}->{tracked_tickers}}, {$ticker_name => $topic};
	$topic+=1;
	for my $algorithm (@$ticker_algorithms){
		my $algorithm_enabled = $algorithm->{enabled};
		next if $algorithm_enabled eq "False";
		my $algorithm_name = $algorithm->{name};
		my $config = $algorithm->{config};
		if (defined $algorithm_config->{$ticker_name} and defined $algorithm_config->{$ticker_name}->{$algorithm_name}) {
			printf("$f", "Error:" , "Algorithm $algorithm_name already defined for $ticker_name") and die ("Startup Error");
		}

		my @available_tick_sources = keys %{$ticker_config->{$ticker_name}->{required_sources}->{$system_name}};
		$algorithm_config->{$ticker_name}->{$algorithm_name} = {
			algorithm_port => $current_algorithm_port, #TODO: Figure out what to do with this?
			algorithm_name => $algorithm_name,
			configuration_options => $config,
			proxy_port => $current_algorithm_proxy_port,
			heartbeat_port => $current_heartbeat_port,
			available_ticker_sources => \@available_tick_sources,
		};

		$current_heartbeat_port+=1;

		# $current_algorithm_port+=1;
	}

	$proxy_config->{$ticker_name} = {
		algorithm_proxy_port => $current_algorithm_port + $algorithm_proxy_offset,
		account_proxy_port => $current_algorithm_port + $account_offset,
	};
	$account_config->{$ticker_name} = {
		account_proxy_port => $current_algorithm_port + $account_offset,
		broker_proxy_port => $broker_proxy_port,
		heartbeat_port => $current_heartbeat_port,
	};
	$current_heartbeat_port+=1;

	$current_algorithm_proxy_port += $base_ticker_offset;
	$current_ticker_port += $base_ticker_offset;
	$current_algorithm_port += $base_ticker_offset;
	$ticker_count +=1;
}
#print(Dumper($algorithm_config));
# A this tage the system is 'valid'. We now conver these hash maps into json config files for our nodes to load
# Delete Old Configs
#
# STEP 4: Write the configs for each node
# TODO: Put in a flag for no-delete
qx\rm -rf ./config/generated\;
qx\mkdir ./config/generated/\;
qx\mkdir ./config/generated/$system_name\;

# Build Manager Configs
qx\mkdir ./config/generated/$system_name/manager/\;
my $manager = $manager_config;
my $json = encode_json $manager;
qx\touch ./config/generated/$system_name/manager/manager.json\;
open(FH, '>', "./config/generated/$system_name/manager/manager.json") or die $!;
print FH $json;
close(FH);

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

# Build Broker Configs
qx\mkdir ./config/generated/$system_name/broker/\;
my $broker_config = {
	broker_proxy_port => $broker_proxy_port,
	trader_proxy_port => $trader_proxy_port
};
$json = encode_json $broker_config;
qx\touch ./config/generated/$system_name/broker/$system_name.json\;
open(FH, '>', "./config/generated/$system_name/broker/$system_name.json") or die $!;
print FH $json;
close(FH);


# Build Trader Configs
qx\mkdir ./config/generated/$system_name/trader/\;
$trader_config = {
	trader_proxy_port => $trader_proxy_port,
	heartbeat_port => $current_heartbeat_port
};
$json = encode_json $trader_config;
qx\touch ./config/generated/$system_name/trader/$system_name.json\;
open(FH, '>', "./config/generated/$system_name/trader/$system_name.json") or die $!;
print FH $json;
close(FH);

exit 0 if $dry_run;

# STAGE 5: Start Each Node and Ping them to see if they are alive.
# At this stage, all the configuration files (.json) have been created and written to disk. Start each node and ping them
print color('bold yellow');
print("Starting Market Nodes\n");
foreach (keys %$market_config) {
	my $market_name = $_;
	my $market_sources = $market_config->{$_}->{sources};
	my $market_heartbeat =$market_config->{$_}->{heartbeat_port};

	foreach (keys %$market_sources) {
		print color('bold blue');
		print("Starting: $market_name ($_) ");
		my $pid=fork();
		die "Cannot fork: $!" if (! defined $pid);
		if (! $pid) {

			# Only the child does this
			setpgrp;
			eval{
				exec("python3 $cur_dir/module/system/$market_name/market.py $system_name $market_name $_ >> /dev/$std_tty 2>> /dev/$std_err_tty &");
				exit(); # < Technically not possible to reach
				 # NO EXECUTION BELOW THIS POINT!
			};
		} else {

			# Only The Parent Does This.
			ping_node($market_heartbeat->{$_}, "$system_name.$market_name.$_");
		}
	}
}

print color('green');

#print ("All Markets have Started\n");
print("\n");
print color('bold yellow');
print ("Starting Manager Node\n");
print color('bold blue');
print("Starting: Manager ");

my $pid=fork();
die "Cannot fork: $!" if (! defined $pid);
if (! $pid) {

	# Only the child does this
	setpgrp;
	eval{
		exec("python3 $cur_dir/module/manager.py $system_name  >> /dev/$std_tty 2>> /dev/$std_err_tty &");
		exit(); # < Technically not possible to reach
		 # NO EXECUTION BELOW THIS POINT!
	};
} else {

	# Only The Parent Does This.
	ping_node($manager_config->{heartbeat_port}, "$system_name.manager");
}

print color('green');

#print ("All Managers have Started\n");
print("\n");
print color('bold yellow');
print("Starting Ticker Nodes\n");

foreach (keys %$ticker_config) {
	my $ticker_name = $_;
	print color('bold blue');
	print("Starting: Ticker ($ticker_name) ");
	my $pid=fork(); # TODO: Yea, We fork the current process and create a new one. But we do not assign 'new' file handlers
	die "Cannot fork: $!" if (! defined $pid);
	if (! $pid) {

		# Only the child does this
		setpgrp;
		eval{
			exec("python3 $cur_dir/module/ticker.py $system_name $ticker_name  >> /dev/$std_tty 2>> /dev/$std_err_tty &");
			exit(); # < Technically not possible to reach
			 # NO EXECUTION BELOW THIS POINT!
		};
	} else {

		# Only The Parent Does This.
		ping_node($ticker_config->{$_}->{heartbeat_port}, "$system_name.$_");
	}
}

print color('green');

#print ("All Tickers have Started\n");
print("\n");
print color('bold yellow');
print("Starting Algorithm Nodes\n");

foreach (keys %$algorithm_config) {
	my $ticker_name = $_;
	foreach (keys %{$algorithm_config->{$ticker_name}}) {
		print color('bold blue');
		print("Starting: Algorithm $ticker_name ($_) ");

		my $pid=fork(); # TODO: Yea, We fork the current process and create a new one. But we do not assign 'new' file handlers
		die "Cannot fork: $!" if (! defined $pid);
		if (! $pid) {

			# Only the child does this
			setpgrp;
			eval{
				#TODO: Explain What is going onhere
				exec("python3 $cur_dir/algorithm/$_.py $system_name $ticker_name $_ >> /dev/$std_tty 2>> /dev/$std_err_tty &");
				exit(); # < Technically not possible to reach
				 # NO EXECUTION BELOW THIS POINT!
			};
		} else {

			# Only The Parent Does This.
			ping_node($algorithm_config->{$ticker_name}->{$_}->{heartbeat_port}, "$system_name.$ticker_name.$_");
		}
	}
}

print color('green');

#print ("All Algorithms have Started\n");
print("\n");
print color('bold yellow');
print("Starting Algorothm Proxy Nodes\n");

foreach (keys %$proxy_config) {
	my $ticker_name = $_;
	print color('bold blue');
	print("Starting: Proxy ($ticker_name) ");
	my $pid=fork(); # TODO: Yea, We fork the current process and create a new one. But we do not assign 'new' file handlers
	die "Cannot fork: $!" if (! defined $pid);
	if (! $pid) {

		# Only the child does this
		setpgrp;
		eval{
			#TODO: Explain What is going onhere
			exec("python3 $cur_dir/module/util/proxy.py $system_name $ticker_name  >> /dev/$std_tty 2>> /dev/$std_err_tty &");
			exit(); # < Technically not possible to reach
			 # NO EXECUTION BELOW THIS POINT!
		};
	} else {

		# Only The Parent Does This.
		#ping_node(); We do not ping proxies (yet)
	}
}

print color('green');

#print ("All Algorithm Proxies have Started\n");
print("\n\n");
print color('bold yellow');
print("Starting Account Nodes\n");

foreach (keys %$account_config) {
	my $ticker_name = $_;
	print color('bold blue');
	print("Starting: Account ($ticker_name) ");
	my $pid=fork(); # TODO: Yea, We fork the current process and create a new one. But we do not assign 'new' file handlers
	die "Cannot fork: $!" if (! defined $pid);
	if (! $pid) {

		# Only the child does this
		setpgrp;
		eval {
			#TODO: Explain What is going onhere
			exec("python3 $cur_dir/module/system/$system_name/account.py $system_name $ticker_name  >> /dev/$std_tty 2>> /dev/$std_err_tty &");
			exit(); # < Technically not possible to reach
			 # NO EXECUTION BELOW THIS POINT!
		};


	} else {

		# Only The Parent Does This.
		ping_node($account_config->{$ticker_name}->{heartbeat_port}, "$system_name.$ticker_name.account");
	}
}

print color('green');

#print ("All Accounts have Started\n");
print("\n");
print color('bold yellow');
print("Starting Broker\n");
print color('bold blue');

print("Starting: Broker ($system_name)\n");
$pid=fork(); # TODO: Yea, We fork the current process and create a new one. But we do not assign 'new' file handlers
die "Cannot fork: $!" if (! defined $pid);
if (! $pid) {

	# Only the child does this
	setpgrp;
	eval {
		exec("python3 $cur_dir/module/broker.py $system_name   >> /dev/$std_tty 2>> /dev/$std_err_tty &");
		exit(); # < Technically not possible to reach
		 # NO EXECUTION BELOW THIS POINT!
	};

} else {

	# Only The Parent Does This.
	#ping_node(); No Ping Broker (Just Yet)
}

print color('green');

#print ("All Broker's have Started\n");
print("\n");
print color('bold yellow');
print("Starting Trader\n");
print color('bold blue');
print("Starting: Trader ($system_name) ");
print color('bold green');


$pid=fork();
die "Cannot fork: $!" if (! defined $pid);
print color('bold blue');

if (! $pid) {

	# Only the child does this
	setpgrp;
	eval{

		exec("python3 $cur_dir/module/system/$system_name/trader.py $system_name   >> /dev/$std_tty 2>> /dev/$std_err_tty &");
		exit(); # < Technically not possible to reach
		 # NO EXECUTION BELOW THIS POINT!
	};

} else {

	# Only The Parent Does This.
	ping_node($trader_config->{heartbeat_port}, "$system_name.trader");
}

print color('green');

#print ("All Brokers And Traders have Started\n");
print("\n");
print color('bold magenta');
print ("F_Trader ($system_name) has Started in State: Waiting for Executive\n");

#TODO: Hand over control to the executive node
