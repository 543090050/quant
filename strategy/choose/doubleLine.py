# -*- coding: UTF-8 -*-"""@作者: 石雨风@时间: 2020/12/20@功能： 均线选股 - 买入/卖出"""import numpy as npimport pandas as pdfrom common.Context import Contextimport common.vars as vsfrom util import dataUtil, timeUtil, msgUtilimport logginglogging.basicConfig(level=logging.DEBUG,                    format='%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s')filePath = vs.FILE_PATH + 'current_stocks.h5'def handle_data():    try:        context = Context()    except IndexError:        context = Context()    try:        current_stocks = dataUtil.get_h5_data('current_stocks')    except FileNotFoundError:        current_stocks = pd.DataFrame()        current_stocks['gold_flag'] = 'none'        current_stocks['dead_flag'] = 'none'    # all_code_list = dataUtil.get_sample_stocks('all')['code']    all_code_list = dataUtil.get_sample_stocks('hs300')['code']    # all_code_list = dataUtil.get_sample_stocks()['code']    # all_code_list = pd.Series(['sz.000939'])    chunk_len = 50    for code_list in np.array_split(all_code_list, len(all_code_list) / chunk_len + 1):        # 发送的QQ消息        goldMsg = ""        deadMsg = ""        short_code_list = code_list.apply(dataUtil.get_short_code)        # 获取当前价格        current_data_df = dataUtil.get_current_data(short_code_list)        for code in zip(code_list):            code = code[0]            try:                current_data = current_data_df.loc[dataUtil.get_short_code(code)]            except KeyError:                logging.info("未查询到" + code + "今日的实时价格")                continue            # 获取历史价格            history_data = dataUtil.attribute_history(context, code, 30)            # 计算均线            ma8 = history_data['close'][-8:].mean()            ma30 = history_data['close'].mean()            # 填充值            current_stocks.loc[code, 'ma8'] = ma8            current_stocks.loc[code, 'ma30'] = ma30            pre_value = history_data.iloc[-1]['close']  # 上一个交易日的价格            current_stocks.loc[code, 'pre_value'] = pre_value            last_value = current_data['最新价']            current_stocks.loc[code, 'last_value'] = last_value            current_stocks.loc[code, 'last_time'] = current_data['时间']            # todo 每天定时清空消息发送标志            # 执行校验 冲破30 跌破8            if pre_value < ma30 < last_value:                gold_flag = current_stocks.loc[code]['gold_flag']                if gold_flag != 'sended':                    msg = code + "冲破30日均线出现金叉;\n"                    goldMsg = goldMsg + msg                    current_stocks.loc[code, 'gold_flag'] = 'sended'                else:                    logging.info(code + "已发送过金叉消息，不再发送")            if pre_value > ma8 > last_value:                data = current_stocks.loc[code]                dead_flag = current_stocks.loc[code]['dead_flag']                if dead_flag != 'sended':                    msg = code + "跌破8日均线出现死叉;\n"                    deadMsg = deadMsg + msg                    current_stocks.loc[code, 'dead_flag'] = 'sended'                else:                    logging.info(code + "已发送过死叉消息，不再发送")        # 发送qq数据        if len(goldMsg + deadMsg) > 0:            msgUtil.sendMsg(goldMsg + "\n" + deadMsg)    # logging.info(current_stocks)    # 保存h5文件，目的是记录消息标志位，目的是一天只发送一次符合条件的消息    dataUtil.put_h5_data("current_stocks", current_stocks)# handle_data()if __name__ == '__main__':    while 1:        if timeUtil.in_trade_time():            # if timeUtil.in_trade_time(time1='9:00', time2='23:00'):            handle_data()