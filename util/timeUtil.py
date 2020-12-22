import datetime
import time


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


def is_current_date(line_split):
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


def in_trade_time(time1='9:00', time2='15:00'):
    """
    判断当前时间是否在
    :param time1:
    :param time2:
    :return: boolean
    """
    # 范围时间
    d_time1 = datetime.datetime.strptime(str(datetime.datetime.now().date()) + time1, '%Y-%m-%d%H:%M')
    d_time2 = datetime.datetime.strptime(str(datetime.datetime.now().date()) + time2, '%Y-%m-%d%H:%M')
    # 当前时间
    n_time = datetime.datetime.now()
    # print('当前时间： ' + str(n_time))
    # 判断当前时间是否在范围时间内
    return d_time1 < n_time < d_time2
