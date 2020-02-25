from pymongo import MongoClient
from datetime import datetime
from bson.objectid import ObjectId

class Opt(object):
    def __init__(self):
        self.connect = MongoClient('mongodb://39.108.74.74:27017/')
        self.db = self.connect['fm']
        self.article = self.db["article"]

    def setUnavailable(self,url):
        result = self.article.update_one({"url":url},{'$set': {"no_voice": True}})
        print(result.raw_result)
#单例
opt = Opt()