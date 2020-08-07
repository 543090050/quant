import baostock as bs
import pandas as pd

# 股票文件的存储路径
FILE_PATH = 'D:/stockFile/'
DATA_COLUMN = "date,code,open,high,low,close,volume"

bs.login()


# 获取交易日信息，并存储成文件
def get_trade_cal():
    filename = FILE_PATH + 'trade_cal.csv'

    try:
        # print("get_trade_cal 从", filename, "中获取交易日信息")
        result = pd.read_csv(filename)
    except FileNotFoundError:
        print("get_trade_cal 从文件中获取交易日信息失败，从API接口重新下载数据")
        # bs.login()
        rs = bs.query_trade_dates()
        data_list = []
        while (rs.error_code == '0') & rs.next():
            data_list.append(rs.get_row_data())
        result = pd.DataFrame(data_list, columns=rs.fields)
        result.to_csv(filename, encoding="gbk", index=False)
        # bs.logout()
    return result


# 获取当日行情(游标日)
# return dataFrame
def get_today_data(context, security):
    today = context.cursor_date.strftime('%Y-%m-%d')
    filename = FILE_PATH + security + '.csv'
    try:
        # print("get_today_data 从%s文件中获取%s今日行情(%s)" % (filename, security,today))
        f = open(filename, 'r')
        df = pd.read_csv(f, index_col='date', parse_dates=['date'])
        data = df.loc[today, :]
    except FileNotFoundError:
        print("get_today_data 从", filename, "文件中获取今日行情失败，改为从api接口获取")
        save_history_k_data(security)
        return get_today_data(context, security)
    except KeyError:
        data = pd.Series()
        print("get_today_data 未获取到%s的%s数据，今日未更新或为非交易日" % (security, today))
    return data


# 根据股票代码下载并生每日的k线成历史行情数据
def save_history_k_data(security, start_date='2017-01-01'):
    # print("save_history_k_data 根据股票代码 %s 调用API下载历史k线数据" % security)
    # bs.login()
    rs = bs.query_history_k_data_plus(security,
                                      DATA_COLUMN,
                                      start_date=start_date,
                                      frequency="d", adjustflag="3")
    if rs.error_code != '0':
        raise NameError("save_history_k_data respond  error_msg:" + rs.error_msg)
    else:
        filename = FILE_PATH + security + '.csv'
        print("将股票%s保存至%s" % (security, filename))
        data_list = []
        while (rs.error_code == '0') & rs.next():
            data_list.append(rs.get_row_data())
        result = pd.DataFrame(data_list, columns=rs.fields)
        result.to_csv(filename, index=False)
    # bs.logout()


# 历史行情数据
# security(股票代码); count(返回前几天),fields(返回的属性)
def attribute_history(context, security, count, fields=('open', 'close', 'high', 'low', 'volume')):
    # end_date = (context.cursor_date - datetime.timedelta(days=1)).strftime('%Y-%m-%d')
    end_date = context.cursor_date.strftime('%Y-%m-%d')
    start_date = context.trade_cal[(context.trade_cal['is_trading_day'] == 1) &
                                   (context.trade_cal['calendar_date'] <= end_date)][-count:].iloc[0, :][
        'calendar_date']
    return attribute_daterange_history(security, start_date, end_date, fields)


# 历史行情数据
# security(股票代码); start_date - end_date时间范围内, fields(返回的属性)
def attribute_daterange_history(security, start_date, end_date, fields=('open', 'close', 'high', 'low', 'volume')):
    filename = FILE_PATH + security + '.csv'
    try:
        # print("attribute_daterange_history 从%s文件中获取%s历史行情" % (filename, security))
        f = open(filename, 'r')
        df = pd.read_csv(f, index_col='date', parse_dates=['date']).loc[start_date:end_date, :]
    except FileNotFoundError:
        print("attribute_daterange_history 从%s文件中获取%s历史行情失败，改为从api接口获取" % (filename, security))
        save_history_k_data(security)
        df = attribute_daterange_history(security, start_date, end_date, fields)
    return df[list(fields)]


# 下载成分股 上证50；沪深300；中证500
def download_sample_stocks(sample_name='sz50'):
    if sample_name == 'sz50':
        filename = FILE_PATH + "sz50_stocks.csv"
        rs = bs.query_sz50_stocks()
    elif sample_name == 'hs300':
        filename = FILE_PATH + "hs300_stocks.csv"
        rs = bs.query_hs300_stocks()
    elif sample_name == 'zz500':
        filename = FILE_PATH + "zz500_stocks.csv"
        rs = bs.query_zz500_stocks()

    stocks = []
    while (rs.error_code == '0') & rs.next():
        stocks.append(rs.get_row_data())
    result = pd.DataFrame(stocks, columns=rs.fields)
    result.to_csv(filename, encoding="gbk", index=False)
    print("将成分股%s保存至%s" % (sample_name, filename))

    # 开始下载样本股票的详细历史信息
    sample_stocks = pd.read_csv(filename, encoding='gbk')['code']
    for value in zip(sample_stocks):
        stock_code = value[0]
        save_history_k_data(stock_code)


# 查询成分股所包含的股票信息
def get_sample_stocks(sample_name='sz50'):
    if sample_name == 'sz50':
        filename = FILE_PATH + "sz50_stocks.csv"
    elif sample_name == 'hs300':
        filename = FILE_PATH + "hs300_stocks.csv"
    elif sample_name == 'zz500':
        filename = FILE_PATH + "zz500_stocks.csv"

    try:
        f = open(filename, 'r')
        result = pd.read_csv(f)
    except FileNotFoundError:
        print("get_sample_stocks 从文件中获取成分股%s失败，从API接口重新下载数据" % sample_name)
        download_sample_stocks(sample_name)
        f = open(filename, 'r')
        result = pd.read_csv(f)
    return result

# print(get_sample_stocks()['code'])
