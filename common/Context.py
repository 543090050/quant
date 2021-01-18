"""上下文对象，记录基本信息"""
import datetime

import dateutil

from util import dataUtil, timeUtil


class Context:

    def __init__(self, cash=100000, start_date=timeUtil.get_pre_day().strftime("%Y-%m-%d"),
                 end_date=datetime.datetime.now().strftime("%Y-%m-%d")):
        """
        初始化
        :param cash: 初始金额 int
        :param start_date: 起始时间 str
        :param end_date: 结束时间 str
        """
        trade_cal = dataUtil.get_trade_cal()
        self.cash = cash
        self.start_date = start_date
        self.end_date = end_date
        # 持仓信息，当作一个字典,{股票代码:持有数量}
        self.positions = {}
        # 参考基准
        self.benchmark = None
        # 交易日期
        self.trade_cal = trade_cal
        # 过滤出start_date - end_date间的所有交易日
        self.date_range = trade_cal[(trade_cal['is_trading_day'] == 1) &
                                    (trade_cal['calendar_date'] >= start_date) &
                                    (trade_cal['calendar_date'] <= end_date)]['calendar_date'].values
        # 游标日期日期(type date)。比如获取某天(cursor_date)的股票信息
        # 取昨天的交易日期，因为今天的k线数据还没有更新到文件里
        # self.cursor_date = dateutil.parser.parse(self.date_range[-2])
        ''' 如果今日是交易日则游标为trade_cal中的倒数第二个交易日（因为倒数第一日为今日，今日数据未更新在历史文件里）
            如果今日是非交易日游标为trade_cal中的倒数第一个交易日
        '''
        # 今日是否为交易日标志
        today_trade_flag = trade_cal[trade_cal['calendar_date'] == end_date]['is_trading_day'].values
        if today_trade_flag == 1:
            # 今日为交易日
            self.cursor_date = dateutil.parser.parse(self.date_range[-2])
        else:
            # 今日为非交易日
            self.cursor_date = dateutil.parser.parse(self.date_range[-1])

# def get_context():
#     try:
#         context = Context()
#     except IndexError:
#         context = Context()
#     return context
