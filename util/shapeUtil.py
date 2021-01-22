# -*- coding: UTF-8 -*-
"""
@作者: 石雨风
@时间: 2021/01/05
@功能： 
"""
from util.logUtil import logger

from util.timeUtil import time_to_date


# def get_bigger_data(a, b):
#     if a >= b:
#         return a
#     else:
#         return b
#
#
# def get_smaller_data(a, b):
#     if a >= b:
#         return b
#     else:
#         return a


def is_top_shape(df, high_index):
    """
    判断顶分型
    :param df: df 历史数据
    :param high_index: date 顶点索引
    :return:
    """
    # print(merged_data)
    # try:
    high1_data = df.loc[high_index]
    # except KeyError:
    # 找不到代表当前日期被合并k线了，如果能被合并，代表当前日期不是极值，则不构成顶分型
    # return False
    pre_high1_index = df.index.get_loc(high_index) - 1
    # print(high1_index)
    pre_high1_data = df.iloc[pre_high1_index]
    after_high1_index = df.index.get_loc(high_index) + 1
    after_high1_data = df.iloc[after_high1_index]
    # 顶分型 - 高点是最高的
    if pre_high1_data['high'] < high1_data['high'] and after_high1_data['high'] < high1_data['high']:
        # return True
        # 顶分型 - 低点也是最高的
        if pre_high1_data['low'] < high1_data['low'] and after_high1_data['low'] < high1_data['low']:
            return True
    return False


def is_bottom_shape(df, min_index):
    """
    判断底分型
    :param df: df 历史数据
    :param min_index: date 底点索引
    :return:
    """
    # try:
    min1_data = df.loc[min_index]
    # except KeyError:
    #     找不到代表当前日期被合并k线了，如果能被合并，代表当前日期不是极值，则不构成底分型
    # return False
    pre_min1_index = df.index.get_loc(min_index) - 1
    pre_min1_data = df.iloc[pre_min1_index]
    after_min1_index = df.index.get_loc(min_index) + 1
    after_min1_data = df.iloc[after_min1_index]
    # 底分型 - 高点是最低的
    if pre_min1_data['high'] > min1_data['high'] and after_min1_data['high'] > min1_data['high']:
        # 底分型 - 低点也是最低的
        if pre_min1_data['low'] > min1_data['low'] and after_min1_data['low'] > min1_data['low']:
            return True
    return False


def merge_region_down(region_down):
    """
    只合并包含关系的
    在下降趋势中合并k线，高点取最低的，低点也取最低的
    :param region_down: df
    :return: df
    """
    for i in range(0, len(region_down)):
        if i == len(region_down) - 1:
            continue
        cur_data = region_down.iloc[i]
        try:
            is_merge_day = region_down.loc[cur_data.name]
        except KeyError:
            # 如果获取不到，则证明当前日期已经被合并过了，是无效日期
            continue
        cur_data_high = cur_data['high']
        cur_data_low = cur_data['low']

        after_data = region_down.iloc[i + 1]
        after_data_high = after_data['high']
        after_data_low = after_data['low']

        if cur_data_high >= after_data_high and cur_data_low <= after_data_low:
            # 如果前边包含后边
            result = cur_data.copy()
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
            logger.debug(
                "下降趋势 " + time_to_date(result.name) + ' ' + time_to_date(after_data.name) + ' 向前合并到 ' + time_to_date(
                    result.name))
            return region_down
        elif after_data_high >= cur_data_high and after_data_low <= cur_data_low:
            # 如果后边包含前边
            result = after_data.copy()
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
            logger.debug(
                "下降趋势 " + time_to_date(cur_data.name) + ' ' + time_to_date(result.name) + ' 向后合并到 ' + time_to_date(
                    result.name))
            return region_down
    return region_down


def get_merged_region_down(region_down):
    """
    合并下降趋势k线
    :param region_down:df
    :return:df
    """
    region_down_merged = region_down
    while True:
        before_len = len(region_down_merged)
        region_down_merged = merge_region_down(region_down_merged)
        after_len = len(region_down_merged)
        if after_len < before_len:
            continue
        else:
            break
    return region_down_merged


def merge_region_up(region_up):
    """
    合并上升趋势k线
    :param region_up: df
    :return:df
    """
    for i in range(0, len(region_up)):
        if i == len(region_up) - 1:
            continue
        cur_data = region_up.iloc[i]
        try:
            is_merge_day = region_up.loc[cur_data.name]
        except KeyError:
            # 如果获取不到，则证明当前日期已经被合并过了，是无效日期
            continue
        cur_data_high = cur_data['high']
        cur_data_low = cur_data['low']

        after_data = region_up.iloc[i + 1]
        after_data_high = after_data['high']
        after_data_low = after_data['low']

        if cur_data_high >= after_data_high and cur_data_low <= after_data_low:
            # 如果前边包含后边
            result = cur_data.copy()
            result['high'] = cur_data_high
            result['low'] = after_data_low
            # 因为上升趋势合并时 低点（脚） 取两者的最高点，有可能导致开盘价/收盘价 小于最低点，保证开盘/收盘价在极值之间
            if result['close'] <= result['low']:
                result['close'] = result['low']
            if result['open'] <= result['low']:
                result['open'] = result['low']
            region_up = region_up.drop(after_data.name)
            region_up = region_up.drop(result.name)
            region_up = region_up.append(result)
            region_up.sort_index(inplace=True)  # 按索引排序
            logger.debug(
                "上升趋势 " + time_to_date(result.name) + ' ' + time_to_date(after_data.name) + ' 向前合并到 ' + time_to_date(
                    result.name))
            return region_up
        elif after_data_high >= cur_data_high and after_data_low <= cur_data_low:
            # 如果后边包含前边
            result = after_data.copy()
            result['high'] = after_data_high
            result['low'] = cur_data_low
            # 因为上升趋势合并时 低点（脚） 取两者的最高点，有可能导致开盘价/收盘价 小于最低点，保证开盘/收盘价在极值之间
            if result['close'] <= result['low']:
                result['close'] = result['low']
            if result['open'] <= result['low']:
                result['open'] = result['low']
            region_up = region_up.drop(result.name)
            region_up = region_up.drop(cur_data.name)
            region_up = region_up.append(result)
            region_up.sort_index(inplace=True)  # 按索引排序
            logger.debug(
                "上升趋势 " + time_to_date(cur_data.name) + ' ' + time_to_date(result.name) + ' 向后合并到 ' + time_to_date(
                    result.name))
            return region_up
    return region_up


def get_merged_region_up(region_up):
    """
    上升趋势，递归合并k线。只合并包含关系的
    :param region_up:df
    :return:df
    """
    region_up_merged = region_up
    while True:
        before_len = len(region_up_merged)
        region_up_merged = merge_region_up(region_up_merged)
        after_len = len(region_up_merged)
        if after_len < before_len:
            continue
        else:
            break
    return region_up_merged


def expend_peak_region_up(range_df, high_data, high_index_loc):
    """
    判断极值向右是否存在可合并的k线，如果含有则扩大当前的趋势范围
    :return: int
    """
    offset_up = 1
    temp = high_data.copy()
    for offset_up in range(1, 5):
        if (high_index_loc + offset_up) == len(range_df):  # 代表已经合到边界了，没有下个值了
            break
        after_data = range_df.iloc[high_index_loc + offset_up]
        if temp['high'] >= after_data['high'] and temp['low'] <= after_data['low']:
            temp['low'] = after_data['low']
        else:
            break
    return offset_up


def expend_peak_region_down(range_df, min_data, min_index_loc):
    """
    判断极值向右是否存在可合并的k线，如果含有则扩大当前的趋势范围
    :return: int
    """
    offset_down = 1
    temp = min_data.copy()
    for offset_down in range(1, 5):
        if (min_index_loc + offset_down) == len(range_df):  # 代表已经合到边界了，没有下个值了
            break
        after_data = range_df.iloc[min_index_loc + offset_down]
        if temp['high'] >= after_data['high'] and temp['low'] <= after_data['low']:
            temp['high'] = after_data['high']
        else:
            break
    return offset_down


def do_merge(df):
    for i in range(1, len(df) - 1):  # 因为要与前一个对比增长趋势，所以cur_data从 1 开始

        cur_data = df.iloc[i]
        cur_data_high = cur_data['high']
        cur_data_low = cur_data['low']

        before_data = df.iloc[i - 1]
        before_data_high = before_data['high']
        before_data_low = before_data['low']

        if before_data_high <= cur_data_high and before_data_low <= cur_data_low:
            merge_type = 'up'
        else:
            merge_type = 'down'

        after_data = df.iloc[i + 1]
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
                df = df.drop(after_data.name)
                df = df.drop(result.name)
                df = df.append(result)
                df.sort_index(inplace=True)  # 按索引排序
                logger.debug(
                    "下降趋势 " + time_to_date(result.name) + ' ' + time_to_date(
                        after_data.name) + ' 向前合并到 ' + time_to_date(
                        result.name))
                return df
            elif 'up' == merge_type:
                result['high'] = cur_data_high
                result['low'] = after_data_low
                # 因为上升趋势合并时 低点（脚） 取两者的最高点，有可能导致开盘价/收盘价 小于最低点，保证开盘/收盘价在极值之间
                if result['close'] <= result['low']:
                    result['close'] = result['low']
                if result['open'] <= result['low']:
                    result['open'] = result['low']
                df = df.drop(after_data.name)
                df = df.drop(result.name)
                df = df.append(result)
                df.sort_index(inplace=True)  # 按索引排序
                logger.debug(
                    "上升趋势 " + time_to_date(result.name) + ' ' + time_to_date(
                        after_data.name) + ' 向前合并到 ' + time_to_date(
                        result.name))
                return df
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
                df = df.drop(result.name)
                df = df.drop(cur_data.name)
                df = df.append(result)
                df.sort_index(inplace=True)  # 按索引排序
                logger.debug(
                    "下降趋势 " + time_to_date(cur_data.name) + ' ' + time_to_date(result.name) + ' 向后合并到 ' + time_to_date(
                        result.name))
                return df
            elif 'up' == merge_type:
                result['high'] = after_data_high
                result['low'] = cur_data_low
                # 因为上升趋势合并时 低点（脚） 取两者的最高点，有可能导致开盘价/收盘价 小于最低点，保证开盘/收盘价在极值之间
                if result['close'] <= result['low']:
                    result['close'] = result['low']
                if result['open'] <= result['low']:
                    result['open'] = result['low']
                df = df.drop(result.name)
                df = df.drop(cur_data.name)
                df = df.append(result)
                df.sort_index(inplace=True)  # 按索引排序
                logger.debug(
                    "上升趋势 " + time_to_date(cur_data.name) + ' ' + time_to_date(result.name) + ' 向后合并到 ' + time_to_date(
                        result.name))
                return df
    return df


def merge_all_k_line(df):
    # df_merged = df
    df_length = len(df)
    for i in range(0, df_length):
        df = do_merge(df)
    return df
