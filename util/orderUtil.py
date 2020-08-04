from pTest.util.historyUtil import get_today_data

FILE_PATH = 'D:/stockFile/'  # 股票文件的存储路径


# context.dt = datetime.datetime.strptime('2018-01-05', '%Y-%m-%d')
# print(get_today_data('sh.601318'))


# 下单函数 正数为买，负数为卖
# 今日行情，股票代码，操作股票的数量(手，100的倍数)
def _order(context, today_data, security, amount):
    if len(today_data) == 0:
        print("今日停牌")
        return

    # 当前股票价格
    p = today_data['open']
    if context.cash - amount * p < 0:
        amount = int(context.cash / p)
        print("现金不足,已调整为%d手" % amount)

    # 买卖的手数为100的倍数
    if amount % 100 != 0:
        if amount != -context.positions.get(security, 0):
            # 负号为卖出，卖出时不等于当前持有这只股票的总数
            amount = int(amount / 100) * 100
            print("买卖的手数不是100的倍数，已调整为%d手" % amount)

    # 卖出的数量大于已持有的数量时
    if context.positions.get(security, 0) < -amount:
        amount = -context.positions.get(security, 0)
        print("卖出股票不能超过持仓数，已调整为%d手" % amount)

    # 更新持仓信息
    context.positions[security] = context.positions.get(security, 0) + amount
    if context.positions[security] == 0:
        del context.positions[security]

    # 更新现金信息
    context.cash = context.cash - amount * p


# 买多少手的这只股票
def order(context, security, amount):
    today_data = get_today_data(context, security)
    _order(context, today_data, security, amount)


# 买到多少手
def order_target(context, security, amount):
    if amount < 0:
        print("数量不能为负,已调整为0")
        amount = 0
    today_data = get_today_data(context, security)
    hold_amount = context.positions.get(security, 0)  # TODO 卖出没有考虑 T+1
    delta_amount = amount - hold_amount
    _order(context, today_data, security, delta_amount)


# 买多少钱的股票
def order_value(context, security, value):
    today_data = get_today_data(context, security)
    amount = int(value / today_data['open'])
    _order(context, today_data, security, amount)


# 买至价值到多少钱的股票
def order_target_value(context, security, value):
    if value < 0:
        print("价值不能为负，已调整为0")
        value = 0
    today_data = get_today_data(context, security)
    hold_value = context.positions.get(security, 0) * today_data['open']
    delta_value = value - hold_value
    order_value(context, security, delta_value)
