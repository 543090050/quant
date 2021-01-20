import mplfinance

from util import dataUtil, shapeUtil, timeUtil
from util.logUtil import logger


def strategy_w_shape(code, stocks_info, history_data):
    logger.info("解析" + code)
    stocks_info.loc[code, 'code'] = code
    stocks_info.loc[code, 'w_shape_flag'] = 'NaN'
    stocks_info.loc[code, '最新时间'] = timeUtil.getCurrentTime()
    # data_range 确定游标范围长度，默认从15开始，因为有三个趋势类型，每个趋势类型至少有5条k线
    for data_range in range(15, len(history_data) + 1):
        range_df = history_data[-data_range:]  # 从后往前逐步扩大范围
        # logger.info('游标天数=====:' + str(data_range) + " 时间范围: " + range_df.index[0].strftime('%Y-%m-%d') + " - " +
        #             range_df.index[-1].strftime('%Y-%m-%d'))

        for split in range(4, data_range - 4):  # 分割索引从4开始，保证区域内至少有3个值
            region1 = range_df[0:split]
            region2 = range_df[split:]

            high1_index = region1['high'].idxmax()
            high1_data = region1.loc[high1_index]
            min1_index = region1['low'].idxmin()
            min1_data = region1.loc[min1_index]
            min2_index = region2['low'].idxmin()
            min2_data = region2.loc[min2_index]

            # 最后一天为买点，要是阳线
            buy_day = range_df.iloc[-1]
            if buy_day['open'] >= buy_day['close']:
                # continue
                return '未找到符合条件的时间范围'

            # 倒数第三天应是min2应该在的位置；倒数第二天构成底分型；倒数第一天为买点
            min2_temp = range_df.iloc[-3]
            if min2_temp.name != min2_index:
                continue
                # return '未找到符合条件的时间范围'

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

            # TODO debug找日期
            # if high1_index.strftime('%Y-%m-%d') == '2020-10-13' and min1_index.strftime('%Y-%m-%d') == '2020-11-02' \
            #         and high2_index.strftime('%Y-%m-%d') == '2020-11-10':
            #     pass
            # else:
            #     continue

            # 开始校验====================================================================================================
            # 如果极值在起始边界，则为无效数据，跳过下面分型的校验。
            if high1_index.strftime('%Y-%m-%d') == range_df.index[0].strftime('%Y-%m-%d') \
                    or min2_index.strftime('%Y-%m-%d') == range_df.index[-1].strftime('%Y-%m-%d'):
                continue

            # 四个极点的顺序
            if high1_index < min1_index < high2_index < min2_index:
                pass
            else:
                continue

            # 确认是w形态
            if min1 <= min2 and high1 > high2:  # w 形态的四个主要点，高一低一；高二低二
                pass
            else:
                continue

            # high1要是整个范围内的最大值
            if high1_data['high'] < range_df['high'].max():
                continue

            # min1要是整个范围内的最小值
            if min1_data['low'] > range_df['low'].min():
                continue

            # min2要是high2到结束间的最小值
            region_high2_end = range_df.iloc[range_df.index.get_loc(high2_index) + 1:]
            if min2_data['low'] > region_high2_end['low'].min():
                continue

            # 一顶和一底之间至少有 3 条k线。如果包括两个极点，就是5条k线
            if range_df.index.get_loc(min1_index) - range_df.index.get_loc(high1_index) > 3:
                pass
            else:
                continue

            # 一底和二顶之间至少有 3 条k线。如果包括两个极点，就是5条k线
            if range_df.index.get_loc(high2_index) - range_df.index.get_loc(min1_index) > 3:
                pass
            else:
                continue

            # 二顶和二底之间至少有 3 条k线。如果包括两个极点，就是5条k线
            if range_df.index.get_loc(min2_index) - range_df.index.get_loc(high2_index) > 3:
                pass
            else:
                continue

            # 识别一顶分型
            if dataUtil.is_top_shape(range_df, high1_index):
                pass
            else:
                continue

            # 识别一底分型
            if dataUtil.is_bottom_shape(range_df, min1_index):
                pass
            else:
                continue

            # 识别二顶分型
            if dataUtil.is_top_shape(range_df, high2_index):
                pass
            else:
                continue

            # 识别二底分型
            if dataUtil.is_bottom_shape(range_df, min2_index):
                pass
            else:
                continue

            # 如果通过前面的校验，则加到结果集
            info = code + ' 符合底分型 ' + str(high1_index).replace(' 00:00:00', ' ') + str(min1_index).replace(
                ' 00:00:00', ' ') + str(
                high2_index).replace(' 00:00:00', ' ') + str(min2_index).replace(
                ' 00:00:00', ' ')
            # mplfinance.plot(range_df, type='candle')
            # result.add(info)
            logger.info(info)
            stocks_info.loc[code, 'w_shape_flag'] = 'True'
            dataUtil.put_h5_data("stocks_info", stocks_info)
            return info
    return '未找到符合条件的时间范围'
