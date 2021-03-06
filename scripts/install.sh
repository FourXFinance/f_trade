#!/bin/bash

declare -a system_apps=("git" "perl" "perl-doc" "python3-pip" "tmux" "raptyr") 

for i in "${system_apps[@]}"
    do
    dpkg -l | cut -d " " -f 3 | grep -i "^$i$" > /dev/null 2>&1
    if [ $? = 0 ]
    then
        tput setaf 2;
        echo "(App) $i is Installed"
    else
    tput setaf 1;
    echo "(App) $i is not installed. Installing from apt"
    tput setaf 3;
        sudo apt-get install $i
    fi
done


# TODO: This could do with some work. It trys to install zmq no matter what.
declare -a system_libs=("libzmq3-dev")

for i in "${system_libs[@]}"
    do
    ldconfig -p | grep -i "^$i$" > /dev/null 2>&1
    if [ $? = 0 ]
    then
    tput setaf 2;
        echo "(Lib) $i is Installed"
    else
        tput setaf 1;
        echo "(Lib) $i is not installed. Installing from apt"
        tput setaf 3;
        sudo apt-get install $i
    fi
done

# Setup required Perl Libs.  Part 1 - cpan TODO: Figure out how to work with cpanm instead of cpan
declare -a perl_cpan_libs=("App:cpanminus")
for i in "${perl_cpan_libs[@]}"
do
    perldoc -l $i > /dev/null 2>&1
    if [ $? = 0 ]
    then
        tput setaf 2;
        echo "(Perl) $i is Installed"
    else
        tput setaf 1;
        echo "(Perl) $i is not installed. Installing from CPAN"
        tput setaf 3;
        cpan $i
    fi
done

# Setup required Perl Libs. Part 2 - cpanm
declare -a perl_cpanm_libs=( "JSON" "ZMQ::FFI" "YAML::XS" "TryCatch")

for i in "${perl_cpanm_libs[@]}"
do
    perldoc -l $i > /dev/null 2>&1
    if [ $? = 0 ]
    then
        tput setaf 2;
        echo "(Perl) $i is Installed"
    else
        tput setaf 1;
        echo "(Perl) $i is not installed. Installing from CPAN"
        tput setaf 3;
        cpanm --notest $i # Test if you have time.
    fi
done
# Setup required python Libs
declare -a python_pip_libs=("python-binance" "pyzmq" "pandas" "numpy")

for i in "${python_pip_libs[@]}"
do
    pip3 list | grep -F $i > /dev/null 2>&1
    if [ $? = 0 ]
    then
        tput setaf 2;
        echo "(Python) $i is Installed"
    else
        tput setaf 1;
        echo "(Python) $i is not installed. Installing from Pip"
        tput setaf 3;
        pip3 install $i
    fi
done

tput setaf 5;


# Setup required aliases

CUR_DIR="$(cd "$(dirname "$0")" && pwd)";
if [ -f ~/.f_trader_rc ]; then
    tput setaf 1;
    echo "Removing Old F_trader Configuration";
    rm ~/.f_trader_rc;
fi
touch ~/.f_trader_rc;
echo "alias F='perl ${CUR_DIR}/explore.pl'" >> ~/.f_trader_rc;
echo "alias B='perl ${CUR_DIR}/build.pl'" >> ~/.f_trader_rc;
echo "alias S='perl ${CUR_DIR}/status.pl'" >> ~/.f_trader_rc;
echo "alias K='perl ${CUR_DIR}/shutdown.pl'" >> ~/.f_trader_rc;
# We use tty63 for our output. This cannot be root
chmod 777 /dev/tty63 # TODO. 777 means we all die
tput setaf 2;
#TODO: Automatically source.
echo "F_Trader has Been Installed (Don't forget to source ~/.f_trader_rc for shorthand commands)";
