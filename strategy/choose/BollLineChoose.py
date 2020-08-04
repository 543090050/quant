# 布林带选股策略
import datetime

import baostock as bs
import pandas as pd

from quant.common import G
from quant.common.Context import Context
from quant.util import historyUtil, mainUtil
from quant.util.historyUtil import save_history_k_data

g = G
g.CASH = 100000
g.START_DATE = '2020-01-01'
g.END_DATE = '2020-07-20'
g.FILE_PATH = 'D:/stockFile/'  # 股票文件的存储路径

g.trade_cal = historyUtil.get_trade_cal()
context = Context(g.CASH, g.START_DATE, g.END_DATE, g.trade_cal)

# 股票文件的存储路径
FILE_PATH = 'D:/stockFile/'


# 下载成分股 上证50；沪深300；中证500
def download_sample_stocks(sample_name='sz50'):
    bs.login()
    if sample_name == 'sz50':
        filename = FILE_PATH + "/sz50_stocks.csv"
        rs = bs.query_sz50_stocks()
    elif sample_name == 'hs300':
        filename = FILE_PATH + "/sz50_stocks.csv"
        rs = bs.query_hs300_stocks()
    else:
        filename = FILE_PATH + "/sz50_stocks.csv"
        rs = bs.query_zz500_stocks()

    # bs.logout()

    stocks = []
    while (rs.error_code == '0') & rs.next():
        stocks.append(rs.get_row_data())
    result = pd.DataFrame(stocks, columns=rs.fields)
    result.to_csv(filename, encoding="gbk", index=False)

    # 开始下载样本股票的详细历史信息
    sample_stocks = pd.read_csv(filename, encoding='gbk')['code']
    for value in zip(sample_stocks):
        stock_code = value[0]
        save_history_k_data(stock_code)


def run():
    mainUtil.set_benchmark(context, 'sh.601318')
    g.security = 'sh.601318'
    # 均线时间（天）
    g.M = 20
    # 布林带宽度
    g.k = 1.7

    context.cursor_date = datetime.datetime.now()
    print(context.cursor_date)

    sr = historyUtil.attribute_history(context, g.security, g.M)['close']

    print(sr)


run()
