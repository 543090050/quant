import datetime
# import logging

# 10.09 - 11.19    1015 1118
import pandas as pd

from common.Context import Context
from util import dataUtil

# logging.basicConfig(level=logging.DEBUG,
#                     format='%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s')

"""
    1 18
    2 21 
    3 22
    4 23
    5 24
    6 27
    7 28
"""
fields = ('open', 'close', 'high', 'low')
start_date = '2020-12-15'
end_data = '2020-12-30'
code = 'sz.002507'
history_data = dataUtil.attribute_daterange_history(code, start_date, end_data, fields)

print(history_data)
print()

high_index = history_data['high'].idxmax()
high_index_loc = history_data.index.get_loc(high_index)
high_data = history_data.iloc[high_index_loc]

low_index = history_data['low'].idxmin()
low_index_loc = history_data.index.get_loc(low_index)
low_data = history_data.iloc[low_index_loc]

region_down = history_data[high_index:low_index]
# print(region_down)

print(region_down.iloc[7])

region_up = history_data[low_index:]
# print(region_up)

region2 = pd.DataFrame()
for i in range(0, len(region_down)):
    if i == len(region_down):
        continue
    cur_data = region_down.iloc[i]
    cur_data_high = cur_data['high']
    cur_data_low = cur_data['low']

    idnex = i + 1
    print(idnex)
    after_data = region_down.iloc[idnex]
    after_data_high = after_data['high']
    after_data_low = after_data['low']

    if cur_data_high >= after_data_high and cur_data_low <= after_data_low:
        region2 = region2.append(cur_data)
        # print(region2)
    print()
