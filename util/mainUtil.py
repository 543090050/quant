import dateutil
import matplotlib.pyplot as plt
import pandas as pd

# 设置基准，目前这里只支持一只股票作为基准
from common.Context import Context
from util import dataUtil


def get_context():
    try:
        context = Context()
    except IndexError:
        context = Context()
    return context


def set_benchmark(context, security):
    context.benchmark = security


def parse_percent(value):
    """
    将小数转换为百分数
    :param value:
    :return:
    """
    return "%.2f%%" % value


def run(context, initialize, handle_data):
    # 最初始所持有的资金
    initial_cash = context.cash
    # income 收益
    plt_df = pd.DataFrame(index=pd.to_datetime(context.date_range).strftime('%Y-%m-%d'), columns=['income'])
    initialize(context)
    # 股票的最近一次有效价格，用于处理停牌的情况
    last_prize = {}
    for cursor_date in context.date_range:
        # 计算游标日期
        context.cursor_date = dateutil.parser.parse(cursor_date)
        # 执行策略
        handle_data(context)
        available_cash = context.cash
        for stock in context.positions:
            today_data = dataUtil.get_today_data(context, stock)
            if len(today_data) == 0:
                # 停牌的情况
                today_prize = last_prize[stock]
            else:
                today_prize = today_data['open']
                last_prize[stock] = today_prize
            available_cash = available_cash + (today_prize * context.positions[stock])
        plt_df.loc[cursor_date, 'income'] = available_cash

    # yield - 收益率
    plt_df['yield'] = ((plt_df['income'] - initial_cash) / initial_cash) * 100
    # 计算基准
    benchmark_df = dataUtil.attribute_daterange_history(context.benchmark, context.start_date, context.end_date)
    benchmark_init = benchmark_df['open'][0]
    plt_df['benchmark_yield'] = ((benchmark_df['open'] - benchmark_init) / benchmark_init) * 100
    final_income = str(round(plt_df['income'][-1], 2))
    print("最终资产:%s" % final_income)
    print("策略收益%s,基准收益%s" % (parse_percent(plt_df['yield'][-1]), parse_percent(plt_df['benchmark_yield'][-1])))
    # 画图
    plt_df[['yield', 'benchmark_yield']].plot()
    plt.show()
