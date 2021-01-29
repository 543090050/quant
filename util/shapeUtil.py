# -*- coding: UTF-8 -*-
"""
@作者: 石雨风
@时间: 2021/01/05
@功能： 
"""
import pandas as pd

from util.logUtil import logger

from util.timeUtil import time_to_date


def is_top_shape(df, high_index):
    """
    判断顶分型
    :param df: df 历史数据
    :param high_index: date 顶点索引
    :return:
    """
    high1_data = df.loc[high_index]
    pre_high1_index = df.index.get_loc(high_index) - 1
    after_high1_index = df.index.get_loc(high_index) + 1
    if len(df) == after_high1_index or pre_high1_index == -1:  # 给定位置在边界 无法判断分型
        return False

    pre_high1_data = df.iloc[pre_high1_index]
    after_high1_data = df.iloc[after_high1_index]
    # 顶分型 - 高点是最高的
    if pre_high1_data['high'] < high1_data['high'] and after_high1_data['high'] < high1_data['high']:
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
    min1_data = df.loc[min_index]
    pre_min1_index = df.index.get_loc(min_index) - 1
    after_min1_index = df.index.get_loc(min_index) + 1
    if len(df) == after_min1_index or pre_min1_index == -1:  # 给定位置在边界 无法判断分型
        return False
    pre_min1_data = df.iloc[pre_min1_index]
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


def get_trend_type(df, index_loc):
    """
    获取趋势类型，用当前k线与上一k线做比较
    :param df:
    :param index_loc:
    :return:
    """
    cur_data = df.iloc[index_loc]
    cur_data_high = cur_data['high']
    cur_data_low = cur_data['low']

    before_data = df.iloc[index_loc - 1]
    before_data_high = before_data['high']
    before_data_low = before_data['low']

    if before_data_high <= cur_data_high and before_data_low <= cur_data_low:
        merge_type = 'up'
    else:
        merge_type = 'down'
    return merge_type


def do_merge(df):
    """
    合并k线
    :param df:
    :return:
    """
    for i in range(1, len(df) - 1):  # 因为要与前一个对比增长趋势，所以cur_data从 1 开始
        cur_data = df.iloc[i]
        cur_data_high = cur_data['high']
        cur_data_low = cur_data['low']

        merge_type = get_trend_type(df, i)

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
    """
    合并k线
    :param df:
    :return:df
    """
    df_length = len(df)
    for i in range(0, df_length):
        df = do_merge(df)
    return df


def get_up_stroke(start_index_loc, history_data):
    """
    寻找上升笔
    :param start_index_loc:
    :param history_data:
    :return: 上升笔结束的日期
    """
    stroke_flag = False  # 是否形成一个完全的笔（后面是否有新笔产生）
    for i in range(start_index_loc + 1, len(history_data)):
        cur_data = history_data.iloc[i]
        cur_index = cur_data.name
        cur_index_loc = history_data.index.get_loc(cur_index)
        if is_top_shape(history_data, cur_index):
            next_range = history_data.iloc[start_index_loc:cur_index_loc + 1]
            max_data = next_range['high'].max()
            # 找到顶分型 结束步骤1的循环，开始寻找笔的延续
            if max_data == cur_data['high']:
                logger.debug("找到顶分型" + cur_index.strftime('%Y-%m-%d') + "开始寻找笔的延续")
                stroke_flag, next_stroke_end_time = get_up_stroke(0, history_data.iloc[cur_index_loc:])
                if stroke_flag == False:
                    # 在之后的范围未能形成新笔，则在当前笔结束,结束点在范围最后
                    return True, cur_index
                else:
                    return True, next_stroke_end_time
        # 向下寻找底分型才能结束下降笔
        elif is_bottom_shape(history_data, cur_index):
            next_range = history_data.iloc[start_index_loc:cur_index_loc + 1]
            min_data = next_range['low'].min()
            # 判断有效（距离3个位置以上；最低值为前一顶到现底的最低值）后，结束上升笔
            if min_data == cur_data['low'] and (cur_index_loc - start_index_loc) > 3:
                start_data = history_data.iloc[start_index_loc]
                logger.debug("找到之后的底分型" + cur_data.name.strftime('%Y-%m-%d') + "形成下降笔，当前顶分型在" +
                             start_data.name.strftime('%Y-%m-%d') + "完成上升笔")
                stroke_flag = True
                return stroke_flag, start_data.name

    # 能执行到这里，证明没有找到顶 底分型，那就证明是一条单纯的趋势，只比较其实值与结束值即可
    logger.debug("至结束" + history_data.iloc[-1].name.strftime('%Y-%m-%d') + "未形成新笔,上一笔的结束日期为" + history_data.iloc[
        0].name.strftime('%Y-%m-%d'))
    return stroke_flag, history_data.iloc[-1].name


def get_down_stroke(start_index_loc, history_data):
    """
    寻找下降笔
    :param start_index_loc:
    :param history_data:
    :return: 下降笔结束日期
    """
    stroke_flag = False  # 是否形成一个完全的笔（后面是否有新笔产生）
    for i in range(start_index_loc + 1, len(history_data)):
        cur_data = history_data.iloc[i]
        cur_index = cur_data.name
        cur_index_loc = history_data.index.get_loc(cur_index)
        if is_bottom_shape(history_data, cur_index):
            next_range = history_data.iloc[start_index_loc:cur_index_loc + 1]
            min_data = next_range['low'].min()
            # 找到底分型 结束步骤1的循环，开始寻找笔的延续
            if min_data == cur_data['low']:
                logger.debug("找到底分型" + cur_index.strftime('%Y-%m-%d') + "开始寻找笔的延续")
                stroke_flag, next_stroke_end_time = get_down_stroke(0, history_data.iloc[cur_index_loc:])
                if stroke_flag == False:
                    # 在之后的范围未能形成新笔，则在当前笔结束,结束点在范围最后
                    return True, cur_index
                else:
                    # 在之后的范围可以找到新笔，则结束日期为找到新笔之前的那个日期，即next_stroke_end_time
                    return True, next_stroke_end_time
        # 向下寻找顶分型才能结束下降笔
        elif is_top_shape(history_data, cur_index):
            next_range = history_data.iloc[start_index_loc:cur_index_loc + 1]
            max_data = next_range['high'].max()
            # 判断有效（距离3个位置以上；最高值为前一底到现顶的最高值）后，结束下降笔
            if max_data == cur_data['high'] and (cur_index_loc - start_index_loc) > 3:
                start_data = history_data.iloc[start_index_loc]
                logger.debug("找到之后的顶分型" + cur_data.name.strftime('%Y-%m-%d') + "形成上升笔，当前底分型在" +
                             start_data.name.strftime('%Y-%m-%d') + "完成下降笔")
                stroke_flag = True
                return stroke_flag, start_data.name
    logger.debug("至结束" + history_data.iloc[-1].name.strftime('%Y-%m-%d') + "未形成新笔,上一笔的结束日期为" + history_data.iloc[
        0].name.strftime('%Y-%m-%d'))
    return stroke_flag, history_data.iloc[-1].name


def get_stroke(history_data):
    """
    从指定范围开始寻找一笔
    :param history_data:
    :return:
    """
    logger.debug("笔开始的日期" + history_data.iloc[0].name.strftime('%Y-%m-%d'))
    df_length = len(history_data)
    for start_index, start_row in history_data.iterrows():
        start_index_loc = history_data.index.get_loc(start_index)
        if start_index_loc == 0:  # 如果是开始边界，无法与上一个k线比较趋势
            continue

        trend_type = get_trend_type(history_data, start_index_loc)

        if start_index_loc == df_length - 1:  # 最后一天，还未找到笔，那么就比较开始日期到结束日期的趋势
            end_data = history_data.iloc[-1]
            if history_data.iloc[0]['close'] > end_data['close']:
                trend_type = 'down'
            else:
                trend_type = 'up'
            return end_data.name, trend_type

        if trend_type == 'down':
            """
              1.下降趋势，找到底分型(a)以后，从底的位置再往后循环遍历
              2.当找到一个顶分型
                  判断有效（距离3个位置以上；最高值为前一底到现顶的最高值）后，结束下降笔，结点为a底
                  判断无效 继续往后
              3.当找到一个底分型(b)
                  结束步骤1的循环，开始一个新的循环,作为笔的延申
            """
            logger.debug(start_index.strftime('%Y-%m-%d') + "作为下降趋势")
            if is_bottom_shape(history_data, start_index):
                stroke_flag, stroke_end_time = get_down_stroke(start_index_loc, history_data)
                if stroke_flag == True:
                    return stroke_end_time, trend_type
                else:
                    end_data = history_data.iloc[-1]
                    if history_data.iloc[0]['close'] > end_data['close']:
                        trend_type = 'down'
                    else:
                        trend_type = 'up'
                    return end_data.name, trend_type
        elif trend_type == 'up':
            """
            1.上升趋势，找到顶分型(a)以后，从顶的位置再往后循环遍历
            2.当找到一个底分型
              判断有效（距离3个位置以上；最低值为前一顶到现底的最低值）后，结束上升笔，结点为a顶
              判断无效 继续往后
            3.当找到一个顶分型(b)
              结束步骤1的循环，开始一个新的循环,作为笔的延申
            """
            logger.debug(start_index.strftime('%Y-%m-%d') + "作为上升趋势")
            if is_top_shape(history_data, start_index):
                stroke_flag, stroke_end_time = get_up_stroke(start_index_loc, history_data)
                if stroke_flag == True:
                    return stroke_end_time, trend_type
                else:
                    end_data = history_data.iloc[-1]
                    if history_data.iloc[0]['close'] > end_data['close']:
                        trend_type = 'down'
                    else:
                        trend_type = 'up'
                    return end_data.name, trend_type


def get_all_stroke(history_data):
    """
    获取给定数据范围内的所有笔
    :param history_data:
    :return: df
    """
    strokes_df = pd.DataFrame(columns=('start_time', 'end_time', 'shape_type'))
    stroke_start_time = history_data.iloc[0].name
    stroke_end_time, trend_type = get_stroke(history_data)
    stroke_info = [stroke_start_time, stroke_end_time, trend_type]
    strokes_df.loc[stroke_start_time] = stroke_info
    while stroke_end_time != history_data.iloc[-1].name:
        stroke_start_time = stroke_end_time
        next_range = history_data.loc[stroke_start_time:]
        stroke_end_time, trend_type = get_stroke(next_range)
        stroke_info = [stroke_start_time, stroke_end_time, trend_type]
        strokes_df.loc[stroke_start_time] = stroke_info

    # 合并最后的两段一致的笔
    if strokes_df.iloc[-1]['shape_type'] == strokes_df.iloc[-2]['shape_type']:
        info_2 = strokes_df.iloc[-2].copy()
        info_2['end_time'] = strokes_df.iloc[-1]['end_time']
        strokes_df.iloc[-2] = info_2
        strokes_df = strokes_df.drop(strokes_df.iloc[-1].name)
    return strokes_df
