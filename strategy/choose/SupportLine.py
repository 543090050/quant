# 支撑线画图

import datetime

from quant.common.Context import Context
from quant.util import historyUtil, mainUtil

CASH = 100000
START_DATE = '2019-01-01'
END_DATE = datetime.datetime.now().strftime("%Y-%m-%d")
FILE_PATH = 'D:/stockFile/'  # 股票文件的存储路径

trade_cal = historyUtil.get_trade_cal()
context = Context(CASH, START_DATE, END_DATE, trade_cal)


def run():
    min_float_per = 20  # 大于最小值的百分之多少
    rise_per_condition = 8  # 增长条件 百分之多少

    sample_stocks_sz50 = historyUtil.get_sample_stocks('sz50')['code']
    sample_stocks = sample_stocks_sz50

    for value in zip(sample_stocks):
        security = value[0]
        # print("\n开始解析"+security)
        plt_df = historyUtil.attribute_history(context, security, 180)

        min_price = plt_df['close'].min()
        mean_price = plt_df['close'].mean()
        max_price = plt_df['close'].max()
        yesterday_open = plt_df['open'][-1]
        yesterday_close = plt_df['close'][-1]

        rise_flag = False
        min_flag = False

        rise_per = (yesterday_close - yesterday_open) / yesterday_open * 100
        if rise_per >= rise_per_condition:
            # print('%s符合涨幅条件' % security)
            # print("最小值：%f，最大值：%f，平均值：%f" % (min_price, max_price, mean_price))
            # print("昨日开盘：%f，昨日收盘：%f，涨幅：%s" % (yesterday_open, yesterday_close, mainUtil.parse_percent(rise_per)))
            rise_flag = True

        min_per = (yesterday_open - min_price) / min_price * 100  # 昨日价格与最低价的比值

        if min_per < min_float_per:
            # print('%s符合低值条件' % security)
            # print("最小值：%f，最大值：%f，平均值：%f" % (min_price, max_price, mean_price))
            # print("昨日开盘：%f，昨日收盘：%f，涨幅：%s" % (yesterday_open, yesterday_close, mainUtil.parse_percent(rise_per)))
            min_flag = True

        if rise_flag & min_flag:
            print('%s符合条件' % security)
            print("最小值：%f，最大值：%f，平均值：%f" % (min_price, max_price, mean_price))
            print("昨日开盘：%f，昨日收盘：%f，涨幅：%s" % (yesterday_open, yesterday_close, mainUtil.parse_percent(rise_per)))

    print("分析完成")


run()
