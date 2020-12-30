# coding=utf-8
import time
import win32gui
import win32con
import win32clipboard

# import pywin32

# 引入 win32gui 时，需要先引用 pywin32

# 根据任务栏的好友名称，提取聊天窗口，实现发送qq消息
from util import timeUtil
import logging

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s')


def setText(msg):  # 把要发送的消息复制到剪贴板
    win32clipboard.OpenClipboard()
    win32clipboard.EmptyClipboard()
    win32clipboard.SetClipboardData(win32con.CF_UNICODETEXT, msg)
    win32clipboard.CloseClipboard()


def sendMsg(msg, friendName='quantMsg'):  # 给好友发送消息
    # logging.info("发送qq消息: " + msg)
    setText(msg)
    hwndQQ = win32gui.FindWindow(None, friendName)  # 找到名字为'friendName'的窗口
    if hwndQQ == 0:
        # logging.error('未找到qq对话框')
        raise Exception('未找到qq对话框 ' + friendName)
        # return
    win32gui.SendMessage(hwndQQ, win32con.WM_PASTE, 0, 0)
    win32gui.SendMessage(hwndQQ, win32con.WM_KEYDOWN, win32con.VK_RETURN, 0)


if __name__ == '__main__':
    friendName = 'quant'
    msg = timeUtil.getCurrentTime()
    for i in range(5):
        time.sleep(1)
        sendMsg(friendName, msg)
