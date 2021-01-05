# import logging

# 10.09 - 11.19    1015 1118

from util import dataUtil, shapeUtil

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


# print(region_up)


fields = ('open', 'high', 'low', 'close')
start_date = '2020-12-15'
end_data = '2020-12-30'
code = 'sz.002507'
history_data = dataUtil.attribute_daterange_history(code, start_date, end_data, fields)

# print(history_data)
# print()

high_index = history_data['high'].idxmax()
high_index_loc = history_data.index.get_loc(high_index)
high_data = history_data.iloc[high_index_loc]

low_index = history_data['low'].idxmin()
low_index_loc = history_data.index.get_loc(low_index)
low_data = history_data.iloc[low_index_loc]

region_down = history_data[high_index_loc:low_index_loc]
# print(region_down)
region_up = history_data[low_index_loc + 1:]

region_down_merged = shapeUtil.get_merged_region_down(region_down)
print(region_down_merged)
region_up_merged = shapeUtil.get_merged_region_up(region_up)
print(region_up_merged)
