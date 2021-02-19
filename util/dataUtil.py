import time
import urllib.request

import pandas as pd
# 股票文件的存储路径
from dateutil.parser import ParserError

import common.vars as vs
from util import timeUtil
from util.logUtil import logger


def get_current_data(code_list, lock):
    """
    从新浪网实时获取数据
    :param lock:
    :param code_list: array
    :return: df
    """
    lock.acquire()  # 加锁
    time.sleep(vs.SINA_QUERY_INTERVAL)  # 每次请求间隔，防止被封IP
    url = "http://hq.sinajs.cn/list=" + ",".join(code_list)
    logger.info("新浪查询实时价格: " + url)
    # 抓取原始股票数据
    content = urllib.request.urlopen(url).read().decode("gbk").encode('utf8').strip()
    lock.release()  # 解锁

    df = pd.DataFrame()
    # 从line中读取数据
    for line in content.decode().split('\n'):
        line_split = line.split(',')
        code = line_split[0].split('="')[0][-8:]
        if len(line_split) == 1:
            logger.debug(code, '已退市')
            continue
        open_price = float(line_split[1])
        if open_price - 0.0 < 0.0001:
            logger.debug(code, '已停牌')
            continue
        if not timeUtil.is_current_date_sina(line_split):
            # 获取到的最后价格的日期 不是当日的
            continue
        df.loc[code, '股票代码'] = code
        df.loc[code, '股票名称'] = line_split[0].split('="')[-1]
        df.loc[code, '开盘价'] = float(line_split[1])
        df.loc[code, '昨收'] = float(line_split[2])
        df.loc[code, '最新价'] = float(line_split[3])
        df.loc[code, '最高价'] = float(line_split[4])
        df.loc[code, '最低价'] = float(line_split[5])
        df.loc[code, '成交手数'] = float(line_split[8])
        df.loc[code, '成交金额'] = float(line_split[9])
        try:
            df.loc[code, '最新时间'] = pd.to_datetime(line_split[-4] + u' ' + line_split[-3])
        except ParserError:
            # sh开头的与sz开头的时间结果位置不一致
            df.loc[code, '最新时间'] = pd.to_datetime(line_split[-3] + u' ' + line_split[-2])
    return df


def get_short_code(x):
    """
    把 sh.600000 替换成  sh600000
    """
    return x.replace(".", "")


def fill_today_data(current_data, history_data):
    """
    将今日最新价 追加到history_data后
    :param current_data:
    :param history_data:
    :return:
    """
    history_data_last_index = history_data.iloc[-1].name
    current_data_index = current_data['最新时间']
    if timeUtil.compare_time(current_data_index.strftime("%Y-%m-%d"), history_data_last_index.strftime("%Y-%m-%d")):
        # 证明今日正在交易，history中的数据为前一天的数据
        current_data_series = {
            "open": current_data['开盘价'],
            "close": current_data['最新价'],
            "high": current_data['最高价'],
            "low": current_data['最低价'],
            "volume": current_data['成交手数'],
            "amount": current_data['成交金额']
        }
        current_data_df = pd.DataFrame(current_data_series, index=[current_data_index])
        history_data = history_data.append(current_data_df)
    return history_data


def update_base_info(stocks_info, current_data_df, code):
    """
    将实时的查询结果赋值到stocks_info中
    :param stocks_info:
    :param current_data_df:
    :param code:
    :return:
    """
    current_data = current_data_df.loc[get_short_code(code)]  # 根据code从df中获取Series
    stocks_info.loc[code, '股票代码'] = code
    stocks_info.loc[code, '股票名称'] = current_data['股票名称']
    stocks_info.loc[code, '开盘价'] = current_data['开盘价']
    stocks_info.loc[code, '昨收'] = current_data['昨收']
    stocks_info.loc[code, '最新价'] = current_data['最新价']
    stocks_info.loc[code, '最高价'] = current_data['最高价']
    stocks_info.loc[code, '最低价'] = current_data['最低价']
    stocks_info.loc[code, '成交手数'] = current_data['成交手数']
    stocks_info.loc[code, '成交金额'] = current_data['成交金额']
    stocks_info.loc[code, '最新时间'] = current_data['最新时间']
    return stocks_info.loc[code]


def get_cur_ma_line(history_data, current_data, days):
    """
    计算移动平均线
    :param history_data:
    :param current_data:
    :param days: 计算 days日的移动平均线
    :return: Series
    """
    df = fill_today_data(current_data, history_data)
    return pd.Series.rolling(df['close'], window=days).mean()
