#/bin/bash

#启动百度转化项目
`chmod 774 ./voice/main.py`
`nohup python ./voice/main.py  </dev/null 1>>./baidu.out 2>>./baidu.out &`

#启动爬虫项目
`chmod 774 ./news_scrapy/newspider/main.py`
`nohup python ./news_scrapy/newspider/main.py </dev/null 1>>./scrapy.out 2>>./scrapy.out &`