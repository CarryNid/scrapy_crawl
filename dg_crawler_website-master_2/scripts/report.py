# encoding=utf-8

import time
from libs.mysql import Mysql
from config.db_config import *
from libs.excel import Excel
from libs.mail import Mail

"""
数据部 每日数据获取报表脚本。
生成报表.xls文件
发送到数据部成员邮箱、数据挖掘实验室邮箱、老师邮箱。
"""

smtp = 'smtp.163.com'  # smtp域名
# sender = 'khan.liu@qq.com'  # 发送方邮箱(刘鼎谦)
# passwd = 'wxuhjbiaippcbbac'  # 授权码(ldq)
sender = 'gdufs_shuwa@163.com'
passwd = 'UZWEIBYLWAOVDQYK'  # 授权码(gdufs_shuwa)
receivers = [  # 收件人邮箱
    'gdufs_shuwa@163.com',
    '657742829@qq.com',
    'jiangshengyi@163.com',
    '1090030606@qq.com',  # 林晓钿
    '331423904@qq.com',
    'chenxuanqi6@163.com',
    '2630862330@qq.com',  # WPF
    '1226144058@qq.com',  # LingMin
    '2754976781@qq.com',
    '467691306@qq.com',  # 彭雨胜
    '2905939881@qq.com',  # 曾嘉祥
    '734200940@qq.com',  # 刘鼎谦
]

# sql语句,日常数据获取报告和日常获取量。
daily_sql = "SELECT website_id,count(*) FROM news WHERE cole_time >= '{}' GROUP BY website_id ORDER BY NULL"
daily_common_sql = "SELECT website.id,url,website.c_name,country.`name`,`language`.c_name,remark,developer,CAST(website.start_time AS CHAR) FROM website LEFT JOIN country ON website.country_id = country.id LEFT JOIN `language` ON website.lan_id = `language`.id WHERE website.id = {}"
all_sql = "SELECT website_id,count(*) FROM news GROUP BY website_id ORDER BY NULL"
all_common_sql = "SELECT website.id,url,website.c_name,country.`name`,`language`.c_name,remark,developer,CAST(website.start_time AS CHAR) FROM website LEFT JOIN country ON website.country_id = country.id LEFT JOIN `language` ON website.lan_id = `language`.id WHERE website.id = {}"
# 时间
time_yesterday = time.strftime("%Y-%m-%d", time.localtime(time.time() - 86400))
# 文件路径
file = '{}.xls'
# 累计数据获取报告和累计获取量。
daily_fields_list = ['website_id', 'url', 'c_name', 'country', 'language', 'remark', 'developer', 'start_time',
                     'news_amount']
all_fields_list = ['website_id', 'url', 'c_name', 'country', 'language', 'remark', 'developer', 'start_time',
                   'news_amount']


def daily():
    '''
    每日统计数据生成逻辑
    '''
    news_db = Mysql(WEBSITE_CONFIG_LIST['01'])
    common_db = Mysql(COMMON_WEBSITE_CONFIG)
    data = [daily_fields_list]
    sum = 0
    data1 = news_db.select(daily_sql.format(time_yesterday))
    for i in data1:
        data2 = list(common_db.select(daily_common_sql.format(i[0]))[0])
        sum += i[1]
        data2.append(i[1])
        data.append(data2)
    data.append([])
    data.append(['总计'])
    data.append([sum])
    return data


def all():
    '''
    累计数据生成逻辑
    '''
    news_db = Mysql(WEBSITE_CONFIG_LIST['01'])
    common_db = Mysql(COMMON_WEBSITE_CONFIG)
    data = [all_fields_list]
    sum = 0
    data1 = news_db.select(all_sql.format(time_yesterday))
    for i in data1:
        data2 = list(common_db.select(all_common_sql.format(i[0]))[0])
        sum += i[1]
        data2.append(i[1])
        data.append(data2)
    data.append([])
    data.append(['总计'])
    data.append([sum])
    return data


def annual():
    '''
    年度统计表格生成逻辑
    '''
    pass


def run():
    global time_yesterday
    time_yesterday = time.strftime("%Y-%m-%d", time.localtime(time.time() - 86400))
    file_ = file.format(time_yesterday)
    book = Excel(file_)
    book.add_sheet('每日', daily())
    book.add_sheet('累计', all())
    # book.add_sheet('累计', annual())
    book.save()

    subject = '数据获取每日报表 {}'.format(time_yesterday)
    message = Mail(sender=sender, receivers=receivers, passwd=passwd, smtp=smtp, subject=subject)
    message.attach_file(file_)
    message.send()


# python -m scripts.report
if __name__ == '__main__':
    run()
