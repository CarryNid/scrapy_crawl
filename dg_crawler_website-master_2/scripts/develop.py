'''
Description: file description
Version: 1.0
Autor: Renhetian
Date: 2022-02-28 14:44:59
LastEditors: Renhetian
LastEditTime: 2022-02-28 22:41:30
'''

import sys
import inspect
import pkgutil
from fire import Fire

from crawler.spiders import BaseSpider
from utils.date_util import DateUtil
from libs.mysql import Mysql
from config.db_config import COMMON_WEBSITE_CONFIG
from common.db_keys import WEBSITE_DEVELOPMENT_KEYS

paths = ['crawler/passed']

sql1 = 'SELECT website_id FROM development'
sql2 = 'UPDATE website SET `status`= 1, start_time="{}" WHERE id={}'

def run():
    sql = Mysql(COMMON_WEBSITE_CONFIG)
    website_id_list = [i[0] for i in sql.select(sql1)]
    for _, modname, _ in pkgutil.walk_packages(path=paths, prefix='crawler.passed.'):
        exec('from ' + modname + ' import *')
        for _, class_ in inspect.getmembers(sys.modules[modname], inspect.isclass):
            if issubclass(class_, BaseSpider) and class_ != BaseSpider:
                if class_.website_id in website_id_list:
                    continue
                sql.insert('development', WEBSITE_DEVELOPMENT_KEYS, 
                [class_.website_id, class_.name, '00', 2, 1, '', 0, 
                DateUtil.time_now_formate(), DateUtil.time_now_formate()])
                sql.execute(sql2.format(DateUtil.time_now_formate(), class_.website_id))
                print('爬虫已录入 ==> id:{}'.format(class_.website_id))

# python -m scripts.develop
if __name__ == "__main__":
    Fire(run)