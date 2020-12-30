from strategy.choose.doubleLine import handle_data
from util import timeUtil, dataUtil

if __name__ == '__main__':
    while 1:
        # if timeUtil.in_trade_time():
        if timeUtil.in_trade_time(time1='9:00', time2='23:00'):
            handle_data()


