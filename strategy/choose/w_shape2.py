import datetime

import mplfinance

from common.Context import Context
from util import dataUtil, shapeUtil
from util.logUtil import logger


"""
汉邦高科、开立医疗、莱茵生物、西藏珠峰、海康威视、广汽集团、牧原股份
晶澳科技、青龙商行、中银证券、金字火腿、一恒药业、大族激光、鸿路钢构、st金刚
"""

def handle_data():
    fields = ('open', 'high', 'low', 'close', 'volume')
    context = Context()

    # 6开头是sh；0,3开头是sz
    code = 'sz.002541'  # {'2020-09-21 2020-11-26 2020-12-11 2020-12-30 '}
    start_date = '2020-09-01'
    end_data = '2020-12-31'
    history_data = dataUtil.attribute_daterange_history(code, start_date, end_data, fields)
    # history_data = dataUtil.attribute_history(context, code, 90)
    # logger.info(history_data)
    logger.info(start_date + "-" + end_data + ' 总天数: ' + str(len(history_data)))

    for data_range in range(15, len(history_data) + 1):  # data_range 确定游标范围长度  默认从15开始
        range_df = history_data[-data_range:]
        logger.info('游标天数=====:' + str(data_range)+" 时间范围: " + range_df.index[0].strftime('%Y-%m-%d') + " - " + range_df.index[-1].strftime('%Y-%m-%d'))
        # logger.info()

        # TODO 起始范围有待商榷
        for split in range(2, data_range - 1):  # 分割索引从2开始，保证区域内至少有1个值
            region1 = range_df[0:split]
            region2 = range_df[split:]

            high1_index = region1['high'].idxmax()
            high1_data = region1.loc[high1_index]
            min1_index = region1['low'].idxmin()
            min1_data = region1.loc[min1_index]
            min2_index = region2['low'].idxmin()
            min2_data = region2.loc[min2_index]

            # TODO debug找日期
            # if high1_index.strftime('%Y-%m-%d') == '2020-09-21' and min1_index.strftime(
            #         '%Y-%m-%d') == '2020-11-26' and min2_index.strftime('%Y-%m-%d') == '2020-12-30':
            #     c = 1
            # else:
            #     continue

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
            if high1_index.strftime('%Y-%m-%d') == range_df.index[0].strftime('%Y-%m-%d') \
                    or min2_index.strftime('%Y-%m-%d') == range_df.index[-1].strftime('%Y-%m-%d'):
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

            # 合并k线
            region_up_1 = range_df[0:range_df.index.get_loc(high1_index) + 1]
            region_up_1_merged = shapeUtil.get_merged_region_up(region_up_1)
            # 如果极值在起始边界，则为无效数据，跳过下面分型的校验。
            if high1_index.strftime('%Y-%m-%d') == region_up_1_merged.index[0].strftime('%Y-%m-%d'):
                continue
            # mplfinance.plot(region_up_1_merged, type='candle')

            region_down_1 = range_df[range_df.index.get_loc(high1_index) + 1:range_df.index.get_loc(min1_index) + 1]
            region_down_1_merged = shapeUtil.get_merged_region_down(region_down_1)
            # mplfinance.plot(region_down_1_merged, type='candle')

            region_up_2 = range_df[range_df.index.get_loc(min1_index) + 1:range_df.index.get_loc(high2_index) + 1]
            region_up_2_merged = shapeUtil.get_merged_region_up(region_up_2)
            # mplfinance.plot(region_up_2_merged, type='candle')

            region_down_2 = range_df[range_df.index.get_loc(high2_index) + 1:range_df.index.get_loc(min2_index) + 1]
            region_down_2_merged = shapeUtil.get_merged_region_down(region_down_2)
            # mplfinance.plot(region_down_2_merged, type='candle')

            region_up_3 = range_df[range_df.index.get_loc(min2_index) + 1:]
            region_up_3_merged = shapeUtil.get_merged_region_up(region_up_3)
            # 如果极值在起始边界，则为无效数据，跳过下面分型的校验。
            if high2_index.strftime('%Y-%m-%d') == region_up_3_merged.index[-1].strftime('%Y-%m-%d'):
                continue
            # mplfinance.plot(region_up_3_merged, type='candle')
            buy_day = region_up_3.iloc[0]
            if buy_day['open'] > buy_day['close']:
                continue

            region_merged = region_up_1_merged.append(region_down_1_merged).append(region_up_2_merged).append(
                region_down_2_merged).append(region_up_3_merged)
            # mplfinance.plot(region_merged, type='candle')

            # 识别一顶分型
            top1_flag = False
            if dataUtil.is_top_shape(region_merged, high1_index):
                # print('top:'+ str(high1_index))
                top1_flag = True
            else:
                continue

            # 识别一底分型
            bottom1_flag = False
            if dataUtil.is_bottom_shape(region_merged, min1_index):
                # print('low:'+str(min1_index))
                bottom1_flag = True
            else:
                continue

            # 识别二顶分型
            top2_flag = False
            if dataUtil.is_top_shape(region_merged, high2_index):
                # print('top2:'+ str(high2_index))
                top2_flag = True
            else:
                continue

            # 识别二底分型
            bottom2_flag = False
            if dataUtil.is_bottom_shape(region_merged, min2_index):
                # print('low2:'+str(min1_index))
                bottom2_flag = True
            else:
                continue

            # 一顶和一底之间至少有 3 条k线。如果包括两个极点，就是5条k线
            top1_bottom1_flag = False
            if region_merged.index.get_loc(min1_index) - region_merged.index.get_loc(high1_index) > 3:
                top1_bottom1_flag = True
                # print(str(high1_index) + " " + str(min1_index))
            else:
                continue

            # 一底和二顶之间至少有 3 条k线。如果包括两个极点，就是5条k线
            bottom1_top2_flag = False
            if region_merged.index.get_loc(high2_index) - region_merged.index.get_loc(min1_index) > 3:
                bottom1_top2_flag = True
            else:
                continue

            # 二顶和二底之间至少有 3 条k线。如果包括两个极点，就是5条k线
            top2_bottom2_flag = False
            if region_merged.index.get_loc(min2_index) - region_merged.index.get_loc(high2_index) > 3:
                top2_bottom2_flag = True
            else:
                continue

            # 如果通过前面的校验，则加到结果集
            info = str(high1_index).replace(' 00:00:00', ' ') + str(min1_index).replace(
                ' 00:00:00', ' ') + str(
                high2_index).replace(' 00:00:00', ' ') + str(min2_index).replace(
                ' 00:00:00', ' ')
            # add_w_data_info(result, info)  # 去重且取最大
            # mplfinance.plot(region_merged, type='candle')
            # result.add(info)
            return info
    return '未找到符合条件的时间范围'


if __name__ == '__main__':
    logger.info("最终结果：" + handle_data())
