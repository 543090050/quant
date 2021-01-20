import datetime
import multiprocessing
import os
import sys
import time

import mplfinance
import pandas as pd
import numpy as np
import pandas as pd

import common.vars as vs
from strategy.choose import w_shape3
from util import dataUtil, msgUtil, shapeUtil
from util import timeUtil
from util.logUtil import logger
from util.mainUtil import get_context


def handle_list(context, code_list, stocks_info):
    short_code_list = code_list.apply(dataUtil.get_short_code)  # 把 sh.600000 替换成  sh600000
    # 获取当前价格
    current_data_df = dataUtil.get_current_data(short_code_list)
    # 遍历每个小组内的code
    for code in zip(code_list):
        code = code[0]
        # 获取历史价格
        history_data = dataUtil.attribute_history(context, code, 90)
        history_data = shapeUtil.merge_all_k_line(history_data)  # 合并k线
        try:
            # 填充基本信息
            current_data = dataUtil.update_base_info(stocks_info, current_data_df, code)
        except KeyError:
            logger.error("未查询到" + code + "今日的实时价格")
            continue

        # 执行策略
        w_shape3.strategy_w_shape(code, current_data, history_data)


def generate_signal(all_code_list):
    """
    生成每只股票的策略信号
    """

    pool = multiprocessing.Pool(processes=5)  # 创建线程池

    context = get_context()

    stocks_info = dataUtil.get_stocks_info()
    # 将全部code按每组chunk_len个进行分组
    chunk_len = 50
    for code_list in np.array_split(all_code_list, len(all_code_list) / chunk_len + 1):
        # handle_list(context, code_list, stocks_info)
        pool.apply_async(handle_list, (context, code_list, stocks_info))
    pool.close()
    pool.join()


def handle_data():
    # all_code_list = dataUtil.get_sample_stocks('sz50')['code']
    all_code_list = dataUtil.get_sample_stocks('hs300')['code']
    # all_code_list = dataUtil.get_sample_stocks('zz500')['code']
    # all_code_list = dataUtil.get_sample_stocks('all')['code']
    # all_code_list = pd.Series(['sh.600745', 'sh.603259'])
    # all_code_list = pd.Series(['sh.601236'])

    # 生成信号
    generate_signal(all_code_list)
    # 根据信号发送消息
    msgUtil.send_msg_by_signal()


if __name__ == '__main__':
    handle_data()
    # while 1:
    #     # if timeUtil.in_trade_time():
    #     if timeUtil.in_trade_time(time1=vs.STRATEGY_START_TIME, time2=vs.STRATEGY_END_TIME):
    #         start_time = datetime.datetime.now()
    #         handle_data()
    #         end_time = datetime.datetime.now()
    #         logger.info("完成一轮解析,耗时" + str( round((end_time - start_time).seconds / 60, 2)) + "分钟")
