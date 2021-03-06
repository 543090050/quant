import logging

FILE_PATH = 'D:/stockFile/'  # csv文件存储位置
FIELDS_DAY = "date,code,open,high,low,close,volume,amount,turn,pctChg,peTTM,pbMRQ,psTTM,pcfNcfTTM"
STRATEGY_START_TIME = '9:00'  # 策略开始时间
STRATEGY_END_TIME = '23:00'  # 策略结束时间

CONSOLE_LEVEL = logging.INFO  # 控制台日志级别
# CONSOLE_LEVEL = logging.DEBUG  # 控制台日志级别

SINA_QUERY_INTERVAL = 5  # 新浪API查询间隔
