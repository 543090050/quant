import numpy as np
import common.vars as vs
from common.Context import Context
from strategy.choose import doubleLine
from util import dataUtil, msgUtil
from util import timeUtil
from util.mainUtil import get_context

from util.logUtil import logger


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
    # 将全部code按每组chunk_len个进行分组
    chunk_len = 50
    for code_list in np.array_split(all_code_list, len(all_code_list) / chunk_len + 1):
        short_code_list = code_list.apply(dataUtil.get_short_code)  # 把 sh.600000 替换成  sh600000
        # 获取当前价格
        current_data_df = dataUtil.get_current_data(short_code_list)
        # 遍历每个小组内的code
        for code in zip(code_list):
            code = code[0]
            # 获取历史价格
            history_data = dataUtil.attribute_history(context, code, 30)
            try:
                # 更新基本信息
                current_data = dataUtil.update_base_info(stocks_info, current_data_df, code)
            except KeyError:
                logger.error("未查询到" + code + "今日的实时价格")
                continue

            # 执行策略
            doubleLine.strategy_ma30(code, stocks_info, current_data, history_data)
            doubleLine.strategy_ma8(code, stocks_info, current_data, history_data)


def send_msg_by_signal(stocks_info):
    """
    根据信号发送消息
    发送成功时会将gold_msg ， dead_msg置为已发送状态，防止一天发送多次同样的消息
    """
    # 发送的QQ消息
    gold_codes = ""
    dead_codes = ""
    for code in zip(stocks_info.index):
        code = code[0]
        # 判断信号，并发送消息
        gold_flag = stocks_info.loc[code, 'gold_flag']
        if gold_flag != 'sended' and stocks_info.loc[code, 'ma30_flag'] == 'True':
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
        logger.error(e)


def handle_data():
    # time.sleep(5)
    context = get_context()
    stocks_info = get_stocks_info()

    # all_code_list = dataUtil.get_sample_stocks('all')['code']
    # all_code_list = dataUtil.get_sample_stocks('hs300')['code']
    all_code_list = dataUtil.get_sample_stocks('sz50')['code']
    # all_code_list = pd.Series(['sh.600036'])

    # 生成信号
    generate_signal(context, all_code_list, stocks_info)
    # 根据信号发送消息
    send_msg_by_signal(stocks_info)


if __name__ == '__main__':
    while 1:
        # if timeUtil.in_trade_time():
        if timeUtil.in_trade_time(time1=vs.STRATEGY_START_TIME, time2=vs.STRATEGY_END_TIME):
            handle_data()
