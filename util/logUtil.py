import logging
import logging.config
import os
import sys
from logging import handlers
import common.vars as vs

# 控制台日志级别
CONSOLE_LEVEL = vs.CONSOLE_LEVEL


def get_logger(name='root'):

    formatter = logging.Formatter('%(asctime)s - %(module)s.%(funcName)s[line:%(lineno)d] - %(levelname)s: %(message)s')

    # 创建一个日志器logger并设置其日志级别为DEBUG
    logger = logging.getLogger('simple_logger')
    logger.setLevel(logging.DEBUG)

    # 创建一个控制台处理器handler并设置其日志级别为DEBUG
    streamHandler = logging.StreamHandler(sys.stdout)
    streamHandler.setLevel(CONSOLE_LEVEL)
    streamHandler.setFormatter(formatter)

    # 创建文件处理器
    fileHandler = handlers.TimedRotatingFileHandler(os.path.abspath(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + "/log/default.log"),
        "midnight", 1, 6, 'utf-8')
    fileHandler.setLevel(logging.INFO)
    fileHandler.setFormatter(formatter)

    # 为日志器logger添加上面创建的处理器handler
    logger.addHandler(streamHandler)
    # logger.addHandler(fileHandler)
    return logger


logger = get_logger(__name__)
