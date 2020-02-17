# -*- coding: utf-8 -*-
import scrapy
import logging
import random
from urllib.parse import urljoin
from urllib.parse import urlparse
import time
class HuxiuSpider(scrapy.Spider):
    name = 'ifeng'
    allowed_domains = ['news.ifeng.com']
    start_urls = ['https://news.ifeng.com']

    def parse(self, response):
        if(response.status==200):
            self.logger.info('scrapy fetch page: %s', response.url)
            hrefs = response.xpath('//a/@href')
            print("--")
            for href in hrefs:
                url = href.get()
                urlp = urlparse(url)

                #如果netloc是空则是相对路径
                #ParseResult(scheme='http', netloc='www.aw.com', path='/df/23332.jpg', params='', query='', fragment='')
                if "news.ifeng.com" in url:
                    yield scrapy.Request("http://news.ifeng.com/c/7txN1W6aN6m", callback=self.repeat)
                    # yield scrapy.Request(abs_url,callback=self.parse_article)
        else:
            self.logger.error('FAILED! scrapy fetch page: %s', response.url)

    def repeat(self,response):
        time.sleep(5)
        print("................1")
