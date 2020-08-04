# 布林带

from quant.common.Context import Context
from quant.common.G import G
from quant.util import mainUtil, historyUtil, orderUtil

g = G
g.CASH = 100000
g.START_DATE = '2020-01-01'
g.END_DATE = '2020-07-20'
g.FILE_PATH = 'D:/stockFile/'  # 股票文件的存储路径

g.trade_cal = historyUtil.get_trade_cal()
context = Context(g.CASH, g.START_DATE, g.END_DATE, g.trade_cal)


# 初始化函数，设定基准等等
def initialize(context):
    # 设定沪深300作为基准
    mainUtil.set_benchmark(context, 'sh.601318')
    # 开启动态复权模式(真实价格)
    # set_option('use_real_price', True)

    g.security = 'sh.601318'
    # 均线时间（天）
    g.M = 20
    # 布林带宽度
    g.k = 1.7


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
        print("当前价格%s低于支撑线，进行买入" % p)
        orderUtil.order_value(context, g.security, cash)
    elif p > up and g.security in context.positions:
        print("当前价格%s高于压力线，进行卖出" % p)
        orderUtil.order_target(context, g.security, 0)


mainUtil.run(context, initialize, handle_data)
