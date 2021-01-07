import mplfinance

from common.Context import get_context
from util import dataUtil, shapeUtil
from util.logUtil import logger

"""
汉邦高科sz.300449、开立医疗sz.300633、莱茵生物sz.002166、西藏珠峰sh.600338、海康威视sz.002415、广汽集团sh.601238、牧原股份sz.002714
晶澳科技sz.002459、青龙商行、中银证券、金字火腿、一恒药业、大族激光、鸿路钢构、st金刚

莱茵生物sz.002166,海康威视sz.002415,广汽集团sh.601238
"""


def handle_data():
    fields = ('open', 'high', 'low', 'close', 'volume')
    context = get_context()
    result = set()

    # 6开头是sh；0,3开头是sz

    code = 'sz.002459'

    start_date = '2020-08-01'
    end_data = '2020-12-10'
    history_data = dataUtil.attribute_daterange_history(code, start_date, end_data, fields)
    # history_data = dataUtil.attribute_history(context, code, 90)
    # logger.info(history_data)
    logger.info(start_date + "-" + end_data + ' 总天数: ' + str(len(history_data)))

    for data_range in range(46, len(history_data) + 1):  # data_range 确定游标范围长度  默认从15开始
        range_df = history_data[-data_range:]
        logger.info('游标天数=====:' + str(data_range) + " 时间范围: " + range_df.index[0].strftime('%Y-%m-%d') + " - " +
                    range_df.index[-1].strftime('%Y-%m-%d'))
        # logger.info()

        for split in range(4, data_range - 4):  # 分割索引从4开始，保证区域内至少有3个值
            region1 = range_df[0:split]
            region2 = range_df[split:]

            high1_index = region1['high'].idxmax()
            high1_data = region1.loc[high1_index]
            min1_index = region1['low'].idxmin()
            min1_data = region1.loc[min1_index]
            min2_index = region2['low'].idxmin()
            min2_data = region2.loc[min2_index]

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

            # info = str(high1_index).replace(' 00:00:00', ' ') + str(min1_index).replace(
            #     ' 00:00:00', ' ') + str(
            #     high2_index).replace(' 00:00:00', ' ') + str(min2_index).replace(
            #     ' 00:00:00', ' ')
            # if info in result:
            #     continue

            # TODO debug找日期
            if high1_index.strftime('%Y-%m-%d') == '2020-11-03' and min1_index.strftime('%Y-%m-%d') == '2020-11-19':
                pass
            else:
                continue

            # 开始校验====================================================================================================
            # 如果极值在起始边界，则为无效数据，跳过下面分型的校验。
            if high1_index.strftime('%Y-%m-%d') == range_df.index[0].strftime('%Y-%m-%d') \
                    or min2_index.strftime('%Y-%m-%d') == range_df.index[-1].strftime('%Y-%m-%d'):
                logger.debug('最大值: ' + str(high1_index) + ' 或 最小值: ' + str(min2_index) + '在边界')
                continue

            # 四个极点的顺序
            if high1_index < min1_index < high2_index < min2_index:
                pass
            else:
                logger.debug(
                    '四个极值的时间顺序 ' + str(high1_index) + ' ' + str(min1_index) + ' ' + str(high2_index) + ' ' + str(
                        min2_index) + ' 错误')
                continue

            # 确认是w形态
            if min1 <= min2 and high1 > high2:  # w 形态的四个主要点，高一低一；高二低二
                pass
            else:
                logger.debug('四个极点 ' + str(high1) + ' ' + str(min1) + ' ' + str(high2) + ' ' + str(min2) + ' 错误')
                continue

            # high1要是整个范围内的最大值
            if high1_data['high'] < range_df['high'].max():
                logger.debug('high1 ' + str(high1_index) + '不是范围内的最大值')
                continue

            # min1要是整个范围内的最小值
            if min1_data['low'] > range_df['low'].min():
                logger.debug('min1 ' + str(min1_index) + '不是范围内的最小值')
                continue

            # min2要是high2到结束间的最小值
            region_high2_end = range_df.iloc[range_df.index.get_loc(high2_index) + 1:]
            if min2_data['low'] > region_high2_end['low'].min():
                logger.debug('min2 ' + str(min2_index) + ' 不是high2到结束区间的最小值')
                continue

            # 合并k线========================================================================================================
            high1_index_loc = range_df.index.get_loc(high1_index)
            high2_index_loc = range_df.index.get_loc(high2_index)
            min1_index_loc = range_df.index.get_loc(min1_index)
            min2_index_loc = range_df.index.get_loc(min2_index)

            # 判断极值向右是否存在可合并的k线，如果含有则扩大当前的趋势范围
            offset_up1 = shapeUtil.expend_peak_region_up(range_df, high1_data, high1_index_loc)
            region_up_1 = range_df[0:high1_index_loc + offset_up1]
            region_up_1_merged = shapeUtil.get_merged_region_up(region_up_1)

            # 如果极大值在左边界，则为无效数据，跳过下面分型的校验。
            if high1_index.strftime('%Y-%m-%d') == region_up_1_merged.index[0].strftime('%Y-%m-%d'):
                continue

            # 判断极值向右是否存在可合并的k线，如果含有则扩大当前的趋势范围
            offset_down1 = shapeUtil.expend_peak_region_down(range_df, min1_data, min1_index_loc)
            region_down_1 = range_df[high1_index_loc + offset_up1:min1_index_loc + offset_down1]
            region_down_1_merged = shapeUtil.get_merged_region_down(region_down_1)
            if len(region_down_1_merged) == 0:  # 当前区域k线被上一个区域全合并了
                continue

            # 判断极值向右是否存在可合并的k线，如果含有则扩大当前的趋势范围
            offset_up2 = shapeUtil.expend_peak_region_up(range_df, high2_data, high2_index_loc)
            region_up_2 = range_df[min1_index_loc + offset_down1:high2_index_loc + offset_up2]
            region_up_2_merged = shapeUtil.get_merged_region_up(region_up_2)
            if len(region_up_2_merged) == 0:  # 当前区域k线被上一个区域全合并了
                continue

            # 判断极值向右是否存在可合并的k线，如果含有则扩大当前的趋势范围
            offset_down2 = shapeUtil.expend_peak_region_down(range_df, min2_data, min2_index_loc)
            region_down_2 = range_df[high2_index_loc + offset_up2:min2_index_loc + offset_down2]
            region_down_2_merged = shapeUtil.get_merged_region_down(region_down_2)
            if len(region_down_2_merged) == 0:  # 当前区域k线被上一个区域全合并了
                continue

            region_up_3 = range_df[min2_index_loc + offset_down2:]
            region_up_3_merged = shapeUtil.get_merged_region_up(region_up_3)
            if len(region_up_3_merged) == 0:  # 当前区域k线被上一个区域全合并了
                continue

            # 如果极小值在右边界，则为无效数据，跳过下面分型的校验。
            if high2_index.strftime('%Y-%m-%d') == region_up_3_merged.index[-1].strftime('%Y-%m-%d'):
                continue
            buy_day = region_up_3.iloc[0]
            if buy_day['open'] > buy_day['close']:
                continue

            region_merged = region_up_1_merged.append(region_down_1_merged).append(region_up_2_merged).append(
                region_down_2_merged).append(region_up_3_merged)
            mplfinance.plot(region_merged, type='candle')

            # 识别一顶分型
            if dataUtil.is_top_shape(region_merged, high1_index):
                pass
            else:
                continue

            # 识别一底分型
            if dataUtil.is_bottom_shape(region_merged, min1_index):
                pass
            else:
                continue

            # 识别二顶分型
            if dataUtil.is_top_shape(region_merged, high2_index):
                pass
            else:
                continue

            # 识别二底分型
            if dataUtil.is_bottom_shape(region_merged, min2_index):
                pass
            else:
                continue

            # 一顶和一底之间至少有 3 条k线。如果包括两个极点，就是5条k线
            if region_merged.index.get_loc(min1_index) - region_merged.index.get_loc(high1_index) > 3:
                pass
            else:
                continue

            # 一底和二顶之间至少有 3 条k线。如果包括两个极点，就是5条k线
            if region_merged.index.get_loc(high2_index) - region_merged.index.get_loc(min1_index) > 3:
                pass
            else:
                continue

            # 二顶和二底之间至少有 3 条k线。如果包括两个极点，就是5条k线
            if region_merged.index.get_loc(min2_index) - region_merged.index.get_loc(high2_index) > 3:
                pass
            else:
                continue

            # 如果通过前面的校验，则加到结果集
            info = str(high1_index).replace(' 00:00:00', ' ') + str(min1_index).replace(
                ' 00:00:00', ' ') + str(
                high2_index).replace(' 00:00:00', ' ') + str(min2_index).replace(
                ' 00:00:00', ' ')
            # mplfinance.plot(region_merged, type='candle')
            # result.add(info)
            return info
    return '未找到符合条件的时间范围'
    # return result


if __name__ == '__main__':
    logger.info("最终结果: " + handle_data())
