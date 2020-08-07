# 布林带选股策略
import datetime

import dateutil

from quant.common import G
from quant.common.Context import Context
from quant.util import historyUtil

g = G
g.CASH = 100000
g.START_DATE = '2020-01-01'
g.END_DATE = datetime.datetime.now().strftime("%Y-%m-%d")
g.FILE_PATH = 'D:/stockFile/'  # 股票文件的存储路径

g.trade_cal = historyUtil.get_trade_cal()
context = Context(g.CASH, g.START_DATE, g.END_DATE, g.trade_cal)


def run():
    # historyUtil.download_sample_stocks()
    g.security = 'sh.601318'
    # 均线时间（天）
    g.mean_date = 20
    # 布林带宽度
    g.k = 1.7

    # 取昨天的交易日期，因为今天的k线数据还没有更新到文件里
    context.cursor_date = dateutil.parser.parse(context.date_range[-2])

    sr = historyUtil.attribute_history(context, g.security, g.mean_date)['close']
    # 均线
    ma = sr.mean()
    # 上线
    up = ma + g.k * sr.std()
    # 下线
    down = ma - g.k * sr.std()
    # 当前价格
    p = historyUtil.get_today_data(context, g.security)['open']
    #
    # if p < down and g.security not in context.positions:
    #     print("%s 当前价格%s低于支撑线，进行买入" % (g.security,p))
    # elif p > up and g.security in context.positions:
    #     # print("%s 当前价格%s高于压力线，进行卖出" % (g.security,p))
    #     pass

    # data = pd.Series()
    # print(data)


run()
