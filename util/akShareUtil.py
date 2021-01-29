import akshare as ak
import pandas as pd

# pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)


def get_code_info(code):
    """
    根据sz002419截取市场和编码
    :param code:
    :return: sz,002149
    """
    market = code[0:2]
    stock = code[-6:]
    return market, stock


def get_fund_flow(code):
    """
    获取个股资金流向
    :param code:
    :return:
    """
    market, stock = get_code_info(code)
    df = ak.stock_individual_fund_flow(stock, market)
    df.set_index(["日期"], inplace=True)  # 将日期作为索引
    return df


if __name__ == '__main__':
    code = 'sz002419'
    df = get_fund_flow(code)
    print(df)
