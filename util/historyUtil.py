import datetime

import baostock as bs
import pandas as pd

FILE_PATH = 'D:/stockFile/'  # 股票文件的存储路径


# 获取交易日信息，并存储成文件
def get_trade_cal():
    file_name = FILE_PATH + 'trade_cal.csv'

    try:
        print("get_trade_cal 从", file_name, "中获取交易日信息")
        result = pd.read_csv(file_name)
    except FileNotFoundError:
        print("从文件中获取交易日信息失败，改为调用API接口")
        bs.login()
        rs = bs.query_trade_dates()
        data_list = []
        while (rs.error_code == '0') & rs.next():
            data_list.append(rs.get_row_data())
        result = pd.DataFrame(data_list, columns=rs.fields)
        result.to_csv(file_name, encoding="gbk", index=False)
        bs.logout()
    return result


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


# 获取今日行情
def get_today_data(context, security):
    today = context.dt.strftime('%Y-%m-%d')
    file_name = FILE_PATH + security + '.csv'
    try:
        print("get_today_data 从%s文件中获取%s今日行情" % (file_name, security))
        f = open(file_name, 'r')
        data = pd.read_csv(f, index_col='date', parse_dates=['date']).loc[today, :]
    except FileNotFoundError:
        print("get_today_data 从", file_name, "文件中获取今日行情失败，改为从api接口获取")
        save_history_k_data(security)
        return get_today_data(context, security)
    except KeyError:
        data = pd.Series()
        print("get_today_data", today, "为非交易日或", security, "已停牌")
    return data


# 根据股票代码下载并生每日的k线成历史行情数据
def save_history_k_data(security):
    print("save_history_k_data 根据股票代码 %s 调用API下载历史k线数据" % security)
    bs.login()
    rs = bs.query_history_k_data_plus(security,
                                      "date,code,open,high,low,close,volume",
                                      frequency="d", adjustflag="3")
    if rs.error_code != '0':
        raise NameError("save_history_k_data respond  error_msg:" + rs.error_msg)
    else:
        file_name = FILE_PATH + security + '.csv'
        print("将股票%s保存至%s" % (security, file_name))
        data_list = []
        while (rs.error_code == '0') & rs.next():
            data_list.append(rs.get_row_data())
        result = pd.DataFrame(data_list, columns=rs.fields)
        result.to_csv(file_name, index=False)
    bs.logout()


# 历史行情数据
# security(股票代码); count(返回前几天),fields(返回的属性)
def attribute_history(context, security, count, fields=('open', 'close', 'high', 'low', 'volume')):
    # 历史的结束日期
    end_date = (context.dt - datetime.timedelta(days=1)).strftime('%Y-%m-%d')
    # 历史的开始日期
    start_date = context.trade_cal[(context.trade_cal['is_trading_day'] == 1) &
                                   (context.trade_cal['calendar_date'] <= end_date)][-count:].iloc[0, :][
        'calendar_date']
    return attribute_daterange_history(security, start_date, end_date, fields)


# 历史行情数据
# security(股票代码); start_date - end_date时间范围内, fields(返回的属性)
def attribute_daterange_history(security, start_date, end_date, fields=('open', 'close', 'high', 'low', 'volume')):
    file_name = FILE_PATH + security + '.csv'
    try:
        print("attribute_daterange_history 从%s文件中获取%s历史行情" % (file_name, security))
        f = open(file_name, 'r')
        df = pd.read_csv(f, index_col='date', parse_dates=['date']).loc[start_date:end_date, :]
    except FileNotFoundError:
        print("attribute_daterange_history 从%s文件中获取%s历史行情失败，改为从api接口获取" % (file_name, security))
        save_history_k_data(security)
        df = attribute_daterange_history(security, start_date, end_date, fields)
    return df[list(fields)]
