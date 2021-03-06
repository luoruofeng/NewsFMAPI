# -*- coding: utf-8 -*-
import scrapy
import random
from urllib.parse import urljoin
from urllib.parse import urlparse
import time
from .. import items
from scrapy.loader import ItemLoader
import logging
import re
import json

class HuxiuSpider(scrapy.Spider):
    name = 'first_huxiu'
    allowed_domains = ['huxiu.com']



    def start_requests(self):
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36 QIHU 360SE'
        }
        data = {
            'platform': 'www',
            'pagesize': '200'
        }
        yield scrapy.FormRequest('https://article-api.huxiu.com/web/article/articleList', dont_filter=True,method='POST', headers=headers, formdata=data, callback = self.parse_list)

    def parse_list(self, response):
        if(response.status==200):
            logging.log(logging.INFO,'first_scrapy fetch page: %s', response.url)
            res_data = json.loads(response.body.decode('utf-8'))
            if res_data['success']:
                data = res_data["data"]
                if(data != None):
                    for item in data["dataList"]:
                        if(item["is_vip_column_article"] == True):
                            logging.log(logging.ERROR,'article is not free: %s', item["share_url"])
                            continue
                        else:
                            abs_url = "https://www.huxiu.com/article/"+item["aid"]+".html"
                            if abs_url is not None:
                                yield scrapy.Request(abs_url, callback=self.parse_article)
        else:
            logging.log(logging.ERROR,'first scrapy fetch page: %s', response.url)

    def parse_article(self, response):
        if(response.status==200):
            logging.log(logging.INFO,'scrapy fetch page: %s', response.url)

            il = ItemLoader(item=items.Article(), response=response)

            il.add_xpath("title",'//*[@id="article_read"]//*[@class="article__title"]/text()')
            il.add_xpath("time", '//*[@id="article_read"]//*[@class="article__time"]/text()')
            il.add_xpath("content", '//*[@id="article_read"]//*[@id="article-content"]')
            il.add_value("url", response.url)
            il.add_value("original", items.Original.huxiu.value)
            il.add_value("type", items.Type.tech.value)

            yield il.load_item()

        else:
            logging.log(logging.ERROR,'FAILED! scrapy fetch page: %s', response.url)

