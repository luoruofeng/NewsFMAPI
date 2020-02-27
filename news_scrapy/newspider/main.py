import sys
import os
from scrapy.cmdline import execute
import time
import subprocess

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

if __name__ == "__main__":
    #初始化拉取以前的文章
    # p_restart = subprocess.Popen(['scrapy', 'crawl', 'first_huxiu'])

    print("------------start first huxiu---------------")
    app_path = os.path.dirname(os.path.realpath(__file__))
    subprocess.Popen("scrapy crawl first_huxiu", shell=True, cwd=app_path)


    while(True):
        print("------------start huxiu---------------")
        #每两小时拉取一次  www.huxiu/article
        time.sleep(60*60*2)
        # p_restart = subprocess.Popen(['scrapy', 'crawl', 'huxiu'])
        subprocess.Popen("scrapy crawl huxiu", shell=True, cwd=app_path)