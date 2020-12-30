import datetime
import time
import common.vars as vs
import baostock as bs
import pandas as pd


def getCurrentTime():
    """
    获取当前时间
    :return: str
    """
    return datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')


def getToday():
    """
    获取当天日期
    :return: str
    """
    return datetime.datetime.now().strftime("%Y-%m-%d")


def get_pre_day(days=365):
    """
    获取前多少天的日期
    :param days:
    :return: date
    """
    today = datetime.date.today()
    days = datetime.timedelta(days=days)
    preday = today - days
    return preday


def getYesterday():
    today = datetime.date.today()
    one_day = datetime.timedelta(days=1)
    yesterday = today - one_day
    return yesterday


def compare_time(time1, time2=datetime.datetime.now().strftime("%Y-%m-%d")):
    """
    time1 与 time2 比较大小
    :param time1: '2017-04-19'
    :param time2: '2017-04-20'
    :return: 1<2时返回False,1>=2时返回True
    """
    s_time = time.mktime(time.strptime(time1, '%Y-%m-%d'))
    e_time = time.mktime(time.strptime(time2, '%Y-%m-%d'))
    print('s_time is:', s_time)
    print('e_time is:', e_time)
    return (int(s_time) - int(e_time)) >= 0


def is_current_date_sina(line_split):
    """
    根据sina返回的结果判断数据是否是最新的
    :param line_split: 新浪的查询结果
    :return: boolean
    """
    # 分开处理sh和sz的返回结果
    time1 = line_split[-4]
    try:
        s_time = time.mktime(time.strptime(time1, '%Y-%m-%d'))
    except ValueError:
        time1 = line_split[-3]
        s_time = time.mktime(time.strptime(time1, '%Y-%m-%d'))
    e_time = time.mktime(time.strptime(getToday(), '%Y-%m-%d'))
    return (int(s_time) - int(e_time)) >= 0


def in_trade_time(time1='9:30', time2='15:00'):
    """
    判断当前时间是否在有效交易时间内
    :param time1: 9:30
    :param time2: 15:00
    :return: boolean
    """

    # 判断当日是否为交易日期
    trade_flag = is_trade_day()
    if trade_flag != 1:
        return False

    # 范围时间
    d_time1 = datetime.datetime.strptime(str(datetime.datetime.now().date()) + time1, '%Y-%m-%d%H:%M')
    d_time2 = datetime.datetime.strptime(str(datetime.datetime.now().date()) + time2, '%Y-%m-%d%H:%M')
    # 当前时间
    n_time = datetime.datetime.now()
    # print('当前时间： ' + str(n_time))
    # 判断当前时间是否在范围时间内
    return d_time1 < n_time < d_time2


def is_trade_day():
    """
    判断当日是否为交易日
    :return: boolean
    """
    return get_trade_cal().iloc[-1]['is_trading_day']


# 查询交易日信息
def get_trade_cal():
    filename = vs.FILE_PATH + 'trade_cal.csv'
    try:
        # logging.info("get_trade_cal 从", filename, "中获取交易日信息")
        result = pd.read_csv(filename)
    except FileNotFoundError:
        result = download_trade_cal()

    # 下载最新文件
    last_date = result['calendar_date'].iloc[-1]
    end_date = datetime.datetime.now().strftime("%Y-%m-%d")
    if last_date != end_date:
        result = download_trade_cal()
    return result


# 下载交易日信息
def download_trade_cal():
    bs.login()
    filename = vs.FILE_PATH + 'trade_cal.csv'
    rs = bs.query_trade_dates()
    data_list = []
    while (rs.error_code == '0') & rs.next():
        data_list.append(rs.get_row_data())
    result = pd.DataFrame(data_list, columns=rs.fields)
    result.to_csv(filename, encoding="gbk", index=False)
    return result


def is_today(target_date):
    """
    2020-03-25 17:03:55
    检测日期是否为当前日期
    :param target_date: str
    :return: Boolean
    """
    # Get the year, month and day
    c_year = datetime.datetime.now().year
    c_month = datetime.datetime.now().month
    c_day = datetime.datetime.now().day

    # Disassemble the date
    try:
        date_list = target_date.split(" ")[0].split("-")
    except AttributeError:
        target_date = target_date.strftime("%Y-%m-%d %H:%M:%S")
        date_list = target_date.split(" ")[0].split("-")
    t_year = int(date_list[0])
    t_month = int(date_list[1])
    t_day = int(date_list[2])

    final = False
    # Compare years, months and days
    if c_year == t_year and c_month == t_month and c_day == t_day:
        final = True
    return final
