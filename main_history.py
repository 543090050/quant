import datetime
import os
import sys
import time

import mplfinance
import pandas as pd

import pandas as pd

import common.vars as vs
from strategy.choose import w_shape3
from util import dataUtil, msgUtil, shapeUtil
from util import timeUtil
from util.logUtil import logger
from util.mainUtil import get_context


def get_stocks_info():
    """
    从h5文件中读取数据，包括股票基本信息、信号标志、已发送消息标志
    :return: df
    """
    try:
        stocks_info = dataUtil.get_stocks_info_from_h5()
    except (FileNotFoundError, KeyError):
        # 解锁h5_lock，防止锁一直被占用，导致程序卡死
        dataUtil.h5_lock.release()  # 解锁
        stocks_info = dataUtil.init_stocks_info()
    return stocks_info


def generate_signal(context, all_code_list, stocks_info):
    """
    生成每只股票的策略信号
    """
    for code in zip(all_code_list):
        code = code[0]
        # 获取历史价格
        history_data = dataUtil.attribute_history(context, code, 90)

        # start_date = '2020-09-01'
        # end_data = '2021-01-14'
        # fields = ('open', 'high', 'low', 'close', 'volume')
        # history_data = dataUtil.attribute_daterange_history(code, start_date, end_data,fields)

        history_data = shapeUtil.merge_all_k_line(history_data)  # 合并k线
        # mplfinance.plot(history_data, type='candle')

        # 执行策略
        w_shape3.strategy_w_shape(code, stocks_info, history_data)


def send_msg_by_signal(all_code_list, stocks_info):
    """
    根据信号发送消息
    发送成功时会将gold_msg ， dead_msg置为已发送状态，防止一天发送多次同样的消息
    """
    # 发送的QQ消息
    gold_codes = ""
    dead_codes = ""
    for code in zip(all_code_list):
        code = code[0]
        # 判断信号，并发送消息
        gold_flag = stocks_info.loc[code, 'gold_flag']
        if gold_flag != 'sended':
            if stocks_info.loc[code, 'ma30_flag'] == 'True':
                gold_codes = gold_codes + code + ";"
                stocks_info.loc[code, 'gold_flag'] = 'sended'
            elif stocks_info.loc[code, 'w_shape_flag'] == 'True':
                gold_codes = gold_codes + code + ";"
                stocks_info.loc[code, 'gold_flag'] = 'sended'

        dead_flag = stocks_info.loc[code, 'dead_flag']
        if dead_flag != 'sended' and stocks_info.loc[code, 'ma8_flag'] == 'True':
            dead_codes = dead_codes + code + ";"
            stocks_info.loc[code, 'dead_flag'] = 'sended'

    try:
        final_msg = ''
        if len(gold_codes) > 0:
            final_msg = "符合买入信号: " + gold_codes + '\n'
        if len(dead_codes) > 0:
            final_msg = final_msg + "符合卖出信号: " + dead_codes
        msgUtil.sendMsg(final_msg)
        # 保存h5文件，记录消息标志位，目的是一天只发送一次符合条件的消息
        dataUtil.put_h5_data("stocks_info", stocks_info)
    except Exception as e:
        # logger.exception(sys.exc_info())
        logger.error(e)


def handle_data():
    # time.sleep(5)
    context = get_context()
    stocks_info = get_stocks_info()
    # all_code_list = dataUtil.get_sample_stocks('sz50')['code']
    all_code_list = dataUtil.get_sample_stocks('hs300')['code']
    # all_code_list = dataUtil.get_sample_stocks('zz500')['code']
    # all_code_list = dataUtil.get_sample_stocks('all')['code']
    # all_code_list = pd.Series(['sh.600745', 'sh.603259'])
    # all_code_list = pd.Series(['sh.600021'])

    # 生成信号
    generate_signal(context, all_code_list, stocks_info)
    # 根据信号发送消息
    send_msg_by_signal(all_code_list, stocks_info)


if __name__ == '__main__':
    handle_data()
    # while 1:
    #     # if timeUtil.in_trade_time():
    #     if timeUtil.in_trade_time(time1=vs.STRATEGY_START_TIME, time2=vs.STRATEGY_END_TIME):
    #         start_time = datetime.datetime.now()
    #         handle_data()
    #         end_time = datetime.datetime.now()
    #         logger.info("完成一轮解析,耗时" + str( round((end_time - start_time).seconds / 60, 2)) + "分钟")
