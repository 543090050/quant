# 上下文对象，记录基本信息
class Context:
    def __init__(self, cash, start_date, end_date, trade_cal):
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
        self.cursor_date = None
