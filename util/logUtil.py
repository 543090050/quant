import logging
import logging.config
import os
import sys

# https://blog.csdn.net/weixin_42526352/article/details/90242840
from logging import handlers


def get_logger(name='root'):
    # conf_log = os.path.abspath(os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + "/resource/logger_config.ini")
    # logging.config.fileConfig(conf_log)
    # return logging.getLogger(name)

    formatter = logging.Formatter('%(asctime)s - %(module)s.%(funcName)s[line:%(lineno)d] - %(levelname)s: %(message)s')

    # 创建一个日志器logger并设置其日志级别为DEBUG
    logger = logging.getLogger('simple_logger')
    logger.setLevel(logging.DEBUG)

    # 创建一个流处理器handler并设置其日志级别为DEBUG
    streamHandler = logging.StreamHandler(sys.stdout)
    streamHandler.setLevel(logging.DEBUG)
    streamHandler.setFormatter(formatter)

    # 创建文件处理器
    fileHandler = handlers.TimedRotatingFileHandler(os.path.abspath(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + "/log/defalut.log"),
                                                    "midnight", 1, 6, 'utf-8')
    fileHandler.setLevel(logging.DEBUG)
    fileHandler.setFormatter(formatter)

    # 为日志器logger添加上面创建的处理器handler
    logger.addHandler(streamHandler)
    logger.addHandler(fileHandler)
    return logger


logger = get_logger(__name__)


def test():
    logger.info("start")
    try:
        print(1 / 0)
    except Exception:
        logger.error("error:")
        logger.exception(sys.exc_info())  # 打印堆栈信息
    logger.debug("end")
