from os import remove
from sys import path,argv
path.insert(1, 'lib')
from enums import TradeType
# A Generic market agnostic trade object (sent from Acc to Broker/Trader)
class Trade():
    market = None
    def __init__(self) -> None:
        pass

# A Generic market Agnostic trade request object (sent from Algo to Acc)
class TradeRequest():
    market = None
    misc_trade_data = None
    trade_type = None
    purchase_price = None
    def set_trade_type(self, trade_type):
        acceptable_values = set(item.value for item in TradeType)
        if trade_type in acceptable_values:
            self.trade_type = trade_type
        else:
            raise Exception("Trade Type is Unsupported!:" + str(trade_type))
    def set_purchase_type(self, purchase_type): #Unused
        self.purchase_type = purchase_type
    def set_sale_type(self, sale_type): #Unused
        self.sale_type = sale_type

    def set_purchase_price(self, price):
        self.purchase_price = price #Price = "-1" for MARKET PURCHASE
    def set_sale_price(self, price):
        self.set_sale_price = price #Price = "-1" for MARKET PURCHASE
    def set_market(self, market):
        self.market = market
    def set_additional_data(self, misc_trade_date):
        self.misc_trade_data = misc_trade_date
    def validate(self):
        # This message is evaluated before we send the request to the Account Node
        pass
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
