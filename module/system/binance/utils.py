import sys
sys.path.insert(1, 'lib')
from enums import AcceptableKlineValues, Sleep
from util import Trade

sleep_mappings = {
    'RT' : Sleep.SLEEP_RT,
    '1m' : Sleep.SLEEP_1M,
    '3m' : Sleep.SLEEP_3M,
    '5m' : Sleep.SLEEP_5M,
    '15m' : Sleep.SLEEP_15M,
    '30m' : Sleep.SLEEP_30M,
    '1h' : Sleep.SLEEP_1H,
    '2h' : Sleep.SLEEP_2H,
    '4h' : Sleep.SLEEP_4H,
    '6h' : Sleep.SLEEP_6H,
    '8h' : Sleep.SLEEP_8H,
    '12h' : Sleep.SLEEP_12H,
    '1d' : Sleep.SLEEP_1D,

}
def get_sleep_unit_for_interval(interval):
    res =  sleep_mappings.get(interval, None)
    if res == None:
        return 5
    else:
        return res.value
