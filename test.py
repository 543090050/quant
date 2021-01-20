from main_current import get_context
from main_history import get_stocks_info
from util import dataUtil, shapeUtil
from util.timeUtil import time_to_date

# import mplfinance

stocks_info = get_stocks_info()
print(len(stocks_info))
result = stocks_info[stocks_info['w_shape_flag'] == 'True']
print(result)
