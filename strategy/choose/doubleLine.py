# -*- coding: UTF-8 -*-"""@作者: 石雨风@时间: 2020/12/20@功能： 均线选股 - 买入/卖出"""import numpy as npimport pandas as pdfrom common.Context import Contextfrom util import dataUtildef get_short_code(x):    """    把 sh.600000 替换成  sh600000    """    return x.replace(".", "")def handle_data():    context = Context()    stocks = pd.DataFrame()    all_code_list = dataUtil.get_sample_stocks()['code']    # all_code_list = pd.Series(['sz.000939'])    chunk_len = 51    for code_list in np.array_split(all_code_list, len(all_code_list) / chunk_len + 1):        short_code_list = code_list.apply(get_short_code)        # 获取当前价格        current_data_df = dataUtil.get_current_data(short_code_list)        for code in zip(code_list):            code = code[0]            try:                current_data = current_data_df.loc[get_short_code(code)]            except KeyError:                print("未查询到" + code + "今日的实时价格")                continue            # 获取历史价格            history_data = dataUtil.attribute_history(context, code, 30)            # 计算均线            ma8 = history_data['close'][-8:].mean()            ma30 = history_data['close'].mean()            # 填充值            stocks.loc[code, 'ma8'] = ma8            stocks.loc[code, 'ma30'] = ma30            pre_value = history_data.iloc[-1]['close']  # 上一个交易日的价格            stocks.loc[code, 'pre_value'] = pre_value            last_value = current_data['最新价']            stocks.loc[code, 'last_value'] = last_value            stocks.loc[code, 'last_time'] = current_data['时间']            # 执行校验 冲破30 跌破8            if pre_value < ma30 < last_value:                print(code + "冲破30日均线出现金叉")            if pre_value > ma8 > last_value:                print(code + "跌破8日均线出现死叉")    print(stocks)handle_data()