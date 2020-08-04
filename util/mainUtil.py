import dateutil
import matplotlib.pyplot as plt
import pandas as pd

from pTest.util import historyUtil


# 设置基准，目前这里只支持一只股票作为基准
def set_benchmark(context, security):
    context.benchmark = security


def run(context, initialize, handle_data):
    # 最初始所持有的资金
    initial_value = context.cash
    # value 收益
    plt_df = pd.DataFrame(index=pd.to_datetime(context.date_range).strftime('%Y-%m-%d'), columns=['value'])
    initialize(context)
    # 股票的最近一次有效价格，用于处理停牌的情况
    last_prize = {}
    for dt in context.date_range:
        context.dt = dateutil.parser.parse(dt)
        handle_data(context)
        value = context.cash
        for stock in context.positions:
            today_data = historyUtil.get_today_data(context, stock)
            if len(today_data) == 0:
                # 停牌的情况
                today_prize = last_prize[stock]
            else:
                today_prize = today_data['open']
                last_prize[stock] = today_prize
            value += today_prize * context.positions[stock]
        # 画图
        plt_df.loc[dt, 'value'] = value
    # ratio - 收益率
    plt_df['ratio'] = (plt_df['value'] - initial_value) / initial_value
    # 计算基准
    bm_df = historyUtil.attribute_daterange_history(context.benchmark, context.start_date, context.end_date)
    bm_init = bm_df['open'][0]
    plt_df['benchmark_ratio'] = (bm_df['open'] - bm_init) / bm_init
    # 画图
    plt_df[['ratio', 'benchmark_ratio']].plot()
    plt.show()
