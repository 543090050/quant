# 布林带画图

import datetime

import dateutil
import matplotlib.pyplot as plt
import pandas as pd

from common import G
from common.Context import Context
from util import historyUtil

g = G
g.CASH = 100000
g.START_DATE = '2019-01-01'
g.END_DATE = datetime.datetime.now().strftime("%Y-%m-%d")
g.FILE_PATH = 'D:/stockFile/'  # 股票文件的存储路径

g.trade_cal = historyUtil.get_trade_cal()
context = Context(g.CASH, g.START_DATE, g.END_DATE, g.trade_cal)


def run():
    plt_df = pd.DataFrame(index=pd.to_datetime(context.date_range).strftime('%Y-%m-%d'), columns=['mean'])

    g.security = 'sh.601138'
    # 均线时间（天）
    g.date = 20
    # 布林带宽度
    g.k = 2

    # 股票的最近一次有效价格，用于处理停牌的情况
    last_prize = {}
    for cursor_date in context.date_range:
        # 计算游标日期
        context.cursor_date = dateutil.parser.parse(cursor_date)

        sr = historyUtil.attribute_history(context, g.security, g.date)['close']
        # 均线
        ma = sr.mean()
        # 上线
        up = ma + g.k * sr.std()
        # 下线
        down = ma - g.k * sr.std()
        # 当前价格
        price = historyUtil.get_today_data(context, g.security)['open']

        plt_df.loc[cursor_date, 'mean'] = ma
        plt_df.loc[cursor_date, 'price'] = price
        plt_df.loc[cursor_date, 'up'] = up
        plt_df.loc[cursor_date, 'down'] = down

    # 画图
    plt_df[['price', 'up', 'down']].plot()
    plt.show()


run()
