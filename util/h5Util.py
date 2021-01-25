import threading

import pandas as pd

import common.vars as vs
from util import timeUtil
from util.logUtil import logger

FILE_PATH = vs.FILE_PATH
FIELDS_DAY = vs.FIELDS_DAY
h5_lock = threading.RLock()


def put_h5_data(key, value):
    """
    写入h5文件
    :param key: str
    :param value: df
    """
    filename = FILE_PATH + "stock_data.h5"
    h5_lock.acquire()  # 加锁
    hStore = pd.HDFStore(filename, 'w')
    hStore.put(key, value, format='table', append=False)
    hStore.close()
    h5_lock.release()  # 解锁


def get_h5_data(key):
    """
    读h5文件
    :param key: str
    :return: df
    """
    filename = FILE_PATH + "stock_data.h5"
    h5_lock.acquire()  # 加锁
    result = pd.read_hdf(filename, key=key)
    h5_lock.release()  # 解锁
    return result


def init_stocks_info():
    """
    构造stocks_info，初始化基本列
    :return: df
    """
    logger.debug("h5文件中的信息错误或已过期，清空h5文件重新构建")
    stocks_info = pd.DataFrame()
    # 构造列，防止空列错误
    # stocks_info['code'] = 'NaN'
    stocks_info['股票代码'] = 'NaN'
    stocks_info['股票名称'] = 'NaN'
    stocks_info['开盘价'] = 'NaN'
    stocks_info['昨收'] = 'NaN'
    stocks_info['最新价'] = 'NaN'
    stocks_info['最高价'] = 'NaN'
    stocks_info['最低价'] = 'NaN'
    stocks_info['成交手数'] = 'NaN'
    stocks_info['成交金额'] = 'NaN'
    stocks_info['最新时间'] = 'NaN'
    stocks_info['gold_flag'] = 'NaN'
    stocks_info['dead_flag'] = 'NaN'
    stocks_info['ma30_flag'] = 'NaN'
    stocks_info['ma8_flag'] = 'NaN'
    stocks_info['w_shape_flag'] = 'NaN'
    return stocks_info


def get_stocks_info_from_h5(key='stocks_info'):
    """
    从h5文件中读取股票信息
    :return: df
    """
    result = get_h5_data(key)
    # 清空h5文件，重新构造
    clear_flag = False
    try:
        if not timeUtil.is_today(result.iloc[-1]['最新时间']) and timeUtil.is_trade_day():
            # 如果从文件里读出的信息不是当日的最新信息，则清空文件内容，这样做是为了每天初始化消息信号的标志位
            clear_flag = True
    except KeyError:  # 读取不到最新时间
        clear_flag = True

    if clear_flag:
        logger.info("清空h5文件，重新构造")
        result = init_stocks_info()
        put_h5_data(key, result)
    return result


def get_stocks_info():
    """
    从h5文件中读取数据，包括股票基本信息、信号标志、已发送消息标志
    :return: df
    """
    try:
        stocks_info = get_stocks_info_from_h5()
    except (FileNotFoundError, KeyError, TypeError):
        # 解锁h5_lock，防止锁一直被占用，导致程序卡死
        h5_lock.release()  # 解锁
        stocks_info = init_stocks_info()
    return stocks_info


if __name__ == '__main__':
    stocks_info = get_stocks_info()
    result = stocks_info[stocks_info['w_shape_flag'] == 'True']
    print(result['股票名称'])
