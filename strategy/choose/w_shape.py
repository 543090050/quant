# -*- coding: UTF-8 -*-
"""
@作者: 石雨风
@时间: 2020/12/28
@功能： 
"""
import datetime
import logging

# 10.09 - 11.19    1015 1118
from common.Context import Context
from util import dataUtil

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s')


def add_w_data_info(result, info):
    """
    将时间信息添加到set集合里，去重并取最大范围。对于小一，小二，大二相同的日期信息，取最前面的大二日期
    """
    info_list = info.split(' ')
    high1_index = info_list[0]
    min1_index = info_list[1]
    high2_index = info_list[2]
    min2_index = info_list[3]
    if len(result) == 0:
        result.add(info)
    else:
        add_flag = False
        for exist in result:
            exist_list = exist.split(' ')
            exist_high1 = exist_list[0]
            exist_low1 = exist_list[1]
            exist_high2 = exist_list[2]
            exist_low2 = exist_list[3]
            if min1_index == exist_low1 and high2_index == exist_high2 and min2_index == exist_low2:
                exist_high1_time = datetime.datetime.strptime(exist_high1, "%Y-%m-%d")
                high1_time = datetime.datetime.strptime(high1_index, "%Y-%m-%d")
                if exist_high1_time > high1_time:
                    # 如果已经存在的在当前日期的后面，则为已存在的是小范围，当前为大范围。则删除已存在的
                    result.remove(exist)
                    result.add(info)
                    add_flag = True
                    break
                else:
                    add_flag = True
        if not add_flag:
            result.add(info)
    # logging.info(result)


fields = ('open', 'close', 'high', 'low', 'volume')
context = Context()
result = set()

"""
1、总时间范围history_data日期数固定，游标范围不固定，游标范围从最小 data_range = 4 开始，到 data_range = 日期总数len(history_data)
2、移动游标范围data_range，使data_range从头到尾走一遍总时间范围history_data
    range的索引从 range_index = 0 开始，到 range_index = len(history_data) - data_range结束
    e.g.
        当总时间范围 len(history_data) = 10 ,游标范围range长度为4，需要遍历的情况
        range_df = history_data.iloc[0:3]
        range_df = history_data.iloc[1:4]
        ....
        range_df = history_data.iloc[5:8]
        range_df = history_data.iloc[6:9]
3、固定一个游标范围range以后，确定切点(将游标范围分成两个区域)，切片从 split = 1 开始，到split = range的最大数-1结束(确保区域二是两个坐标组成的区域)
    比如游标范围是 0 - 5 ,那么切点可以是1，2，3。
    e.g.
        当split=1时，region1为0-1；region2为2-4
        当split=2时，region1为0-2；region2为3-4
4、分割成两个区间后
    1.	找区间1的极小值min1，为左底
    2.	找区间2的极小值min2，为右底
    3.	判断min1 < min2
    4.	找左底与右底之间区域的极大值 max2
    5.  找区间1的极大值 max1
    6.	判断max1 > max2
"""

# 6开头是sh；0,3开头是sz
code = 'sz.002541'  # {'2020-09-21 2020-11-26 2020-12-11 2020-12-30 '}
# code = 'sz.300449'
# code = 'sz.300633'
# code = 'sz.002166'
# code = 'sh.600338'
start_date = '2020-09-18'
end_data = '2020-12-31'
history_data = dataUtil.attribute_daterange_history(code, start_date, end_data, fields)
# history_data = history_data.iloc[::-1]  # 将df倒序
# logging.info(history_data)
logging.info(start_date + "-" + end_data + ' 总天数: ' + str(len(history_data)))

for data_range in range(69, len(history_data) + 1):  # data_range 确定游标范围长度  默认从15开始
    logging.info('游标天数======================================================================:' + str(data_range))
    for data_range_index in range(0, len(history_data) - data_range + 1):  # 用 游标范围 遍历 总数据
        # 得到游标范围内的df
        range_df = history_data[data_range_index:data_range_index + data_range]
        logging.info("时间范围:" + range_df.index[0].strftime('%Y-%m-%d') + "-" + range_df.index[-1].strftime('%Y-%m-%d'))

        for split in range(2, data_range - 1):  # 分割索引从2开始，保证区域内至少有1个值
            region1 = range_df[0:split]
            region2 = range_df[split:]

            high1_index = region1['high'].idxmax()
            high1_data = region1.loc[high1_index]
            min1_index = region1['low'].idxmin()
            min1_data = region1.loc[min1_index]
            min2_index = region2['low'].idxmin()
            min2_data = region2.loc[min2_index]

            if high1_index.strftime('%Y-%m-%d') == '2020-09-21' and min1_index.strftime(
                    '%Y-%m-%d') == '2020-11-26' and min2_index.strftime('%Y-%m-%d') == '2020-12-30':
                c = 1

            min2_index_iloc = history_data.index.get_loc(min2_index)
            buy_day = history_data.iloc[min2_index_iloc + 1]
            if buy_day['open'] > buy_day['close']:
                continue
            region3 = range_df.loc[min1_index:min2_index]
            if len(region3) < 3:  # 区域3需要掐头去尾掉区域一二的最小值，这里的判断保证区域三内至少有值
                continue
            region3 = region3[1:-1]  # 去掉 区域三 头尾的最小值

            high2_index = region3['high'].idxmax()
            high2_data = region3.loc[high2_index]

            high1 = high1_data['high']
            min1 = min1_data['low']
            high2 = high2_data['high']
            min2 = min2_data['low']

            # 开始校验----------------------------------------------------------------------------------------------------
            # 如果极值在起始边界，则为无效数据，跳过下面分型的校验。
            if high1_index.strftime('%Y-%m-%d') == start_date or min1_index.strftime('%Y-%m-%d') == start_date:
                continue

            # 四个极点的顺序
            time_order_flag = False
            if high1_index < min1_index < high2_index < min2_index:
                time_order_flag = True
            else:
                continue

            # 确认是w形态
            w_shape_flag = False
            if min1 <= min2 and high1 > high2:  # w 形态的四个主要点，高一低一；高二低二
                w_shape_flag = True
            else:
                continue

            # 识别一顶分型
            top1_flag = False
            if dataUtil.is_top_shape(history_data, high1_index):
                # print('top:'+ str(high1_index))
                top1_flag = True
            else:
                continue

            # 识别一底分型
            bottom1_flag = False
            if dataUtil.is_bottom_shape(history_data, min1_index):
                # print('low:'+str(min1_index))
                bottom1_flag = True
            else:
                continue

            # 识别二顶分型
            top2_flag = False
            if dataUtil.is_top_shape(history_data, high2_index):
                # print('top2:'+ str(high2_index))
                top2_flag = True
            else:
                continue

            # 识别二底分型
            bottom2_flag = False
            if dataUtil.is_bottom_shape(history_data, min2_index):
                # print('low2:'+str(min1_index))
                bottom2_flag = True
            else:
                continue

            # 一顶和一底之间至少有 3 条k线。如果包括两个极点，就是5条k线
            top1_bottom1_flag = False
            if history_data.index.get_loc(min1_index) - history_data.index.get_loc(high1_index) > 3:
                top1_bottom1_flag = True
                # print(str(high1_index) + " " + str(min1_index))
            else:
                continue

            # 一底和二顶之间至少有 3 条k线。如果包括两个极点，就是5条k线
            bottom1_top2_flag = False
            if history_data.index.get_loc(high2_index) - history_data.index.get_loc(min1_index) > 3:
                bottom1_top2_flag = True
            else:
                continue

            # 二顶和二底之间至少有 3 条k线。如果包括两个极点，就是5条k线
            top2_bottom2_flag = False
            if history_data.index.get_loc(min2_index) - history_data.index.get_loc(high2_index) > 3:
                top2_bottom2_flag = True
            else:
                continue

            # 如果通过前面的校验，则构造结果信息
            info = str(high1_index).replace(' 00:00:00', ' ') + str(min1_index).replace(
                ' 00:00:00', ' ') + str(
                high2_index).replace(' 00:00:00', ' ') + str(min2_index).replace(
                ' 00:00:00', ' ')
            # add_w_data_info(result, info)  # 去重且取最大
            result.add(info)  # 直接加如到结果集

logging.info(result)
