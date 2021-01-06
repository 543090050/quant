# -*- coding: UTF-8 -*-
"""
@作者: 石雨风
@时间: 2021/01/05
@功能： 
"""
import logging

from util.timeUtil import time_to_date

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s')


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
            cur_data['high'] = after_data_high
            cur_data['low'] = cur_data_low
            region_down = region_down.drop(after_data.name)
            region_down = region_down.drop(cur_data.name)
            region_down = region_down.append(cur_data)
            region_down.sort_index(inplace=True)  # 按索引排序
            logging.debug("下降趋势 "+time_to_date(cur_data.name) + ' ' + time_to_date(after_data.name) + ' 向前合并到 ' + time_to_date(
                cur_data.name))
            return region_down
        elif after_data_high >= cur_data_high and after_data_low <= cur_data_low:
            # 如果后边包含前边
            after_data['high'] = cur_data_high
            after_data['low'] = after_data_low
            region_down = region_down.drop(after_data.name)
            region_down = region_down.drop(cur_data.name)
            region_down = region_down.append(after_data)
            region_down.sort_index(inplace=True)  # 按索引排序
            logging.debug("下降趋势 "+time_to_date(cur_data.name) + ' ' + time_to_date(after_data.name) + ' 向后合并到 ' + time_to_date(
                after_data.name))
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
            cur_data['high'] = cur_data_high
            cur_data['low'] = after_data_low
            region_up = region_up.drop(after_data.name)
            region_up = region_up.drop(cur_data.name)
            region_up = region_up.append(cur_data)
            region_up.sort_index(inplace=True)  # 按索引排序
            logging.debug("上升趋势 "+time_to_date(cur_data.name) + ' ' + time_to_date(after_data.name) + ' 向前合并到 ' + time_to_date(
                cur_data.name))
            return region_up
        elif after_data_high >= cur_data_high and after_data_low <= cur_data_low:
            # 如果后边包含前边
            after_data['high'] = after_data_high
            after_data['low'] = cur_data_low
            region_up = region_up.drop(after_data.name)
            region_up = region_up.drop(cur_data.name)
            region_up = region_up.append(after_data)
            region_up.sort_index(inplace=True)  # 按索引排序
            logging.debug("上升趋势 "+time_to_date(cur_data.name) + ' ' + time_to_date(after_data.name) + ' 向后合并到 ' + time_to_date(
                after_data.name))
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
