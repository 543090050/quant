from util import h5Util
from util.logUtil import logger
from util.weChatUtil import weChatClient


def send_msg_by_signal():
    """
    根据信号发送消息
    发送成功时会将gold_msg ， dead_msg置为已发送状态，防止一天发送多次同样的消息
    :return:
    """

    stocks_info = h5Util.get_stocks_info()

    # 发送的消息
    gold_codes = ""
    dead_codes = ""
    for code in zip(stocks_info.index):  # 获取df索引
        code = code[0]
        # 判断信号
        gold_flag = stocks_info.loc[code, 'gold_flag']
        ma30_flag = stocks_info.loc[code, 'ma30_flag']
        w_shape_flag = stocks_info.loc[code, 'w_shape_flag']
        if gold_flag != 'sended':
            if w_shape_flag == 'True':
                gold_codes = gold_codes + code + ";"
                stocks_info.loc[code, 'gold_flag'] = 'sended'

        dead_flag = stocks_info.loc[code, 'dead_flag']
        if dead_flag != 'sended' and stocks_info.loc[code, 'ma8_flag'] == 'True':
            dead_codes = dead_codes + code + ";"
            stocks_info.loc[code, 'dead_flag'] = 'sended'
    # 发送消息
    try:
        final_msg = ''
        if len(gold_codes) > 0:
            final_msg = "符合买入信号: " + gold_codes + '\n'
        if len(dead_codes) > 0:
            final_msg = final_msg + "符合卖出信号: " + dead_codes
        weChatClient.send_data(final_msg)
        # sendMsg(final_msg)
        # 保存h5文件，记录消息标志位，目的是一天只发送一次符合条件的消息
        h5Util.put_h5_data("stocks_info", stocks_info)
    except Exception as e:
        # logger.exception(sys.exc_info())
        logger.error(e)
