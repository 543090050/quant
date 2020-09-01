# 布林带回测策略

from common.Context import Context
from common.G import G
from util import mainUtil, historyUtil, orderUtil

g = G
g.CASH = 100000
g.START_DATE = '2019-01-01'
g.END_DATE = '2020-07-20'
g.FILE_PATH = 'D:/stockFile/'  # 股票文件的存储路径

g.trade_cal = historyUtil.get_trade_cal()
context = Context(g.CASH, g.START_DATE, g.END_DATE, g.trade_cal)


# 初始化函数，设定基准等等
def initialize(context):
    mainUtil.set_benchmark(context, 'sh.601138')
    g.security = 'sh.601138'
    # 均线时间（天）
    g.M = 20
    # 布林带宽度
    g.k = 2


def handle_data(context, data=None):
    sr = historyUtil.attribute_history(context, g.security, g.M)['close']
    # 均线
    ma = sr.mean()
    # 上线
    up = ma + g.k * sr.std()
    # 下线
    down = ma - g.k * sr.std()
    # 当前价格
    p = historyUtil.get_today_data(context, g.security)['open']
    # 可用金额
    cash = context.cash
    if p < down and g.security not in context.positions:
        print("%s当前价格%s低于支撑线，进行买入" % (context.cursor_date, p))
        orderUtil.order_value(context, g.security, cash)
    elif p > up and g.security in context.positions:
        print("%s当前价格%s高于压力线，进行卖出" % (context.cursor_date, p))
        orderUtil.order_target(context, g.security, 0)


mainUtil.run(context, initialize, handle_data)
