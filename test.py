from main_current import get_context
from util import dataUtil, shapeUtil
from util.timeUtil import time_to_date


# import mplfinance


def do_merge(region_down):
    for i in range(1, len(region_down) - 1):  # 因为要与前一个对比增长趋势，所以cur_data从 1 开始

        cur_data = region_down.iloc[i]
        cur_data_high = cur_data['high']
        cur_data_low = cur_data['low']

        before_data = region_down.iloc[i - 1]
        before_data_high = before_data['high']
        before_data_low = before_data['low']

        if before_data_high <= cur_data_high and before_data_low <= cur_data_low:
            merge_type = 'up'
        else:
            merge_type = 'down'

        after_data = region_down.iloc[i + 1]
        after_data_high = after_data['high']
        after_data_low = after_data['low']
        if cur_data_high >= after_data_high and cur_data_low <= after_data_low:
            # 如果前边包含后边
            result = cur_data.copy()
            if 'down' == merge_type:
                result['high'] = after_data_high
                result['low'] = cur_data_low
                # 因为下降趋势合并时 高点（头） 取两者的最低点，有可能导致开盘价/收盘价 大于最低点，保证开盘/收盘价在极值之间
                if result['close'] >= result['high']:
                    result['close'] = result['high']
                if result['open'] >= result['high']:
                    result['open'] = result['high']
                region_down = region_down.drop(after_data.name)
                region_down = region_down.drop(result.name)
                region_down = region_down.append(result)
                region_down.sort_index(inplace=True)  # 按索引排序
                print(
                    "下降趋势 " + time_to_date(result.name) + ' ' + time_to_date(
                        after_data.name) + ' 向前合并到 ' + time_to_date(
                        result.name))
                return region_down
            elif 'up' == merge_type:
                result['high'] = cur_data_high
                result['low'] = after_data_low
                # 因为上升趋势合并时 低点（脚） 取两者的最高点，有可能导致开盘价/收盘价 小于最低点，保证开盘/收盘价在极值之间
                if result['close'] <= result['low']:
                    result['close'] = result['low']
                if result['open'] <= result['low']:
                    result['open'] = result['low']
                region_down = region_down.drop(after_data.name)
                region_down = region_down.drop(result.name)
                region_down = region_down.append(result)
                region_down.sort_index(inplace=True)  # 按索引排序
                print(
                    "上升趋势 " + time_to_date(result.name) + ' ' + time_to_date(
                        after_data.name) + ' 向前合并到 ' + time_to_date(
                        result.name))
                return region_down
        elif after_data_high >= cur_data_high and after_data_low <= cur_data_low:
            # 如果后边包含前边
            result = after_data.copy()
            if 'down' == merge_type:
                result['high'] = cur_data_high
                result['low'] = after_data_low
                # 因为下降趋势合并时 高点（头） 取两者的最低点，有可能导致开盘价/收盘价 大于最低点，保证开盘/收盘价在极值之间
                if result['close'] >= result['high']:
                    result['close'] = result['high']
                if result['open'] >= result['high']:
                    result['open'] = result['high']
                region_down = region_down.drop(result.name)
                region_down = region_down.drop(cur_data.name)
                region_down = region_down.append(result)
                region_down.sort_index(inplace=True)  # 按索引排序
                print(
                    "下降趋势 " + time_to_date(cur_data.name) + ' ' + time_to_date(result.name) + ' 向后合并到 ' + time_to_date(
                        result.name))
                return region_down
            elif 'up' == merge_type:
                result['high'] = after_data_high
                result['low'] = cur_data_low
                # 因为上升趋势合并时 低点（脚） 取两者的最高点，有可能导致开盘价/收盘价 小于最低点，保证开盘/收盘价在极值之间
                if result['close'] <= result['low']:
                    result['close'] = result['low']
                if result['open'] <= result['low']:
                    result['open'] = result['low']
                region_down = region_down.drop(result.name)
                region_down = region_down.drop(cur_data.name)
                region_down = region_down.append(result)
                region_down.sort_index(inplace=True)  # 按索引排序
                print(
                    "上升趋势 " + time_to_date(cur_data.name) + ' ' + time_to_date(result.name) + ' 向后合并到 ' + time_to_date(
                        result.name))
                return region_down
    return region_down


def merge_all_k_line(df_merged):
    # df_merged = df
    df_length = len(df_merged)
    for i in range(0, df_length):
        df_merged = do_merge(df_merged)
    return df_merged


fields = ('open', 'high', 'low', 'close', 'volume')
context = get_context()
code = 'sz.002507'
# start_date = '2020-12-24'
# end_data = '2020-12-31'
# history_data = dataUtil.attribute_daterange_history(code, start_date, end_data, fields)
history_data = dataUtil.attribute_history(context, code, 30, fields)

print(history_data)
print()
history_data = merge_all_k_line(history_data)
print(history_data)
print()
# mplfinance.plot(history_data, type='candle')
