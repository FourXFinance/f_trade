from enum import Enum

minute = 60 

class TradeType(Enum):
    BUY = 0b1
    SELL = 0b1 << 1
    BUY_WITH_SELL = 0b1 << 2
    BUY_WITH_OCO = 0b1 << 3
    SELL_WITH_BUY = 0b1 << 4 #Not sure these are positions we want?
    CLOSE_ALL = 0b1 << 5 #  In event of an emergency

class AcceptableKlineValues(Enum):
    KLINE_INTERVAL_RT = 'RT' # Special Case for our system
    KLINE_INTERVAL_1MINUTE = '1m' #These are all replicated from python-binance
    KLINE_INTERVAL_3MINUTE = '3m'
    KLINE_INTERVAL_5MINUTE = '5m'
    KLINE_INTERVAL_15MINUTE = '15m'
    KLINE_INTERVAL_30MINUTE = '30m'
    KLINE_INTERVAL_1HOUR = '1h'
    KLINE_INTERVAL_2HOUR = '2h'
    KLINE_INTERVAL_4HOUR = '4h'
    KLINE_INTERVAL_6HOUR = '6h'
    KLINE_INTERVAL_8HOUR = '8h'
    KLINE_INTERVAL_12HOUR = '12h'
    KLINE_INTERVAL_1DAY = '1d'
    KLINE_INTERVAL_3DAY = '3d'
    KLINE_INTERVAL_1WEEK = '1w'
    KLINE_INTERVAL_1MONTH = '1M'

class Sleep(Enum):
    SLEEP_RT =  5 # RT Time will dominate bandwidth use!
    SLEEP_1M =  (1 * minute) - 1
    SLEEP_3M =  (3 * minute) - 1
    SLEEP_5M =  (5 * minute) - 1
    SLEEP_15M = (15 * minute) - 1
    SLEEP_30M = (30 * minute) - 1
    SLEEP_1H =  (60 * minute) - 1
    SLEEP_2H =  (120 * minute) - 1
    SLEEP_4H =  (240 * minute) - 1
    SLEEP_6H =  (300 * minute) - 1
    SLEEP_8H =  (480 * minute) - 1
    SLEEP_12H =  (720 * minute) - 1
    SLEEP_1D =  (1440 * minute) - 1

class NodeModes(Enum):
    START_UP_AWAITING_PING = 0b1
    START_UP_AWAITING_EXEC = 0b1 << 1
    OK = 0b1 << 2
    ERROR = 0b1 << 3

class SystemModes(Enum):
    TEST_STARTING_UP = 0b1
    STARTING_UP = 0b1 << 1
    OK = 0b1 << 2
    ERROR = 0b1 << 3
    

    

