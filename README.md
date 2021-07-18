
# f_trade - Trade The Future^(TM)

This Repository contains the Code for f_trade. A ZeroMQ implementation of a trading system.

This trading system is designed to be agnostic of most limitations:
    - Algorithm Language
    - Market
    - Commodity
Designed by Warren Fletcher, Benjamin Wolfaardtm Julia Ruiter, and Björn Dierks. (c) FourXFinance

## Philosophy Of F Trader

Think of a Factory. This Factory receives some raw materials, processes them, and then ships them out to another factory which in tern does the same. Eventually, the final factory produces a product for the end-user. 

This network of factories is essentially how F_Trader works. This grid of Factories (Nodes) and the communication infrastructure between them (ZeroMQ) Is the basis for a language agnostic, scalable, reliable, and resilient system.

Right Now we are using python as the core language, But any language can be used as long as their are bindings for ZeroMQ available.


## A Detailed Explanation of f_Trader(tm)

Every Node in the system does one job and it does this job well. If you ever think that a node is doing two jobs, split them up. The only exception to this is logging. 

Each node communicates via a 'stream'. A stream is a logical ZeroMQ interface that connects ports to nodes.

Communication is not as simple as 'One Stream. One Node'. Infact, a single node can communicate with as many nodes as it wants. Streams are not handled directly by node. Instead they are handled by a 'Controller'. Multiple streams can be bound to a controller. The reason why we bind streams to controllers is to bundle related streams into a logical unit. For example. Each node comes with 3 default Controllers.

1. Upstream - To handle all inbound streams
2. Downstream - To handle all outbound streams
3. Intervention - To handle user-related commands

When consuming messages. We might chose to poll the 'intervention' controller before any other controller. Or we might not. It is up to you. 

NOTE: Future versions of f_trader might use an event loop. This would get rid of polling altogether.

Thankfully, the use of controllers has been (mostly) abstracted. You just need to mention which stream you are sending to (Or Receiving from) and the node will figure out which controller to use.

Each node follows an execution loop:

1. Get snapshot of the current system (What data is waiting to be processed)
2. Iterate through the data and produce the required outputs
3. Log state (If Logging is enabled)

This cycle is then repeated. By default data is stored in queues. That means on every tick of the system, each node will ingest the data available. If you do not want your data to stack up, there are methods which can be implemented.

There are many types of sockets. I cannot cover them all here. I would recommend a good solid reading of the ZeroMQ guide [here](https://zguide.zeromq.org/).

This document will be updated with more information as development continues.

If you are ever wondering what needs to be worked on. Simple type `git grep TODO` And see what pops up

## How to run f_trader(tm)

Pull the latest source code.

1. Run `sudo ./scripts/install.sh` to download and install all required dependancies. Please report if you any untracked dependancies I may have forgotten
2. Run `sudo ./scripts/build.sh <MARKET_NAME>` to build the required configs. Market Names come from `./config/system/<MARKET_NAME>.yaml`.
3. After the Configs are built. The system will start up.
4. Run `sudo ./scripts/status.pl` to get a list of all running nodes and there PIDs
5. Run `sudo tail -f/proc/PID_VALUE/fd/1` to get STDOUT for a specific Node (In Future, this will be more User Friendly)
6. Run `sudo tail -f/proc/PID_VALUE/fd/2` to get STDERR for a specific Node (In Future, this will be more User Friendly)

