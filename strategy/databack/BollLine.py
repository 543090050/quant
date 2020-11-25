# 布林带回测策略

from common.Context import Context
from common.G import G
from util import mainUtil, dataUtil, orderUtil
from util.mainUtil import getYesterday

g = G
g.security = 'sh.601933'
g.CASH = 100000
g.START_DATE = '2020-01-01'
g.END_DATE = getYesterday().strftime("%Y-%m-%d")
g.FILE_PATH = 'D:/stockFile/'  # 股票文件的存储路径

g.trade_cal = dataUtil.get_trade_cal()
context = Context(g.CASH, g.START_DATE, g.END_DATE, g.trade_cal)


# 初始化函数，设定基准等等
def initialize(context):
    mainUtil.set_benchmark(context, g.security)
    # 均线时间（天）
    g.M = 20
    # 布林带宽度
    g.k = 1.5


def handle_data(context, data=None):
    sr = dataUtil.attribute_history(context, g.security, g.M)['close']
    # 均线
    ma = sr.mean()
    # 上线
    up = ma + g.k * sr.std()
    # 下线
    down = ma - g.k * sr.std()
    # 当前价格
    p = dataUtil.get_today_data(context, g.security)['open']
    # 可用金额
    cash = context.cash
    cursor_date = context.cursor_date.strftime("%Y-%m-%d")
    if p < down and g.security not in context.positions:
        print("%s价格%s低于支撑线，进行买入" % (cursor_date, p))
        orderUtil.order_value(context, g.security, cash)
    elif p > up and g.security in context.positions:
        print("%s价格%s高于压力线，进行卖出" % (cursor_date, p))
        orderUtil.order_target(context, g.security, 0)


mainUtil.run(context, initialize, handle_data)
