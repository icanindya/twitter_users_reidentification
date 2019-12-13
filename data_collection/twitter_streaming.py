from tweepy import Stream
from tweepy.streaming import StreamListener
import helper
import json
import sys
import time

TWITTER_STREAM_PATH = r'D:\Data\Linkage\FL\FL18\all_tweets\stream_{}.txt'
TOP_ONEGRAMS_PATH =   r'D:\Data\Linkage\FL\FL18\ml_datasets\top_1grams.txt'


class TwitterListener(StreamListener):
    """ A listener handles tweets that are received from the stream.
    This is a basic listener that just prints received tweets to stdout.
    """

    def __init__(self):
        self.file = open(TWITTER_STREAM_PATH.format(option), 'a', encoding='utf-8')
        self.count = 0

    def on_data(self, data):
        json_obj = json.loads(data)

        if 'limit' in json_obj:
            time.sleep(1)

        elif not json_obj['retweeted'] and not json_obj['text'].startswith('RT @'):
            twitter_id = json_obj['user']['id_str']
            tweet_id = json_obj['id_str']
            tweet = json_obj['text']
            tweet = tweet.replace('\0', '') \
                .replace('\r\n', ' ') \
                .replace('\r', ' ') \
                .replace('\n', ' ') \
                .replace('\f', ' ')
            self.file.write('{}-{}, {}\n'.format(twitter_id, tweet_id, tweet))
            self.count += 1
            if self.count % 100 == 0:
                print(self.count)
                self.file.flush()

    def on_error(self, status):
        print('error:', status)


if __name__ == '__main__':

    option = 'lang'
    api_index = 1

    if len(sys.argv) > 1:
        option = sys.argv[1]
        api_index = int(sys.argv[2])

    top_1grams = []

    with open(TOP_ONEGRAMS_PATH, 'r', encoding='utf-8') as rf:
        for i, line in enumerate(rf):
            if i == 400:
                break
            top_1grams.append(line.strip())

    listener = TwitterListener()
    apis = helper.get_twitter_user_auths()

    stream = Stream(apis[api_index], listener)
    #
    if option == 'geo':
        stream.filter(locations=[-123.62, 32.94, -66.82, 47.20])
    elif option == 'lang':
        stream.filter(languages=["en"], track=top_1grams)
        # stream.filter(languages=["en"], track=["a", "the", "i", "you", "u"])
    else:
        print('invalid option')
