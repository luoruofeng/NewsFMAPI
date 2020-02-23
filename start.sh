#/bin/bash

#启动百度转化项目
echo -e "\n执行baidu api进程\n"
`chmod 774 ./voice/main.py`
`nohup python ./voice/main.py  </dev/null 1>>./baidu.out 2>>./baidu.out &`

#启动爬虫项目
cd $(pwd)/news_scrapy/newspider
echo -e "进入$(pwd)\n"
echo -e "运行scrapy项目\n"
`chmod 774 ./main.py`
`nohup python ./main.py </dev/null 1>>$(pwd)/../../scrapy.out 2>>$(pwd)/../../scrapy.out &`
cd $(pwd)/../../
echo -e "回到目录$(pwd)\n"
