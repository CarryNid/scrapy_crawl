# encoding: utf-8

# 存储news与html的数据库配置列表
WEBSITE_CONFIG_LIST = {

    '00': {# 此为公用测试数据库（校园网内可使用），可以换成自己的.
        'host': 'localhost',
        'port': 3306,
        'user': 'root',
        'password': '1234',
        'db': 'dg_db_website'
    },
    '01': {  # 本地测试数据库
        'host': 'localhost',
        'port': 3306,
        'user': 'root',
        'password': '1234',
        'db': 'dg_db_website'
    }
}