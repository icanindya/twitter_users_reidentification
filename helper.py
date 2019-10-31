import mongo_credentials as mcred
import twitter_credentials as tcred
import urllib
import pymongo
import tweepy
from datetime import datetime, timedelta


mongo_user = urllib.parse.quote_plus(mcred.USERNAME)
mongo_pass = urllib.parse.quote_plus(mcred.PASSWORD)


def get_twitter_user_apis():
    ''' application-user apis '''
    apis = []

    for ckey, cksec, atok, atsec in zip(tcred.consumer_keys, tcred.consumer_key_secrets,
                                        tcred.access_tokens, tcred.access_token_secrets):
        auth = tweepy.OAuthHandler(ckey, cksec)
        auth.set_access_token(atok, atsec)
        api = tweepy.API(auth)
        apis.append(api)

    return apis


def get_twitter_app_apis():
    ''' application-oonly apis'''
    apis = []

    for ckey, cksec in zip(tcred.consumer_keys, tcred.consumer_key_secrets):
        auth = tweepy.AppAuthHandler(ckey, cksec)
        api = tweepy.API(auth)
        apis.append(api)

    return apis


def get_mongo_client():
    mongo_client = pymongo.MongoClient('mongodb://{}:{}@127.0.0.1:27017'.format(mongo_user, mongo_pass))
    return mongo_client


def get_maif_age_label(age):
    if age <= 18:
        return '<=18'
    elif 19 <= age <= 22:
        return '19-22'
    elif 23 <= age <= 33:
        return '23-33'
    elif 34 <= age <= 45:
        return '34-45'
    else:
        return '>=46'


def date_difference_years(datetime1, datetime2):
    return int((datetime1 - datetime2).days // 365.2425)


def get_curr_age_label(dob):
    dob_datetime = datetime.strptime(dob + ' -0500', '%m/%d/%Y %z')
    curr_datetime = datetime.strptime('01/01/2019 -0500', '%m/%d/%Y %z')
    age = date_difference_years(curr_datetime, dob_datetime)
    return get_maif_age_label(age)


def get_race_label(race_code):
    if race_code == 1:
        return 'AI'
    elif race_code == 2:
        return 'AP'
    elif race_code == 3:
        return 'BL'
    elif race_code == 4:
        return 'HI'
    elif race_code == 5:
        return 'WH'
    elif race_code == 6:
        return 'OT'
    elif race_code == 7:
        return 'MU'
    elif race_code == 9:
        return 'UN'
    else:
        print('unknown race code: {}'.format(race_code))


def is_link(text):
    return text.startswith('http://') or text.startswith('https://')


def is_handle(text):
    return text.startswith('@')


UPPERCASE_ALPHABET = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L',
                      'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X',
                      'Y', 'Z']

EXTENDED_ALPHABET = open(r'D:\Data\Linkage\FL\FL18\lexicons\top_unicodes.txt', 'r', encoding='utf-8').readline().split()
