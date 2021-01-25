import datetime
import threading

import baostock as bs
import pandas as pd

import common.vars as vs
from util import timeUtil
from util.logUtil import logger

# 股票文件的存储路径

FILE_PATH = vs.FILE_PATH
FIELDS_DAY = vs.FIELDS_DAY
h5_lock = threading.RLock()
bs.login()

pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)


# 查询交易日信息
def get_trade_cal():
    filename = FILE_PATH + 'trade_cal.csv'
    try:
        # logger.debug("get_trade_cal 从", filename, "中获取交易日信息")
        result = pd.read_csv(filename)
    except FileNotFoundError:
        logger.debug("get_trade_cal 从文件中获取交易日信息失败，从API接口重新下载数据")
        result = download_trade_cal()

    # 下载最新文件
    last_date = result['calendar_date'].iloc[-1]
    end_date = datetime.datetime.now().strftime("%Y-%m-%d")
    if last_date != end_date:
        result = download_trade_cal()
    return result


# 下载交易日信息
def download_trade_cal():
    filename = FILE_PATH + 'trade_cal.csv'
    rs = bs.query_trade_dates()
    data_list = []
    while (rs.error_code == '0') & rs.next():
        data_list.append(rs.get_row_data())
    result = pd.DataFrame(data_list, columns=rs.fields)
    result.to_csv(filename, encoding="gbk", index=False)
    return result


# 获取当日行情(游标日)
# return dataFrame
def get_today_data(context, security):
    today = context.cursor_date.strftime('%Y-%m-%d')
    filename = FILE_PATH + security + '.csv'
    try:
        # logger.debug("get_today_data 从%s文件中获取%s今日行情(%s)" % (filename, security,today))
        f = open(filename, 'r')
        df = pd.read_csv(f, index_col='date', parse_dates=['date'])
        data = df.loc[today, :]
    except FileNotFoundError:
        logger.debug("get_today_data 从", filename, "文件中获取今日行情失败，改为从api接口获取")
        download_history_k_data(security)
        return get_today_data(context, security)
    except KeyError:
        data = pd.Series()
        logger.debug("get_today_data 未获取到%s的%s数据，今日未更新或为非交易日" % (security, today))
    return data


def download_history_k_data(security, start_date='2017-01-01'):
    """
    根据股票代码下载每日的k线成历史行情数据
    :param security: 股票代码
    :param start_date: 开始日期 str
    :return:
    """
    # logger.debug("save_history_k_data 根据股票代码 %s 调用API下载历史k线数据" % security)
    # bs.login()
    rs = bs.query_history_k_data_plus(security,
                                      FIELDS_DAY,
                                      start_date=start_date,
                                      frequency="d", adjustflag="2")
    if rs.error_code != '0':
        raise NameError("save_history_k_data respond  error_msg:" + rs.error_msg)
    else:
        filename = FILE_PATH + security + '.csv'
        logger.debug("将股票%s保存至%s" % (security, filename))
        data_list = []
        while (rs.error_code == '0') & rs.next():
            data_list.append(rs.get_row_data())
        result = pd.DataFrame(data_list, columns=rs.fields)
        result.to_csv(filename, index=False)


def attribute_history(context, security, count, fields=(
        'open', 'close', 'high', 'low', 'volume', 'amount', 'turn', 'pctChg', 'peTTM', 'pbMRQ', 'psTTM', 'pcfNcfTTM')):
    """
    查询某个股票前count天的历史行情数据
    :param context:
    :param security: 股票代码
    :param count: 返回前几天
    :param fields: 提取列
    :return: df
    """
    # end_date = (context.cursor_date - datetime.timedelta(days=1)).strftime('%Y-%m-%d')
    end_date = context.cursor_date.strftime('%Y-%m-%d')
    start_date = context.trade_cal[(context.trade_cal['is_trading_day'] == 1) &
                                   (context.trade_cal['calendar_date'] <= end_date)][-count:].iloc[0, :][
        'calendar_date']
    return attribute_daterange_history(security, start_date, end_date, fields)


def attribute_daterange_history(security, start_date, end_date, fields=(
        'open', 'close', 'high', 'low', 'volume', 'amount', 'turn', 'pctChg', 'peTTM', 'pbMRQ', 'psTTM', 'pcfNcfTTM')):
    """
    获取时间范围内的历史行情
    :param security: 股票代码
    :param start_date: str 2020-09-25
    :param end_date: str 2020-12-31
    :param fields: 提取列
    :return: df
    """

    if timeUtil.compare_time(start_date, end_date):
        raise Exception('起始时间%s大于结束时间%s' % (start_date, end_date))

    global result
    filename = FILE_PATH + security + '.csv'
    try:
        # logger.debug("attribute_daterange_history 从%s文件中获取%s历史行情" % (filename, security))
        file = open(filename, 'r')
        df = pd.read_csv(file, index_col='date', parse_dates=['date'])
        result = df.loc[start_date:end_date, :]
    except FileNotFoundError:
        logger.debug("未找到%s历史行情文件，从接口下载" % security)
        download_history_k_data(security)
        df = attribute_daterange_history(security, start_date, end_date, fields)
    if len(df) == 0:
        raise Exception('未能从文件' + filename + '中获取到数据，或数据为空')
    last_date = df.index[-1].strftime('%Y-%m-%d')
    # 更新文件
    if not timeUtil.compare_time(last_date, end_date):  # 如果从文件中获取的日期，小于end_date，则更新文件
        logger.debug(security + "文件中的数据日期" + last_date + "小于当前日期" + end_date + ",重新下载文件以更新数据")
        download_history_k_data(security)
        file = open(filename, 'r')
        df = pd.read_csv(file, index_col='date', parse_dates=['date'])
        result = df.loc[start_date:end_date, :]
    return result[list(fields)]


# 下载成分股 上证50；沪深300；中证500；所有股票
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
    elif sample_name == 'all':
        filename = FILE_PATH + "all_stocks.csv"
        # 取前七天的成分股信息，如果取当前天的，可能当天没有更新
        trade_cal = get_trade_cal()
        trade_day = trade_cal[(trade_cal['is_trading_day'] == 1)]['calendar_date'].values
        rs = bs.query_all_stock()

    stocks = []
    while (rs.error_code == '0') & rs.next():
        stocks.append(rs.get_row_data())
    result = pd.DataFrame(stocks, columns=rs.fields)
    result.to_csv(filename, encoding="gbk", index=False)
    logger.debug("将成分股%s保存至%s" % (sample_name, filename))

    # 开始下载样本股票的详细历史信息
    # sample_stocks = pd.read_csv(filename, encoding='gbk')['code']
    # for value in zip(sample_stocks):
    #     stock_code = value[0]
    #     download_history_k_data(stock_code)


def get_sample_stocks(sample_name='sz50'):
    """
    查询成分股所包含的股票信息
    :param sample_name: str
    :return: df
    """
    if sample_name == 'sz50':
        filename = FILE_PATH + "sz50_stocks.csv"
    elif sample_name == 'hs300':
        filename = FILE_PATH + "hs300_stocks.csv"
    elif sample_name == 'zz500':
        filename = FILE_PATH + "zz500_stocks.csv"
    elif sample_name == 'all':
        filename = FILE_PATH + "all_stocks.csv"

    try:
        f = open(filename, 'r')
        result = pd.read_csv(f)
    except FileNotFoundError:
        logger.debug("get_sample_stocks 从文件中获取成分股%s失败，从API接口重新下载数据" % sample_name)
        download_sample_stocks(sample_name)
        f = open(filename, 'r')
        result = pd.read_csv(f)
    return result
