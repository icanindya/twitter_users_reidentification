import sys
sys.path.append(r'D:\Projects\Python\AttributePrediction\credentials')

import mongo_credentials as mcred
import twitter_credentials as tcred
import urllib
import pymongo
import tweepy
import csv
import re
from datetime import datetime, timedelta
from nltk.tokenize.casual import TweetTokenizer
from nltk.corpus import stopwords

random_seed = 3613
test_percentage = 0.20

mongo_user = urllib.parse.quote_plus(mcred.USERNAME)
mongo_pass = urllib.parse.quote_plus(mcred.PASSWORD)

stopwords = set(stopwords.words('english'))

punctuation_list = {'.', ',', '?', '!', '\'', '"', ':', ';', '-', '–'}
special_list = {'`', '~', '@', '#', '$', '%', '^', '&', '+', '*', '/', '=',
                '>', '<', '(', ')', '{', '}', '[', ']', '|', '\\'}
other_sym_list = {'...', '…', '’', '..', '“', '”'}

stop_url_symbol_list = stopwords.union(punctuation_list).union(special_list).union(other_sym_list).union({'#url'})


class CustomTweetTokenizer(TweetTokenizer):

    def __init__(self, preserve_case=True, reduce_len=False, strip_handles=False, convert_urls=True, remove_stopwords=False):
        super().__init__(preserve_case=preserve_case,
                         reduce_len=reduce_len,
                         strip_handles=strip_handles)
        self.convert_urls = convert_urls
        self.remove_stopwords = remove_stopwords

    @staticmethod
    def convert_url(token):
        if token.startswith('http://') or token.startswith('https://'):
            return '#url'
        return token

    def tokenize(self, text):
        tokens = super().tokenize(text)
        if self.convert_urls:
            tokens = [self.convert_url(token) for token in tokens]
        if self.remove_stopwords:
            tokens = [token for token in tokens if token not in stopwords]
        return tokens


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


def get_twitter_user_auths():
    ''' application-user apis '''
    auths = []

    for ckey, cksec, atok, atsec in zip(tcred.consumer_keys, tcred.consumer_key_secrets,
                                        tcred.access_tokens, tcred.access_token_secrets):
        auth = tweepy.OAuthHandler(ckey, cksec)
        auth.set_access_token(atok, atsec)
        auths.append(auth)

    return auths


def get_twitter_app_apis():
    ''' application-only apis'''
    apis = []

    for ckey, cksec in zip(tcred.consumer_keys, tcred.consumer_key_secrets):
        auth = tweepy.AppAuthHandler(ckey, cksec)
        api = tweepy.API(auth)
        apis.append(api)

    return apis


def get_mongo_client():
    mongo_client = pymongo.MongoClient('mongodb://{}:{}@127.0.0.1:27017'.format(mongo_user, mongo_pass))
    return mongo_client


def get_short_race(code):

    code = int(code)

    if code == 1:
        return 'IA'
    elif code == 2:
        return 'AP'
    elif code == 3:
        return 'BL'
    elif code == 4:
        return 'HI'
    elif code == 5:
        return 'WH'
    elif code == 6:
        return 'OT'
    elif code == 7:
        return 'MU'
    elif code == 9:
        return 'UN'
    else:
        return None

def get_long_sex(x):

    if x == 'F':

        return 'Female'

    elif x == 'M':

        return 'Male'

    return 'Unknown'



def get_maif_age_label(age):
    if age <= 18:
        return '18-'
    elif 19 <= age <= 22:
        return '19-22'
    elif 23 <= age <= 33:
        return '23-33'
    elif 34 <= age <= 45:
        return '34-45'
    else:
        return '46+'

def get_my_age_label(age):
    if age <= 22:
        return '22-'
    elif 23 <= age <= 33:
        return '23-33'
    elif 34 <= age <= 45:
        return '34-45'
    elif 46 <= age <= 60:
        return '46-60'
    else:
        return '61+'

def get_generation(dob):

    try:
        yob = int(dob[-4:])

        if yob >= 1996:
            return '1996-2019'
        elif 1986 <= yob <= 1995:
            return '1986-1995'
        elif 1976 <= yob <= 1985:
            return '1976-1985'
        elif 1966 <= yob <= 1975:
            return '1966-1975'
        elif 1956 <= yob <= 1965:
            return '1956-1965'
        else:
            return '1900-1955'
    except:
        print('invalid dob: {}'.format(dob))
        return None

def get_short_party(party):

    if party == 'CPF':
        return 'CP'
    elif party == 'DEM':
        return 'DM'
    elif party == 'ECO':
        return 'EC'
    elif party == 'GRE':
        return 'GR'
    elif party == 'IND':
        return 'IN'
    elif party == 'LPF':
        return 'LP'
    elif party == 'NPA':
        return 'NP'
    elif party == 'PSL':
        return 'SL'
    elif party == 'REF':
        return 'RF'
    elif party == 'REP':
        return 'RP'
    else:
        return None


def date_difference_years(datetime1, datetime2):
    return int((datetime1 - datetime2).days // 365.2425)


def get_curr_age_label(dob):
    dob_datetime = datetime.strptime(dob + ' -0500', '%m/%d/%Y %z')
    curr_datetime = datetime.strptime('01/01/2019 -0500', '%m/%d/%Y %z')
    age = date_difference_years(curr_datetime, dob_datetime)
    return get_maif_age_label(age)


def is_link(text):
    return text.startswith('http://') or text.startswith('https://')


def is_handle(text):
    return text.startswith('@')


def set_csv_field_size_limit():
    maxInt = sys.maxsize

    while True:
        # decrease the maxInt value by factor 10
        # as long as the OverflowError occurs.

        try:
            csv.field_size_limit(maxInt)
            break
        except OverflowError:
            maxInt = int(maxInt / 10)


UPPERCASE_ALPHABET = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L',
                      'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X',
                      'Y', 'Z']

EXTENDED_ALPHABET = open(r'D:\Data\Linkage\FL\FL18\lexicons\top_unicodes.txt', 'r', encoding='utf-8').readline().split()

set_csv_field_size_limit()


def mention_or_newline(token):
    if token.startswith('@') or token in ['\r', '\n']:
        return True
    return False


def mention(token):
    if token.startswith('@'):
        return True
    return False


def stop_or_mention(token):
    if token.lower() in stopwords or token.startswith('@'):
        return True
    return False


def stop_mention_url_or_symbol(token):

    token = token.lower()

    if token in stop_url_symbol_list or token.startswith('@'):
        return True
    return False


def jaccard_similarity(list1, list2):
    if len(list1) == 0 or len(list2) == 0:
        return 0
    intersection = len(list(set(list1).intersection(list2)))
    union = (len(list1) + len(list2)) - intersection
    return float(intersection) / union




