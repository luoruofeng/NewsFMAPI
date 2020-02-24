# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

import html2text
import pymongo
import re
import errno
import os
import json
from scrapy.exceptions import DropItem
import logging

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
                logging.warning("article content is too short. url is :\n"+item.get("url"))
                raise DropItem("article content is too short. url is :\n"+item.get("url"))
            else:
                logging.info("checked article lenth. url is :\n" + item.get("url"))
                return item
        else:
            logging.warning("article content is Null. content is :\n" + item)
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
        content = re.sub(r'图片来源.*?\s+', "", content)
        content = re.sub(r'本文来自.*?\s+', "", content)
        content = re.sub(r'本文来自.*?，', "", content)
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
            logging.warning("article content is too short. url is :\n" + item.get("url"))
            raise DropItem("article content is too short. url is :\n"+item.get("url"))

        item["content"]=article_content_txt
        logging.info("format content of article. url is :\n"+item.get("url"))
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
        logging.info("saved item to mongo: %s" % item.get("url"))
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
        logging.info("open mongo client!")

    def close_spider(self, spider):
        self.client.close()
        logging.info("close mongo client!")

    def process_item(self, item, spider):
        result = self.db[self.collection_name].find_one({'title':item['title']})
        if result is not None:
            logging.warning("Duplicate item found: \n%s" % item.get("url"))
            raise DropItem("Duplicate item found: \n%s" % item.get("url"))
        else:
            logging.info("checked item isn't duplication: \n%s" % item.get("url"))
            return item




#将item  序列化为json 发送给pipe（fifo有名管道） 另一个程序（进程）读写进程，并转化为音频
class FifoPipeline(object):
    def __init__(self, fifo_name):
        self.fifo_name = fifo_name

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            fifo_name=crawler.settings.get('FIFO_NAME',"/article_pipe")
        )

    def open_spider(self, spider):
        try:
            os.mkfifo(self.fifo_name)
            logging.info("create pipe file")
        except OSError as e:
            if (e.errno != errno.EEXIST):
                logging.warning("pipe file is already exists!")
                raise

    def close_spider(self, spider):
        pass

    def process_item(self, item, spider):
        item_str = json.dumps(dict(item),ensure_ascii=False)
        logging.info("serialize object to json string. url : \n" + item.get("url"))
        with open(self.fifo_name, "w") as f:
            f.write(item_str)

        logging.info("send to pipe. url : \n"+item.get("url"))
