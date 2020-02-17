# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

import html2text
import pymongo
import re

from scrapy.exceptions import DropItem

class NewspiderPipeline(object):
    def process_item(self, item, spider):
        return item



MIN_ARTICLE_LEN = 100

# 判读 article content是否为空 或太短
class ArticleContentLenPipeline(object):
    def process_item(self, item, spider):
        article_content = item.get("content")
        if(article_content):
            if (len(article_content) < MIN_ARTICLE_LEN):
                raise DropItem("article content is too short. url is :\n"+item.get("url"))
            else:
                return item
        else:
            raise DropItem("article content is Null. content is :\n" + item)

#去掉html标签，*，空格
class ArticleContentHtmlPipeline(object):

    def pureHtml(self,article_content):
        converter = html2text.HTML2Text()
        converter.ignore_links = True
        converter.ignore_images = True

        content = converter.handle(article_content)
        content = content.replace("\n", '')
        content = content.replace("*", "")
        content = content.strip()

        content = re.sub(r'\(.*\)', "", content)
        # content = re.sub(r'（.*）', "",content)
        return content



    def article_filter(self,article_content):
        last_index = article_content.rfind("参考资料")
        if last_index != -1:
            return article_content[:last_index]
        else:
            return article_content

    def process_item(self, item, spider):
        article_content = item.get("content")
        article_content_txt = self.pureHtml(article_content)
        article_content_txt = self.article_filter(article_content_txt)
        if (len(article_content_txt) < MIN_ARTICLE_LEN):
            raise DropItem("article content is too short. url is :\n"+item.get("url"))

        item["content"]=article_content_txt
        return item

#item 保存到mongo
class MongoPipeline(object):

    collection_name = 'article'

    def __init__(self, mongo_uri, mongo_db):
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            mongo_uri=crawler.settings.get('MONGO_URI'),
            mongo_db=crawler.settings.get('MONGO_DATABASE', 'fm')
        )

    def open_spider(self, spider):
        self.client = pymongo.MongoClient(self.mongo_uri)
        self.db = self.client[self.mongo_db]

    def close_spider(self, spider):
        self.client.close()

    def process_item(self, item, spider):
        self.db[self.collection_name].insert_one(dict(item))
        return item


#去重
class DuplicatesPipeline(object):
    collection_name = 'article'
    def __init__(self, mongo_uri, mongo_db):
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            mongo_uri=crawler.settings.get('MONGO_URI'),
            mongo_db=crawler.settings.get('MONGO_DATABASE', 'fm')
        )

    def open_spider(self, spider):
        self.client = pymongo.MongoClient(self.mongo_uri)
        self.db = self.client[self.mongo_db]

    def close_spider(self, spider):
        self.client.close()

    def process_item(self, item, spider):
        result = self.db[self.collection_name].find_one({'title':item['title']})
        if result is not None:
            raise DropItem("Duplicate item found: %s" % item.get("url"))
        else:
            return item