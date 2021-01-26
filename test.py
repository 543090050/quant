import threading
import time

import pandas as pd

from main_current import get_context
from util import baoStockUtil, shapeUtil, h5Util
from util.timeUtil import time_to_date
import common.vars as vs

FILE_PATH = vs.FILE_PATH


# import mplfinance

def func1():
    print("t1开始读取:")
    result = h5Util.get_h5_data('stocks_info')
    print(result)


def func2(df):
    print("t2开始写入:")
    filename = FILE_PATH + "stock_data.h5"
    try:
        hStore = pd.HDFStore(filename, 'w')
        hStore.put('stocks_info', df, format='table', append=False)
        time.sleep(2)
        hStore.close()
    except Exception as e:
        print(e)


if __name__ == '__main__':
    df = pd.DataFrame({'name': ['wencky', 'stany', 'barbio'],
                       'age': [29, 29, 3],
                       'gender': ['w', 'm', 'm']})
    t1 = threading.Thread(target=func1)
    t2 = threading.Thread(target=func2, args=(df,))
    t2.start()
    t1.start()
