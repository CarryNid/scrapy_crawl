'''
Description: file description
Version: 1.0
Autor: Renhetian
Date: 2021-10-11 11:39:50
LastEditors: Renhetian
LastEditTime: 2022-02-12 14:21:22
'''
# encoding: utf-8

import os

from apscheduler.schedulers.blocking import BlockingScheduler
from scripts import report, log_clean
from config.scheduler_config import *

def git_pull():
    os.system("git pull")
    print("pull仓库成功")


# 主调度函数
# python -m scheduler
if __name__ == '__main__':
    report.run()
    log_clean.run()
    git_pull()
    sched = BlockingScheduler()
    if is_report:
        sched.add_job(report.run, 'cron', hour=0, minute=10)
    if is_log_clean:
        sched.add_job(log_clean.run, 'cron', args=[3], hour=0, minute=10)
    if is_git_pull:
        sched.add_job(git_pull, 'cron', hour='*/1')
    sched.start()
