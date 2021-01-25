from main_current import get_context
from util import baoStockUtil, shapeUtil
from util.timeUtil import time_to_date

# import mplfinance

stocks_info = baoStockUtil.get_stocks_info()
print(len(stocks_info))
result = stocks_info[stocks_info['w_shape_flag'] == 'True']
print(result['股票名称'])
