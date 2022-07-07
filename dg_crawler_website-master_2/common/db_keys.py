'''
Description: file description
Version: 1.0
Autor: Renhetian
Date: 2021-10-11 11:39:50
LastEditors: Renhetian
LastEditTime: 2022-02-28 22:13:37
'''
# encoding: utf-8

# dg_crawler_website数据库news表字段
WEBSITE_NEWS_KEYS = ( 
    'website_id',
    'request_url',
    'response_url',
    'category1',
    'category2',
    'title',
    'abstract',
    'body',
    'pub_time',
    'cole_time',
    'images',
    'language_id',
    'md5'
)

# dg_crawler_website数据库html表字段
WEBSITE_HTML_KEYS = (
    'md5',
    'html',
    'create_time'
)

# common_website数据库development表字段
WEBSITE_DEVELOPMENT_KEYS = ( 
    'website_id',
    'name',
    'proxy',
    'level',
    'is_open',
    'remark',
    'is_http',
    'start_time',
    'run_time'
)