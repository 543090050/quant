# 最低值上涨选股

import datetime

from common.Context import Context
from util import baoStockUtil, mainUtil

CASH = 100000
START_DATE = '2019-01-01'
END_DATE = datetime.datetime.now().strftime("%Y-%m-%d")
FILE_PATH = 'D:/stockFile/'  # 股票文件的存储路径

trade_cal = baoStockUtil.get_trade_cal()
context = Context(CASH, START_DATE, END_DATE, trade_cal)


def run():
    min_float_per = 20  # 触底条件，大于最小值的百分之多少
    rise_per_condition = 8  # 涨幅条件

    # sample_stocks = historyUtil.get_sample_stocks('all')['code']
    sample_stocks = baoStockUtil.get_sample_stocks('sz50')['code']
    # sample_stocks = historyUtil.get_sample_stocks('zz500')['code']

    for value in zip(sample_stocks):
        security = value[0]
        # print("\n开始解析"+security)
        plt_df = baoStockUtil.attribute_history(context, security, 180)

        min_price = plt_df['close'].min()
        mean_price = plt_df['close'].mean()
        max_price = plt_df['close'].max()
        yesterday_open = plt_df['open'][-1]
        yesterday_close = plt_df['close'][-1]

        rise_flag = False
        min_flag = False
        #涨跌幅
        pctChg = plt_df['pctChg'][-1]
        if pctChg >= rise_per_condition:
            rise_flag = True

        min_per = (yesterday_open - min_price) / min_price * 100  # 昨日价格与最低价的比值

        if min_per < min_float_per:
            min_flag = True

        if rise_flag & min_flag:
            print('%s符合条件' % security)
            print("从%s开始，最小值：%f，最大值：%f，平均值：%f" % (START_DATE,min_price, max_price, mean_price))
            print("昨日开盘：%f，昨日收盘：%f，涨幅：%s" % (yesterday_open, yesterday_close, mainUtil.parse_percent(pctChg)))

    print("分析完成")


run()
