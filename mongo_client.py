import urllib

import mongo_credentials as mcred
import pymongo

mongo_user = urllib.parse.quote_plus(mcred.USERNAME)
mongo_pass = urllib.parse.quote_plus(mcred.PASSWORD)


def get():
    mongo_client = pymongo.MongoClient('mongodb://{}:{}@127.0.0.1:27017'.format(mongo_user, mongo_pass))
    return mongo_client
