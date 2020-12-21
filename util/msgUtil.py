# coding=utf-8

import win32gui
import win32con
import win32clipboard

# import pywin32

# 引入 win32gui 时，需要先引用 pywin32

# 根据任务栏的好友名称，提取聊天窗口，实现发送qq消息
from util import timeUtil


class CSendQQMsg:
    def __init__(self, msg, friendName='quant'):
        self.msg = msg
        self.friendName = friendName

    def setText(self):  # 把要发送的消息复制到剪贴板
        win32clipboard.OpenClipboard()
        win32clipboard.EmptyClipboard()
        win32clipboard.SetClipboardData(win32con.CF_UNICODETEXT, self.msg)
        win32clipboard.CloseClipboard()

    def sendMsg(self):  # 给好友发送消息
        self.setText()
        hwndQQ = win32gui.FindWindow(None, self.friendName)  # 找到名字为'friendName'的窗口
        if hwndQQ == 0:
            print('未找到qq对话框')
            return
        win32gui.SendMessage(hwndQQ, win32con.WM_PASTE, 0, 0)
        win32gui.SendMessage(hwndQQ, win32con.WM_KEYDOWN, win32con.VK_RETURN, 0)


if __name__ == '__main__':
    friendName = 'quant'
    msg = timeUtil.getToday()
    QQClient = CSendQQMsg(friendName, msg)
    for i in range(10):
        QQClient.sendMsg()
