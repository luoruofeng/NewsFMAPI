# -*- coding: utf-8 -*-
import scrapy
import random
from urllib.parse import urljoin
from urllib.parse import urlparse
import time
from .. import items
from scrapy.log import logger
from scrapy.loader import ItemLoader
import re

class HuxiuSpider(scrapy.Spider):
    name = 'huxiu'
    allowed_domains = ['huxiu.com']
    start_urls = ['https://www.huxiu.com/article/']



    def parse(self, response):
        if(response.status==200):
            logger.info('scrapy fetch page: %s', response.url)
            hrefs = response.xpath('//*[contains(@class,"article-item")]//a/@href')
            for href in hrefs:
                url = href.get()
                urlp = urlparse(url)

                #如果netloc是空则是相对路径
                #ParseResult(scheme='http', netloc='www.aw.com', path='/df/23332.jpg', params='', query='', fragment='')
                if url != "" and url is not None and (urlp.netloc == "" or urlp.netloc is None):
                    abs_url = urljoin(response.url, url)
                    if abs_url is not None:
                        yield scrapy.Request(abs_url,callback=self.parse_article)
        else:
            logger.error('FAILED! scrapy fetch page: %s', response.url)

    def parse_article(self, response):
        if(response.status==200):
            logger.info('scrapy fetch page: %s', response.url)

            il = ItemLoader(item=items.Article(), response=response)

            il.add_xpath("title",'//*[@id="article_read"]//*[@class="article__title"]/text()')
            il.add_xpath("time", '//*[@id="article_read"]//*[@class="article__time"]/text()')
            il.add_xpath("content", '//*[@id="article_read"]//*[@id="article-content"]')
            il.add_value("url", response.url)
            il.add_value("original", items.Original.huxiu.value)
            il.add_value("type", items.Type.tech.value)

            yield il.load_item()

        else:
            logger.error('FAILED! scrapy fetch page: %s', response.url)

