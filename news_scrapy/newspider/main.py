import sys
import os
from scrapy.cmdline import execute
from apscheduler.schedulers.blocking import BlockingScheduler
import time
import subprocess

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

if __name__ == "__main__":
    #初始化拉取以前的文章
    p_restart = subprocess.Popen(['scrapy', 'crawl', 'first_huxiu'])

    while(True):
        #每两小时拉取一次  www.huxiu/article
        time.sleep(60*60*2)
        p_restart = subprocess.Popen(['scrapy', 'crawl', 'huxiu'])
