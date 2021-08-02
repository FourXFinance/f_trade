# A Generic market agnostic trade object (sent from Acc to Broker/Trader)
class Trade():
    market = None
    def __init__(self) -> None:
        pass

# A Generic market Agnostic trade request object (sent from Algo to Acc)
class TradeRequest():
    market = None
    trade_data = None
    def __init__(self) -> None:
        pass
# Colors for Printing to terminal
class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
