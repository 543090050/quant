from util import historyUtil

FILE_PATH = 'D:/stockFile/'  # 股票文件的存储路径


# 下单函数 正数为买，负数为卖
# 今日行情，股票代码，操作股票的数量
def _order(context, today_data, security, amount):
    operate_flag = "买入"
    if amount < 0:
        operate_flag = "卖出"

    print("%s%s股%s" % (operate_flag, amount, security))
    if len(today_data) == 0:
        print("今日停牌")
        return

    # 当前股票价格
    p = today_data['open']
    if context.cash - amount * p < 0:
        amount = int(context.cash / p)
        print("现金不足,已调整为%d股" % amount)

    # 买卖的数量为100的倍数
    if amount % 100 != 0:
        if amount != -context.positions.get(security, 0):
            err_amount = amount
            # 负号为卖出，卖出时不等于当前持有这只股票的总数
            amount = int(amount / 100) * 100
            print("%s的数量%s不是100的倍数，已调整为%d股" % (operate_flag, err_amount, amount))

    # 卖出的数量大于已持有的数量时
    if context.positions.get(security, 0) < -amount:
        amount = -context.positions.get(security, 0)
        print("卖出股票不能超过持仓数，已调整为%d股" % amount)

    # 更新持仓信息
    context.positions[security] = context.positions.get(security, 0) + amount
    if context.positions[security] == 0:
        del context.positions[security]

    # 更新现金信息
    context.cash = context.cash - amount * p
    print("剩余可用金额%s" % context.cash)


# 买卖多少股
def order(context, security, amount):
    today_data = historyUtil.get_today_data(context, security)
    _order(context, today_data, security, amount)


# 买卖至多少股
def order_target(context, security, amount):
    if amount < 0:
        print("目标股数不能为负,已调整为0")
        amount = 0
    today_data = historyUtil.get_today_data(context, security)
    hold_amount = context.positions.get(security, 0)  # TODO 卖出没有考虑 T+1
    delta_amount = amount - hold_amount
    _order(context, today_data, security, delta_amount)


# 买卖多少钱的股票
def order_value(context, security, value):
    today_data = historyUtil.get_today_data(context, security)
    amount = int(value / today_data['open'])
    _order(context, today_data, security, amount)


# 买卖至价值多少钱的股票
def order_target_value(context, security, value):
    if value < 0:
        print("目标价值不能为负，已调整为0")
        value = 0
    today_data = historyUtil.get_today_data(context, security)
    hold_value = context.positions.get(security, 0) * today_data['open']
    delta_value = value - hold_value
    order_value(context, security, delta_value)
