# -*- coding: utf-8 -*-
import scrapy
import logging
import random
from urllib.parse import urljoin
from urllib.parse import urlparse
import time
import html2text
from .. import items
from scrapy.loader import ItemLoader
import re

MIN_ARTICLE_LEN = 1000
class HuxiuSpider(scrapy.Spider):
    name = 'test'
    allowed_domains = ['huxiu.com']
    start_urls = ['https://www.huxiu.com/article/339750.html']


    def pureHtml(self,article_content):
        converter = html2text.HTML2Text()
        converter.ignore_links = True
        return re.sub(r'\(.*\)', "",
               re.sub(r'（.*）', "", converter.handle(article_content).replace("\n", '').strip().replace("*", "")))

    def parse(self, response):
        if(response.status==200):
            self.logger.info('scrapy fetch page: %s', response.url)

            article_content = response.xpath('//*[@id="article_read"]//*[@id="article-content"]').get()
            if(len(article_content) < MIN_ARTICLE_LEN):
                return

            article_content_txt = self.pureHtml(article_content)
            # article_content_txt = self.article_filter(article_content_txt)

            print(">>>>>>>>>>>>>>>>>>>>>>")

            il = ItemLoader(item=items.Article(), response=response)

            il.add_xpath("title",'//*[@id="article_read"]//*[@class="article__title"]/text()')
            il.add_xpath("time", '//*[@id="article_read"]//*[@class="article__time"]/text()')
            il.add_value("content", article_content_txt)
            il.add_value("url", response.url)
            il.add_value("original", items.Original.huxiu.value)
            il.add_value("type", items.Type.tech.value)
            # response.xpath('//*[@id="article_read"]//*[@class="article__title"]/text()').get()
            # article_time = response.xpath('//*[@id="article_read"]//*[@class="article__time"]/text()').get()
            # article_content = response.xpath('//*[@id="article_read"]//*[@id="article-content"]').get()
            # converter = html2text.HTML2Text()
            # converter.ignore_links = True
            # article_content_txt = converter.handle(article_content)
            # article_url = response.url
            # article_original = items.Original.huxiu
            # article_type = items.Type.tech

            # print(il.load_item())
            yield scrapy.Request('https://www.huxiu.com/article/339750.html',callback=self.p)
        else:
            self.logger.error('FAILED! scrapy fetch page: %s', response.url)


    def p(self,response):
        print("9999999")

    # '但值得深思的是
    def article_filter(self,article_content):
        last_index = article_content.rfind("参考资料")
        if last_index != -1:
            print(last_index)
            print("~~~~~~~~~~~~")
            return article_content[:last_index]
        else:
            return article_content