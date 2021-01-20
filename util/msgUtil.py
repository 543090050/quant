# coding=utf-8
import time
import win32gui
import win32con
import win32clipboard

# import pywin32

# 引入 win32gui 时，需要先引用 pywin32

# 根据任务栏的好友名称，提取聊天窗口，实现发送qq消息
from util import timeUtil, dataUtil
from util.logUtil import logger

def setText(msg):  # 把要发送的消息复制到剪贴板
    win32clipboard.OpenClipboard()
    win32clipboard.EmptyClipboard()
    win32clipboard.SetClipboardData(win32con.CF_UNICODETEXT, msg)
    win32clipboard.CloseClipboard()


def sendMsg(msg, friendName='quantMsg'):  # 给好友发送消息
    if len(msg.strip()) == 0:
        return
    logger.info("发送qq消息: " + msg)
    setText(msg)
    hwndQQ = win32gui.FindWindow(None, friendName)  # 找到名字为'friendName'的窗口
    if hwndQQ == 0:
        # logger.error('未找到qq对话框')
        raise Exception('未找到qq对话框 ' + friendName)
        # return
    win32gui.SendMessage(hwndQQ, win32con.WM_PASTE, 0, 0)
    win32gui.SendMessage(hwndQQ, win32con.WM_KEYDOWN, win32con.VK_RETURN, 0)


def send_msg_by_signal():
    """
    根据信号发送消息
    发送成功时会将gold_msg ， dead_msg置为已发送状态，防止一天发送多次同样的消息
    :return:
    """

    stocks_info = dataUtil.get_stocks_info()

    # 发送的QQ消息
    gold_codes = ""
    dead_codes = ""
    for code in zip(stocks_info.index):  # 获取df索引
        code = code[0]
        # 判断信号，并发送消息
        gold_flag = stocks_info.loc[code, 'gold_flag']
        if gold_flag != 'sended':
            if stocks_info.loc[code, 'ma30_flag'] == 'True':
                gold_codes = gold_codes + code + ";"
                stocks_info.loc[code, 'gold_flag'] = 'sended'
            elif stocks_info.loc[code, 'w_shape_flag'] == 'True':
                gold_codes = gold_codes + code + ";"
                stocks_info.loc[code, 'gold_flag'] = 'sended'

        dead_flag = stocks_info.loc[code, 'dead_flag']
        if dead_flag != 'sended' and stocks_info.loc[code, 'ma8_flag'] == 'True':
            dead_codes = dead_codes + code + ";"
            stocks_info.loc[code, 'dead_flag'] = 'sended'

    try:
        final_msg = ''
        if len(gold_codes) > 0:
            final_msg = "符合买入信号: " + gold_codes + '\n'
        if len(dead_codes) > 0:
            final_msg = final_msg + "符合卖出信号: " + dead_codes
        sendMsg(final_msg)
        # 保存h5文件，记录消息标志位，目的是一天只发送一次符合条件的消息
        dataUtil.put_h5_data("stocks_info", stocks_info)
    except Exception as e:
        # logger.exception(sys.exc_info())
        logger.error(e)


if __name__ == '__main__':
    for i in range(5):
        msg = timeUtil.getCurrentTime()
        time.sleep(1)
        sendMsg(msg)
