# logUtil.py
import logging
import logging.config
import os
import sys


# https://blog.csdn.net/weixin_42526352/article/details/90242840
def get_logger(name='root'):
    conf_log = os.path.abspath(os.getcwd() + "/resource/logger_config.ini")
    logging.config.fileConfig(conf_log)
    return logging.getLogger(name)


logger = get_logger(__name__)


def test():
    logger.info("start")
    try:
        print(1 / 0)
    except Exception:
        logger.error("error:")
        logger.exception(sys.exc_info())  # 打印堆栈信息
    logger.debug("end")
