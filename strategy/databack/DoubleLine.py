# 双均线回测策略

from common import G
from common.Context import Context
from util import baoStockUtil, mainUtil, orderUtil

g = G
g.CASH = 100000
g.START_DATE = '2020-01-01'
g.END_DATE = '2020-07-20'
g.FILE_PATH = 'D:/stockFile/'  # 股票文件的存储路径

g.trade_cal = baoStockUtil.get_trade_cal()
context = Context(g.CASH, g.START_DATE, g.END_DATE, g.trade_cal)


# 用户自定义函数：初始化
def initialize(context):
    mainUtil.set_benchmark(context, 'sh.601318')
    g.p1 = 5
    g.p2 = 60
    g.security = 'sh.601318'


# 用户自定义函数：处理数据
def handle_data(context):
    # 双均线策略

    hist = baoStockUtil.attribute_history(context, g.security, g.p2)
    ma5 = hist['close'][-g.p1:].mean()
    ma60 = hist['close'].mean()

    if ma5 > ma60 and g.security not in context.positions:
        orderUtil.order_value(context, g.security, context.cash)
    elif ma5 < ma60 and g.security in context.positions:
        orderUtil.order_target(context, g.security, 0)


mainUtil.run(context, initialize, handle_data)
